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

    # controller/curve_controller.py

    def request_edit_to_curve_radius(self, idx):
        """곡선 변경 처리"""
        # 1. 현재 값 가져오기 (AppController를 통해 collection 접근)
        try:
            # collection의 radius_list에서 해당 인덱스의 값을 가져옴
            current_radius = self.app.collection.get_radius_at(idx)
        except (IndexError, AttributeError):
            current_radius = 0.0

        # 2. UI 입력 (현재 값을 초기값으로 제공)
        radius = simpledialog.askfloat(
            "곡선반경 변경",
            f"새 곡선 반경 R (m):",
            parent=self.app,
            minvalue=0.1,
            initialvalue=current_radius  # 사용자가 기존 값을 확인하며 수정 가능
        )

        if radius is None: return

        # 3. 비즈니스 신호 발생
        try:
            self.events.emit('curve_updated', idx, radius)
            self.events.emit('curve_changed_finish')
            self.app.set_status(f"PI {idx} 곡선 변경 완료: R={radius}")
        except Exception as e:
            messagebox.showerror("곡선 변경 오류", str(e))