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
        self.dragging_index        = None
        self.dragging_midpoint_seg = None
        self._overlay_artists = []
        self.ploter = None
        self._configure_window()
        self.canvas_frams = None
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
        """Matplotlib 이벤트를 물리 좌표(숫자)로 변환"""
        if event.xdata is None or event.ydata is None:
            return None

        x, y = event.xdata, event.ydata

        # 좌표계 변환은 UI가 지도 모드 상태를 알고 있으므로 여기서 처리
        if self.view_map_mode.get():
            try:
                from pyproj import Transformer
                t = Transformer.from_crs("EPSG:3857", "EPSG:5186", always_xy=True)
                x, y = t.transform(x, y)
            except Exception:
                pass  # 변환 실패 시 원본 좌표 사용

        # Point2d 객체로 만드는 대신, 순수 데이터(Tuple)를 컨트롤러에 전달
        return x, y

    # ══════════════════════════════════
    # 이벤트 핸들러 (원본 로직 유지)
    # ══════════════════════════════════
    def add_pi_click(self, event):
        if not self.add_pi_mode.get():
            return
        coord = self._event_to_xy(event)
        if coord is None:
            return
        self.controller.pi_ctrl.request_add_pi(coord)

    def remove_pi(self):
        idx = self.pi_index_var.get()
        self.controller.pi_ctrl.request_remove_pi(idx)

    def remove_curve(self):
        idx = self.pi_index_var.get()
        self.controller.curve_ctrl.request_remove_curve(idx)

    def reset_to_initial(self):
        self.controller.request_reset_to_initial()

    def add_curve_ui(self):
        idx = self.pi_index_var.get()
        self.controller.curve_ctrl.request_add_curve(idx)

    def update_radius_ui(self):
        idx = self.pi_index_var.get()
        self.controller.curve_ctrl.request_edit_to_curve_radius(idx)

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
            p = self._event_to_xy(event)
            if p is None:
                return
            self.controller.pi_ctrl.request_edit_pi(p, self.dragging_index)

        elif self.dragging_midpoint_seg is not None:
            p = self._event_to_xy(event)
            if p is None:
                return

            self.controller.mid_ctrl.request_edit_mid_point(self.dragging_midpoint_seg, p)

    def on_release(self, event):
        if self.dragging_index is None and self.dragging_midpoint_seg is None:
            return
        p = self._event_to_xy(event)
        if p is None:
            return
        if self.dragging_index is not None:
            self.controller.pi_ctrl.request_edit_pi(p, self.dragging_index)
        else:
            self.controller.mid_ctrl.request_edit_mid_point(self.dragging_midpoint_seg, p)
        self.dragging_index = None
        self.dragging_midpoint_seg = None

    def save_to_json(self):
        self.controller.file_ctrl.request_save()
    def load_from_json(self):
        self.controller.file_ctrl.request_load()

    def setup_plotter(self, plotter_class, events):
        """외부에서 주입된 플로터 클래스를 캔버스 프레임에 장착"""
        self.ploter = plotter_class(
            master=self.canvas_frams,  # 빌더가 만든 빈 자리
            events=events,
            collection=self.collection
        )

        # 이벤트 연결 (이건 UI 영역이므로 유지)
        self.ploter.canvas.mpl_connect('pick_event', self.on_pick)
        self.ploter.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.ploter.canvas.mpl_connect('button_release_event', self.on_release)
        self.ploter.canvas.mpl_connect('button_press_event', self.add_pi_click)