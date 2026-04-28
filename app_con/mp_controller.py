# controller/curve_controller.py
from tkinter import simpledialog, messagebox

from AutoCAD.point2d import Point2d


class MidPointController:
    """MidPoint 컨트롤러"""
    def __init__(self, app, event_controller):
        self.app = app
        self.events = event_controller

    def request_edit_mid_point(self, seg, point):
        """MidPoint 편집 요청 처리"""
        # 2. 비즈니스 신호 발생
        try:
            coord = self._to_point(point)
            self.events.emit('midpoint_dragged', seg, coord)
            self.events.emit('midpoint_dragged_finish')

        except Exception as e:
            messagebox.showerror("드래그 오류", str(e))

    def _to_point(self, coord):
        """튜플을 도메인 객체로 변환하는 헬퍼 메서드"""
        if isinstance(coord, Point2d):
            return coord
        return Point2d(coord[0], coord[1])