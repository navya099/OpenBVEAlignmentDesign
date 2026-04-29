# map_bridge.py
import time

from AutoCAD.point2d import Point2d
from coordinate_utils import convert_coordinates


class MapBridge:
    def __init__(self):
        self._controller = None
        self._window = None
        self.dragging_index = None
        self._last_drag_time = 0          # 스로틀링용
        self._DRAG_INTERVAL = 0.05        # 50ms마다 1회만 처리 (초당 20회)

    def init_with_app(self, controller, window):
        self._controller = controller
        self._window = window

    def on_map_ready(self):
        print("지도가 준비되었습니다!")

    def on_pi_drag_start(self, index):
        def task():
            self.dragging_index = index
            self._controller.pi_ctrl.request_drag_start()
        self._controller.app.after(0, task)

    # map_bridge.py
    def on_pi_dragging(self, index, lat, lng):
        # ✅ dragging_index가 None이면 dragend 이후 밀려온 호출 → 무시
        print(f"Dragging: {index}")
        if self.dragging_index is None:
            return

        # ✅ 현재 드래그 중인 마커의 이벤트인지 확인
        if self.dragging_index != index:
            return

        now = time.time()
        if now - self._last_drag_time < self._DRAG_INTERVAL:
            return
        self._last_drag_time = now

        x, y = self._to_5186(lat, lng)

        def task():
            self._controller.app.set_coord(x, y)
            self._controller.pi_ctrl.request_drag_pi((x, y), index)

        self._controller.app.after(0, task)

    def on_pi_drag_end(self, index, lat, lng):
        # 1. 즉시 드래그 상태 해제 (가장 중요)
        self.dragging_index = None

        x, y = self._to_5186(lat, lng)

        def task():
            # 2. UI 컨트롤러 상태 업데이트
            self._controller.app.set_coord(x, y)

            # 3. 데이터 업데이트 및 재렌더링
            start = time.perf_counter()
            self._controller.pi_ctrl.request_drag_pi((x, y), index)

            # 4. JS 쪽에 최종 위치 확정 알림 (updateAfterDrag 호출 유도)
            # 이 시점에 pi_ctrl이 renderAll이나 updateAfterDrag를 호출하게 되어있어야 합니다.
            self._controller.pi_ctrl.request_drag_finish()

            elapsed = (time.perf_counter() - start) * 1000
            print(f"[성능] update_pi_total: {elapsed:.1f}ms")

        # Tkinter 등의 메인 루프에서 순차 실행되도록 예약
        self._controller.app.after(0, task)

    def on_map_click(self, lat, lng):
        x, y = self._to_5186(lat, lng)

        def task():
            if self._controller.app.add_pi_mode.get():
                self._controller.pi_ctrl.request_add_pi((x, y))
        self._controller.app.after(0, task)

    def _to_5186(self, lat, lng):
        """위경도(4326) → EPSG:5186 변환. 인자 순서 명확화"""
        return convert_coordinates([lng, lat], 4326, 5186)

    def on_mid_drag_start(self, index):
        # 1. 드래그 유형을 구분하거나 전용 변수를 사용하는 것이 안전합니다.
        # pi_dragging과 겹치지 않게 하기 위함입니다.
        self.dragging_type = 'midpoint'
        self.dragging_index = index

        try:
            target_seg = self._controller.collection.segment_list[index]
        except IndexError:
            return

        def task():
            # 드래그 시작 시점의 초기화 로직 (필요시)
            if hasattr(self._controller.mid_ctrl, 'request_drag_start'):
                self._controller.mid_ctrl.request_drag_start(target_seg)

        self._controller.app.after(0, task)

    def on_mid_dragging(self, index, lat, lng):
        # 2. 유효성 검사 강화: 현재 드래그 중인 것이 midpoint가 맞는지 확인
        if self.dragging_index is None or getattr(self, 'dragging_type', None) != 'midpoint':
            return
        if self.dragging_index != index:
            return

        # 3. 스로틀링 (앞서 정의한 _DRAG_INTERVAL 사용)
        now = time.time()
        if now - self._last_drag_time < self._DRAG_INTERVAL:
            return
        self._last_drag_time = now

        x, y = self._to_5186(lat, lng)

        try:
            target_seg = self._controller.collection.segment_list[index]
        except IndexError:
            return

        def task():
            # 드래그 도중에는 좌표 표시 업데이트와 가벼운 선형 업데이트만 수행
            self._controller.app.set_coord(x, y)
            self._controller.mid_ctrl.request_edit_mid_point(target_seg, (x, y))

        self._controller.app.after(0, task)

    def on_mid_drag_end(self, index, lat, lng):
        # 4. 즉시 상태 초기화 (매우 중요)
        self.dragging_index = None
        self.dragging_type = None

        x, y = self._to_5186(lat, lng)

        try:
            target_seg = self._controller.collection.segment_list[index]
        except IndexError:
            return

        def task():
            self._controller.app.set_coord(x, y)
            start = time.perf_counter()

            # 최종 위치로 데이터 확정 및 DB/메모리 갱신
            self._controller.mid_ctrl.request_edit_mid_point(target_seg, (x, y))

            # 최종 렌더링 호출 (점선을 실선으로 복구하거나 마커 재배치)
            if hasattr(self._controller.mid_ctrl, 'request_drag_mid_point_finish'):
                self._controller.mid_ctrl.request_drag_mid_point_finish()
            else:
                # 공용 종료 함수가 있다면 그것을 사용
                self._controller.pi_ctrl.request_drag_finish()

            elapsed = (time.perf_counter() - start) * 1000
            print(f"[성능] Midpoint Drag End Total: {elapsed:.1f}ms")

        self._controller.app.after(0, task)