# controller/curve_controller.py
from tkinter import simpledialog, messagebox

from AutoCAD.point2d import Point2d


class PIController:
    """PI 컨트롤러"""
    def __init__(self, app, event_controller):
        self.app = app
        self.events = event_controller

    def request_add_pi(self, coord):
        """pi 추가 요청 처리"""
        # 2. 비즈니스 신호 발생
        try:
            coord = self._to_point(coord)
            self.events.emit('pi_added', coord)
            self.events.emit('pi_added_finish')
            self.app.set_status(f"PI 추가 완료")
        except Exception as e:
            messagebox.showerror("PI 추가 오류", str(e))

    def request_edit_pi(self, idx):
        """문자열 입력을 통한 정확한 PI 좌표 편집"""
        # 1. 현재 값 가져오기
        try:
            curr = self.app.collection.coord_list[idx]
            initial_str = f"{curr.x:.2f}, {curr.y:.2f}"
        except:
            initial_str = ""

        # 2. 사용자 입력 (문자열로 받기)
        raw_input = simpledialog.askstring(
            "PI 좌표 정밀 편집",
            f"PI {idx}의 새 좌표 (X, Y):",
            parent=self.app,
            initialvalue=initial_str
        )

        if not raw_input: return

        try:
            # 3. 파싱 및 객체 변환
            parts = raw_input.replace(',', ' ').split()
            if len(parts) != 2:
                raise ValueError("X와 Y 두 좌표를 입력해야 합니다.")

            x, y = map(float, parts)
            point = self._to_point((x, y))  # 튜플을 Point2d로 변환

            # 4. 비즈니스 신호 발생
            self.events.emit('pi_dragged', point, idx)
            self.events.emit('pi_dragged_finish')

            self.app.set_status(f"PI {idx} 좌표 수동 수정 완료: ({x}, {y})")

        except ValueError as e:
            messagebox.showerror("입력 오류", "좌표 형식이 올바르지 않습니다.\n예: 1250.5, 3300.2")
        except Exception as e:
            messagebox.showerror("PI 편집 오류", str(e))

    def request_remove_pi(self, idx):
        """pi 삭제 요청 처리"""
        if not messagebox.askyesno("삭제 확인", f"PI {idx}를 삭제할까요?"):
            return

        try:
            self.events.emit('pi_removed', idx)
            self.events.emit('pi_removed_finish')
            self.app.set_status(f"PI {idx} 삭제 완료")
        except Exception as e:
            messagebox.showerror("PI 삭제 오류", str(e))

    def request_reset_to_initial(self):
        if not messagebox.askyesno("초기화 확인",
                                   "모든 PI와 곡선을 초기화하시겠습니까?"):
            return
        try:
            self.events.emit('reset_to_initial')
            self.events.emit('reset_to_initial_finish')
            self.app.set_status("초기화 완료")
        except Exception as e:
            messagebox.showerror("초기화 오류", str(e))

    def request_drag_pi(self, coord, idx):
        """PI드래그 요청 처리"""
        try:
            coord = self._to_point(coord)
            self.events.emit('pi_dragged', coord, idx)
            self.events.emit('pi_dragged_finish')
            self.app.set_status("초기화 완료")
        except Exception as e:
            messagebox.showerror("초기화 오류", str(e))

    def _to_point(self, coord):
        """튜플을 도메인 객체로 변환하는 헬퍼 메서드"""
        if isinstance(coord, Point2d):
            return coord
        return Point2d(coord[0], coord[1])