# controller/curve_controller.py
from tkinter import simpledialog, messagebox


class ViewController:
    """뷰(맵) 컨트롤러"""
    def __init__(self, app, event_controller):
        self.app = app
        self.events = event_controller

    def request_map_mode_change(self, mode):
        """지도 모드 체인지 요청 처리"""
        pass

    def request_update_map(self, mode):
        """지도 업데이트 요청 처리"""
        pass