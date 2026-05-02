"""
segment_visualizer_ui.py
─────────────────────────────────────────────────
OPENBVE 선형설계 프로그램 - CAD 산업용 리본 툴바 리디자인
스타일: 산업용 CAD / 리본 툴바 / 기능별 그룹화 / 아이콘
─────────────────────────────────────────────────
"""
import tkinter as tk
from tkinter import ttk

from utils.coordinate_utils import convert_coordinates
from myalignment.segment.segment_helper import SegmentHelper
from ui.build import UIBuilder
from ui.design_tokens import C

# ══════════════════════════════════════════════════
# 메인 윈도우
# ══════════════════════════════════════════════════
class SegmentVisualizer(tk.Tk):
    """CAD 산업용 리본 툴바 스타일 선형설계 프로그램"""

    def __init__(self, controller, collection):
        super().__init__()
        self.collection            = collection
        self.controller      = controller #appcontroller

        # ── 상태 변수는 app이 선언 (UIBuilder가 참조)
        self.pi_index_var = tk.IntVar(value=1)
        self.add_pi_mode = tk.BooleanVar(value=False)
        self.view_map_mode = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="준비")
        self.mode_var = tk.StringVar(value="● 일반")
        self.coord_var = tk.StringVar(value="X: ─────  Y: ─────")
        self.pi_disp_var = tk.StringVar(value="PI: 1")
        self._overlay_artists = []
        self.ploter = None
        self._configure_window()
        self.canvas_frams = None
        # ── UI 조립은 builder에 위임
        UIBuilder(self).build()
        self._bind_traces()

    def _configure_window(self):
        self.title("OPENBVE 선형설계 프로그램")
        self.geometry("1440x400")
        self.minsize(1100, 400)

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

    # ══════════════════════════════════
    # 이벤트 핸들러 (원본 로직 유지)
    # ══════════════════════════════════
    def add_pi_click(self, x,y):
        if not self.add_pi_mode.get():
            return
        coord = (x, y)
        self.controller.pi_ctrl.request_add_pi(coord)

    def remove_pi(self):
        idx = self.pi_index_var.get()
        self.controller.pi_ctrl.request_remove_pi(idx)

    def edit_pi(self):
        idx = self.pi_index_var.get()
        self.controller.pi_ctrl.request_edit_pi(idx)

    def remove_curve(self):
        idx = self.pi_index_var.get()
        self.controller.curve_ctrl.request_remove_curve(idx)

    def reset_to_initial(self):
        self.controller.pi_ctrl.request_reset_to_initial()

    def add_curve_ui(self):
        idx = self.pi_index_var.get()
        self.controller.curve_ctrl.request_add_curve(idx)

    def update_radius_ui(self):
        idx = self.pi_index_var.get()
        self.controller.curve_ctrl.request_edit_to_curve_radius(idx)

    def save_to_json(self):
        self.controller.file_ctrl.request_save()
    def load_from_json(self):
        self.controller.file_ctrl.request_load()
    def export_bve(self):
        self.controller.file_ctrl.request_export_bve()

    def on_change_map_mode(self):
        """맵 모드 변경 요청"""
        self.controller.view_ctrl.request_map_mode_change(self.view_map_mode.get())

    def on_update_map(self):
        """맵 업데이트 요청"""
        self.controller.view_ctrl.request_update_map(self.view_map_mode.get())