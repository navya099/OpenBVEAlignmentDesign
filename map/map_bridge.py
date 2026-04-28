# map_bridge.py
from coordinate_utils import convert_coordinates
from data.segment.segment_helper import SegmentHelper


class MapBridge:
    """webview와 파이썬과의 연결을 위한 브릿지
    코드 흐름: webview이벤트(웹, js) 발생-> webviewapi를 통해
    MapBridge 클래스의 메서드가 호출됨-> 내부 컨트롤러(로컬, 파이썬)으로 전달
    ->연산 수행
    """
    def __init__(self):
        self._controller = None
        self._window = None
        self.dragging_index = None  # UI 속성에서 여기로 이사 완료!
    def init_with_app(self, controller, window):
        """pywebview의 스캔이 끝난 후 호출하여 참조 연결"""
        self._controller = controller
        self._window = window

    def on_map_ready(self):
        """지도가 로딩 완료되면 호출됨"""
        print("지도가 준비되었습니다!")

    def on_pi_drag_start(self, index):
        """드래그 시작 시점 (기존 on_pick 역할)"""

        def task():
            self._controller.app.dragging_index = index
            self._controller.pi_ctrl.request_drag_start()

        self._controller.app.after(0, task)

    def on_pi_dragging(self, index, lat, lng):
        """드래그 중 (기존 on_drag 역할)"""
        # 1. 좌표 변환 (위경도 -> EPSG:5186)
        x, y = self.convert_coordinates_system(lat, lng)

        def task():
            # UI 하단 좌표 표시 업데이트
            self._controller.app.set_coord(x, y)
            # 컨트롤러에 드래그 좌표 전달
            self._controller.pi_ctrl.request_drag_pi((x, y), index)

        self._controller.app.after(0, task)

    def on_pi_drag_end(self, index, lat, lng):
        """드래그 종료 (기존 on_release 역할)"""
        x, y = self.convert_coordinates_system(lat, lng)

        def task():
            self._controller.pi_ctrl.request_drag_pi((x, y), index)
            self._controller.pi_ctrl.request_drag_finish()
            self.dragging_index = None

        self._controller.app.after(0, task)

    def on_map_click(self, lat, lng):
        """지도 빈 곳 클릭 시 PI 추가 (기존 add_pi_click 역할)"""
        x, y = self.convert_coordinates_system(lat, lng)

        def task():
            if self._controller.app.add_pi_mode.get():
                self._controller.pi_ctrl.request_add_pi((x, y))

        self._controller.app.after(0, task)


    def convert_coordinates_system(self, lng, lat):
        return convert_coordinates([lat, lng], 4326, 5186)