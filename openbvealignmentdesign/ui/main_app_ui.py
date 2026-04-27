"""
segment_visualizer_ui.py
─────────────────────────────────────────────────
OPENBVE 선형설계 프로그램 - CAD 산업용 리본 툴바 리디자인
스타일: 산업용 CAD / 리본 툴바 / 기능별 그룹화 / 아이콘
─────────────────────────────────────────────────
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from ui.build import UIBuilder
from ui.design_tokens import C

# ══════════════════════════════════════════════════
# 메인 윈도우
# ══════════════════════════════════════════════════
class SegmentVisualizer(tk.Tk):
    """CAD 산업용 리본 툴바 스타일 선형설계 프로그램"""

    def __init__(self, event_controller, collection):
        super().__init__()
        self.collection            = collection
        self.event_controller      = event_controller

        # ── 상태 변수는 app이 선언 (UIBuilder가 참조)
        self.pi_index_var = tk.IntVar(value=1)
        self.add_pi_mode = tk.BooleanVar(value=False)
        self.view_map_mode = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="준비")
        self.mode_var = tk.StringVar(value="● 일반")
        self.coord_var = tk.StringVar(value="X: ─────  Y: ─────")
        self.pi_disp_var = tk.StringVar(value="PI: 1")
        self.dragging_index        = None
        self.dragging_midpoint_seg = None
        self._overlay_artists = []

        self._configure_window()

        # ── UI 조립은 builder에 위임
        UIBuilder(self).build()

        self._bind_traces()

    def _configure_window(self):
        self.title("OPENBVE 선형설계 프로그램")
        self.geometry("1440x860")
        self.minsize(1100, 680)

        self.configure(bg=C["chrome"])
        self._apply_ttk_style()

    # ── TTK 스타일 ──────────────────────
    def _apply_ttk_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=C["toolbar_bg"],
                    foreground=C["text_hi"],
                    fieldbackground=C["btn_normal"],
                    bordercolor=C["border_soft"])

    # ── 모드 추적 ───────────────────────
    def _bind_traces(self):
        # 상태 변수 변경 시 UI 갱신 (로직은 app이 관리)
        self.pi_index_var.trace_add(
            "write",
            lambda *_: self.pi_disp_var.set(f"PI: {self.pi_index_var.get()}")
        )
        self.add_pi_mode.trace_add("write",  self._update_mode_label)
        self.view_map_mode.trace_add("write", self._update_mode_label)

    def _update_mode_label(self, *_):
        if self.add_pi_mode.get():
            self.mode_var.set("● PI 추가 모드")
        elif self.view_map_mode.get():
            self.mode_var.set("● 지도 보기 모드")
        else:
            self.mode_var.set("● 일반")

    # ══════════════════════════════════
    # 헬퍼
    # ══════════════════════════════════
    def set_status(self, msg: str):
        self.status_var.set(msg)

    def set_coord(self, x: float, y: float):
        self.coord_var.set(f"X: {x:>12,.2f}  Y: {y:>12,.2f}")

    def _event_to_xy(self, event):
        if event.xdata is None or event.ydata is None:
            return None
        if self.view_map_mode.get():
            try:
                from pyproj import Transformer
                t = Transformer.from_crs("EPSG:3857", "EPSG:5186", always_xy=True)
                x, y = t.transform(event.xdata, event.ydata)
            except Exception:
                x, y = event.xdata, event.ydata
        else:
            x, y = event.xdata, event.ydata
        try:
            from AutoCAD.point2d import Point2d
            return Point2d(x, y)
        except ImportError:
            return (x, y)

    # ══════════════════════════════════
    # 이벤트 핸들러 (원본 로직 유지)
    # ══════════════════════════════════
    def add_pi_click(self, event):
        if not self.add_pi_mode.get():
            return
        coord = self._event_to_xy(event)
        if coord is None:
            return
        try:
            self.event_controller.emit('pi_added', coord)
            self.event_controller.emit('pi_added_finish')
            self.set_status("PI 추가 완료")
        except Exception as e:
            messagebox.showerror("PI 추가 오류", str(e))

    def remove_pi(self):
        idx = self.pi_index_var.get()
        try:
            self.event_controller.emit('pi_removed', idx)
            self.event_controller.emit('pi_removed_finish')
            self.set_status(f"PI {idx} 삭제 완료")
        except Exception as e:
            messagebox.showerror("PI 삭제 오류", str(e))

    def remove_curve(self):
        idx = self.pi_index_var.get()
        try:
            self.event_controller.emit('curve_removed', idx)
            self.event_controller.emit('curve_removed_finish')
            self.set_status(f"PI {idx} 곡선 삭제 완료")
        except Exception as e:
            messagebox.showerror("곡선 삭제 오류", str(e))

    def reset_to_initial(self):
        if not messagebox.askyesno("초기화 확인",
                                   "모든 PI와 곡선을 초기화하시겠습니까?"):
            return
        try:
            self.event_controller.emit('reset_to_initial')
            self.event_controller.emit('reset_to_initial_finish')
            self.set_status("초기화 완료")
        except Exception as e:
            messagebox.showerror("초기화 오류", str(e))

    def add_curve_ui(self):
        idx = self.pi_index_var.get()
        radius = simpledialog.askfloat("곡선 추가",
                                       f"PI {idx}  곡선 반경 R (m):",
                                       parent=self, minvalue=0.1)
        if not radius:
            return
        try:
            self.event_controller.emit('curve_added', idx, radius)
            self.event_controller.emit('curve_added_finish')
            self.set_status(f"PI {idx}  곡선 추가: R = {radius:.1f} m")
            messagebox.showinfo("완료", f"PI {idx}  →  R = {radius:.2f} m  추가 완료")
        except Exception as e:
            messagebox.showerror("곡선 추가 오류", str(e))

    def update_radius_ui(self):
        idx = self.pi_index_var.get()
        radius = simpledialog.askfloat("곡선 변경",
                                       f"PI {idx}  새 곡선 반경 R (m):",
                                       parent=self, minvalue=0.1)
        if not radius:
            return
        try:
            self.event_controller.emit('curve_updated', idx, radius)
            self.event_controller.emit('curve_changed_finish')
            self.set_status(f"PI {idx}  곡선 변경: R = {radius:.1f} m")
            messagebox.showinfo("완료", f"PI {idx}  →  R = {radius:.2f} m  변경 완료")
        except Exception as e:
            messagebox.showerror("곡선 변경 오류", str(e))

    def on_pick(self, event):
        if not hasattr(self, 'ploter'):
            return
        if event.artist == self.ploter.pi_scatter:
            self.dragging_index = event.ind[0]
            self.dragging_midpoint_seg = None
            return
        for scatter, seg in self.ploter.mid_scatters:
            if event.artist == scatter:
                self.dragging_midpoint_seg = seg
                self.dragging_index = None
                return

    def on_drag(self, event):
        if event.xdata and event.ydata:
            self.set_coord(event.xdata, event.ydata)
        if self.dragging_index is not None:
            self._drag_pi(event)
        elif self.dragging_midpoint_seg is not None:
            self._drag_mid_point(event)

    def _drag_pi(self, event):
        p = self._event_to_xy(event)
        if p is None:
            return
        try:
            self.event_controller.emit('pi_dragged', p, self.dragging_index)
            self.event_controller.emit('pi_dragged_finish')
        except Exception as e:
            messagebox.showerror("드래그 오류", str(e))

    def _drag_mid_point(self, event):
        p = self._event_to_xy(event)
        if p is None:
            return
        try:
            self.event_controller.emit('midpoint_dragged',
                                       self.dragging_midpoint_seg, p)
            self.event_controller.emit('midpoint_dragged_finish')
        except Exception as e:
            messagebox.showerror("드래그 오류", str(e))

    def on_release(self, event):
        if self.dragging_index is None and self.dragging_midpoint_seg is None:
            return
        p = self._event_to_xy(event)
        if p is None:
            return
        try:
            if self.dragging_index is not None:
                self.event_controller.emit('pi_dragged', p, self.dragging_index)
                self.event_controller.emit('pi_dragged_finish')
                self.set_status(f"PI {self.dragging_index} 이동 완료")
            else:
                self.event_controller.emit('midpoint_dragged',
                                           self.dragging_midpoint_seg, p)
                self.event_controller.emit('midpoint_dragged_finish')
                self.set_status("중간점 이동 완료")
        except Exception as e:
            messagebox.showerror("업데이트 실패", str(e))
        self.dragging_index = None
        self.dragging_midpoint_seg = None

    def save_to_json(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")])
        if not path:
            return
        try:
            self.event_controller.emit('save_to_json', path)
            self.set_status(f"저장 완료: {path}")
            messagebox.showinfo("저장 완료", f"저장:\n{path}")
        except Exception as e:
            messagebox.showerror("저장 실패", str(e))

    def load_from_json(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")])
        if not path:
            return
        try:
            self.event_controller.emit('load_from_json', path)
            self.event_controller.emit('load_from_json_finish')
            self.set_status(f"로드 완료: {path}")
            messagebox.showinfo("로드 완료", f"로드:\n{path}")
        except Exception as e:
            messagebox.showerror("로드 실패", str(e))
