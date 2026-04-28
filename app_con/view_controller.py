# controller/curve_controller.py
from tkinter import simpledialog, messagebox


class ViewController:
    """뷰(맵) 컨트롤러"""
    def __init__(self, app, event_controller):
        self.app = app
        self.events = event_controller

    def request_map_mode_change(self, mode):
        """지도 모드 체인지 요청 처리"""
        try:
            self.events.emit('map_view_mode_changed')
            self.events.emit('map_view_mode_changed_finish', view_map_mode=mode)
            self.app.set_status("지도 모드 변경 완료")
        except Exception as e:
            messagebox.showerror("지도 보기 오류", str(e))

    def request_update_map(self, mode):
        """지도 업데이트 요청 처리"""
        if not mode:
            messagebox.showinfo("안내", "지도 보기 모드를 먼저 켜세요.")
            return
        try:

            self.events.emit('map_updated')
            self.events.emit('map_updated_finish', view_map_mode=mode)
            self.app.set_status("지도 업데이트 완료")
        except Exception as e:
            messagebox.showerror("지도 업데이트 오류", str(e))