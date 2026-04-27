# controller/curve_controller.py
from tkinter import simpledialog, messagebox


class CurveController:
    """곡선 컨트롤러"""
    def __init__(self, app, event_controller):
        self.app = app
        self.events = event_controller

    def request_add_curve(self, idx):
        """곡선 추가 처리"""
        # 1. UI 입력 (사용자 상호작용)
        radius = simpledialog.askfloat("곡선 추가", f"PI {idx} 곡선 반경 R (m):",
                                       parent=self.app, minvalue=0.1)
        if radius is None: return

        # 2. 비즈니스 신호 발생
        try:
            self.events.emit('curve_added', idx, radius)
            self.events.emit('curve_added_finish')
            self.app.set_status(f"PI {idx} 곡선 추가 완료: R={radius}")
        except Exception as e:
            messagebox.showerror("곡선 추가 오류", str(e))

    def request_remove_curve(self, idx):
        if not messagebox.askyesno("삭제 확인", f"PI {idx}의 곡선을 삭제할까요?"):
            return

        try:
            self.events.emit('curve_removed', idx)
            self.events.emit('curve_removed_finish')
            self.app.set_status(f"PI {idx} 곡선 삭제 완료")
        except Exception as e:
            messagebox.showerror("곡선 삭제 오류", str(e))