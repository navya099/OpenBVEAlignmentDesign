"""
segment_visualizer_ui.py
─────────────────────────────────────────────────
OPENBVE 선형설계 프로그램 - CAD 산업용 리본 툴바 리디자인
스타일: 산업용 CAD / 리본 툴바 / 기능별 그룹화 / 아이콘
─────────────────────────────────────────────────
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

# ══════════════════════════════════════════════════
# 디자인 토큰
# ══════════════════════════════════════════════════
C = {
    # 배경 계층
    "chrome":       "#1c1e24",
    "toolbar_bg":   "#23262e",
    "group_bg":     "#2a2d38",
    "canvas_bg":    "#12141a",
    "statusbar":    "#191b21",

    # 구분선
    "border_hard":  "#111318",
    "border_soft":  "#3a3f52",
    "shadow":       "#0a0b0f",

    # 버튼 상태
    "btn_normal":   "#2e3240",
    "btn_hover":    "#3b4056",
    "btn_active":   "#454d6a",
    "btn_pressed":  "#1e2130",

    # 강조 색
    "accent":       "#4d9bff",
    "accent_dim":   "#1e3a66",
    "green":        "#3ecf8e",
    "green_dim":    "#1a4d35",
    "red":          "#f05a6e",
    "red_dim":      "#5c1e28",
    "amber":        "#f5b942",
    "teal":         "#2dd4bf",

    # 텍스트
    "text_hi":      "#e4e8f5",
    "text_md":      "#9ba3bf",
    "text_lo":      "#4a5070",
}

FONT_UI   = ("맑은 고딕", 8)
FONT_UI_B = ("맑은 고딕", 8, "bold")
FONT_GRP  = ("맑은 고딕", 7, "bold")
FONT_MONO = ("Consolas",  8)
FONT_COORD= ("Consolas",  9)
FONT_TITL = ("맑은 고딕", 9, "bold")


# ══════════════════════════════════════════════════
# 유틸: 툴팁
# ══════════════════════════════════════════════════
class Tooltip:
    def __init__(self, widget, text):
        self.widget, self.text, self._win = widget, text, None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _show(self, _=None):
        if self._win:
            return
        wx = self.widget.winfo_rootx()
        wy = self.widget.winfo_rooty() + self.widget.winfo_height() + 2
        self._win = w = tk.Toplevel(self.widget)
        w.wm_overrideredirect(True)
        w.wm_geometry(f"+{wx}+{wy}")
        w.configure(bg=C["border_soft"])
        inner = tk.Frame(w, bg=C["group_bg"], padx=7, pady=3)
        inner.pack(padx=1, pady=1)
        tk.Label(inner, text=self.text, font=FONT_MONO,
                 fg=C["text_md"], bg=C["group_bg"]).pack()

    def _hide(self, _=None):
        if self._win:
            self._win.destroy()
            self._win = None


# ══════════════════════════════════════════════════
# CAD 툴바 버튼 (아이콘 위 + 레이블 아래)
# ══════════════════════════════════════════════════
class CadButton(tk.Frame):
    def __init__(self, master, icon, label, command=None,
                 accent=None, width=54, height=50, **kw):
        super().__init__(master, bg=C["btn_normal"],
                         highlightthickness=1,
                         highlightbackground=C["border_hard"],
                         width=width, height=height, **kw)
        self.pack_propagate(False)
        self._cmd  = command
        self._base = C["btn_normal"]
        self._acc  = accent or C["text_hi"]

        self._ico = tk.Label(self, text=icon,
                             font=("Segoe UI Emoji", 13),
                             fg=self._acc, bg=self._base)
        self._ico.pack(expand=True, pady=(4, 0))

        self._lbl = tk.Label(self, text=label, font=FONT_GRP,
                             fg=C["text_md"], bg=self._base)
        self._lbl.pack(pady=(0, 3))

        for w in (self, self._ico, self._lbl):
            w.bind("<Enter>",             self._enter)
            w.bind("<Leave>",             self._leave)
            w.bind("<Button-1>",          self._press)
            w.bind("<ButtonRelease-1>",   self._release)
        self.config(cursor="hand2")

    def _set_bg(self, bg):
        self.config(bg=bg)
        self._ico.config(bg=bg)
        self._lbl.config(bg=bg)

    def _enter(self, _=None):   self._set_bg(C["btn_hover"])
    def _leave(self, _=None):   self._set_bg(self._base)
    def _press(self, _=None):   self._set_bg(C["btn_pressed"])
    def _release(self, _=None):
        self._set_bg(C["btn_hover"])
        if self._cmd:
            self._cmd()


# ══════════════════════════════════════════════════
# CAD 토글 버튼 (ON 상태 강조)
# ══════════════════════════════════════════════════
class CadToggle(tk.Frame):
    def __init__(self, master, icon, label, variable,
                 command=None, width=60, height=50, **kw):
        super().__init__(master, bg=C["btn_normal"],
                         highlightthickness=1,
                         highlightbackground=C["border_hard"],
                         width=width, height=height, **kw)
        self.pack_propagate(False)
        self._var = variable
        self._cmd = command

        self._ico = tk.Label(self, text=icon,
                             font=("Segoe UI Emoji", 13),
                             fg=C["text_hi"], bg=C["btn_normal"])
        self._ico.pack(expand=True, pady=(4, 0))

        self._lbl = tk.Label(self, text=label, font=FONT_GRP,
                             fg=C["text_md"], bg=C["btn_normal"])
        self._lbl.pack(pady=(0, 3))

        for w in (self, self._ico, self._lbl):
            w.bind("<Button-1>", self._toggle)
        self.config(cursor="hand2")

        variable.trace_add("write", lambda *_: self._refresh())
        self._refresh()

    def _toggle(self, _=None):
        self._var.set(not self._var.get())
        if self._cmd:
            self._cmd()

    def _refresh(self):
        on  = self._var.get()
        bg  = C["accent_dim"] if on else C["btn_normal"]
        ico = C["accent"]     if on else C["text_hi"]
        txt = C["text_hi"]    if on else C["text_md"]
        hl  = C["accent"]     if on else C["border_hard"]
        self.config(bg=bg, highlightbackground=hl)
        self._ico.config(bg=bg, fg=ico)
        self._lbl.config(bg=bg, fg=txt)


# ══════════════════════════════════════════════════
# 툴바 그룹 컨테이너
# ══════════════════════════════════════════════════
class ToolGroup(tk.Frame):
    """버튼 묶음 + 하단 그룹 이름"""
    def __init__(self, master, label, **kw):
        super().__init__(master, bg=C["toolbar_bg"], **kw)

        self.btn_row = tk.Frame(self, bg=C["toolbar_bg"])
        self.btn_row.pack(side=tk.TOP, padx=3, pady=(4, 0))

        tk.Frame(self, bg=C["border_soft"], height=1).pack(
            side=tk.BOTTOM, fill=tk.X)
        tk.Label(self, text=label.upper(), font=FONT_GRP,
                 fg=C["text_lo"], bg=C["toolbar_bg"]).pack(
            side=tk.BOTTOM, pady=(0, 2))

    def add_btn(self, icon, label, command=None, accent=None, tip=None):
        btn = CadButton(self.btn_row, icon, label,
                        command=command, accent=accent)
        btn.pack(side=tk.LEFT, padx=2, pady=2)
        if tip:
            Tooltip(btn, tip)
        return btn

    def add_toggle(self, icon, label, variable, command=None, tip=None):
        btn = CadToggle(self.btn_row, icon, label,
                        variable=variable, command=command)
        btn.pack(side=tk.LEFT, padx=2, pady=2)
        if tip:
            Tooltip(btn, tip)
        return btn


# ══════════════════════════════════════════════════
# 툴바 그룹 세로 구분선
# ══════════════════════════════════════════════════
class GroupSep(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, width=7, bg=C["toolbar_bg"], **kw)
        tk.Frame(self, width=1, bg=C["border_hard"]).pack(
            side=tk.LEFT, fill=tk.Y, padx=(2, 0), pady=6)
        tk.Frame(self, width=1, bg=C["border_soft"]).pack(
            side=tk.LEFT, fill=tk.Y, padx=(1, 0), pady=6)

    def pack(self, **kw):
        kw.setdefault("fill", tk.Y)
        kw.setdefault("padx", 2)
        super().pack(**kw)


# ══════════════════════════════════════════════════
# PI 인덱스 스피너 (툴바 내장)
# ══════════════════════════════════════════════════
class PiIndexWidget(tk.Frame):
    def __init__(self, master, variable, **kw):
        super().__init__(master, bg=C["toolbar_bg"], **kw)

        tk.Label(self, text="PI IDX", font=FONT_GRP,
                 fg=C["text_lo"], bg=C["toolbar_bg"]).pack(pady=(8, 0))

        inner = tk.Frame(self, bg=C["btn_normal"],
                         highlightthickness=1,
                         highlightbackground=C["border_soft"])
        inner.pack(padx=8, pady=4)

        tk.Button(inner, text="▲", font=("맑은 고딕", 6),
                  fg=C["text_md"], bg=C["btn_normal"],
                  activebackground=C["btn_hover"],
                  bd=0, relief="flat", cursor="hand2",
                  command=lambda: variable.set(variable.get() + 1)
                  ).pack(side=tk.LEFT, padx=(4, 0))

        self._entry = tk.Entry(inner, textvariable=variable,
                               width=4, font=FONT_COORD,
                               fg=C["text_hi"], bg=C["btn_normal"],
                               insertbackground=C["accent"],
                               bd=0, relief="flat", justify="center")
        self._entry.pack(side=tk.LEFT, ipady=4, pady=2)

        tk.Button(inner, text="▼", font=("맑은 고딕", 6),
                  fg=C["text_md"], bg=C["btn_normal"],
                  activebackground=C["btn_hover"],
                  bd=0, relief="flat", cursor="hand2",
                  command=lambda: variable.set(max(0, variable.get() - 1))
                  ).pack(side=tk.LEFT, padx=(0, 4))

        # 하단 여백 맞추기
        tk.Label(self, text="INDEX", font=FONT_GRP,
                 fg=C["text_lo"], bg=C["toolbar_bg"]).pack(pady=(0, 2))


# ══════════════════════════════════════════════════
# 메인 윈도우
# ══════════════════════════════════════════════════
class SegmentVisualizer(tk.Tk):
    """CAD 산업용 리본 툴바 스타일 선형설계 프로그램"""

    def __init__(self, event_controller, collection):
        super().__init__()
        self.collection            = collection
        self.event_controller      = event_controller
        self.dragging_index        = None
        self.dragging_midpoint_seg = None
        self._overlay_artists      = []

        self.title("OPENBVE 선형설계 프로그램")
        self.geometry("1440x860")
        self.minsize(1100, 680)
        self.configure(bg=C["chrome"])

        self._apply_ttk_style()
        self._build_titlebar()
        self._build_toolbar()
        self._build_workspace()
        self._build_statusbar()
        self._bind_mode_trace()

    # ── TTK 스타일 ──────────────────────
    def _apply_ttk_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=C["toolbar_bg"],
                    foreground=C["text_hi"],
                    fieldbackground=C["btn_normal"],
                    bordercolor=C["border_soft"])

    # ── 타이틀바 ────────────────────────
    def _build_titlebar(self):
        bar = tk.Frame(self, bg=C["shadow"], height=30)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text="⬡  OPENBVE  선형설계 프로그램",
                 font=FONT_TITL, fg=C["accent"],
                 bg=C["shadow"]).pack(side=tk.LEFT, padx=12)

        badge = tk.Frame(bar, bg="#0e1e3a",
                         highlightthickness=1,
                         highlightbackground=C["accent_dim"])
        badge.pack(side=tk.RIGHT, padx=10, pady=4)
        tk.Label(badge, text=" CRS: EPSG 5186 ↔ 3857 ",
                 font=FONT_MONO, fg=C["accent"],
                 bg="#0e1e3a").pack(padx=4, pady=1)

    # ── 리본 툴바 ───────────────────────
    def _build_toolbar(self):
        # 상하 경계선으로 감싼 툴바
        outer = tk.Frame(self, bg=C["border_hard"])
        outer.pack(fill=tk.X)
        tk.Frame(outer, bg=C["border_soft"], height=1).pack(fill=tk.X)

        ribbon = tk.Frame(outer, bg=C["toolbar_bg"])
        ribbon.pack(fill=tk.X)

        # ① PI 인덱스 스피너
        self.pi_index_var = tk.IntVar(value=1)
        PiIndexWidget(ribbon, self.pi_index_var).pack(
            side=tk.LEFT, padx=(8, 0), fill=tk.Y)

        GroupSep(ribbon).pack(side=tk.LEFT)

        # ② 그룹: PI 편집 ─────────────────
        g_pi = ToolGroup(ribbon, "PI 편집")
        g_pi.pack(side=tk.LEFT, fill=tk.Y)

        self.add_pi_mode = tk.BooleanVar(value=False)
        g_pi.add_toggle("📍", "PI추가", self.add_pi_mode,
                         tip="활성화 후 캔버스 클릭 → PI 추가")
        g_pi.add_btn("✂", "PI삭제", self.remove_pi,
                     accent=C["red"],
                     tip="선택한 인덱스의 PI를 삭제합니다")

        GroupSep(ribbon).pack(side=tk.LEFT)

        # ③ 그룹: 곡선 ────────────────────
        g_curve = ToolGroup(ribbon, "곡선")
        g_curve.pack(side=tk.LEFT, fill=tk.Y)

        g_curve.add_btn("＋", "곡선추가", self.add_curve_ui,
                        accent=C["green"],
                        tip="선택한 PI에 곡선 반경을 추가합니다")
        g_curve.add_btn("✎", "곡선변경", self.update_radius_ui,
                        accent=C["accent"],
                        tip="선택한 PI의 곡선 반경을 수정합니다")
        g_curve.add_btn("✂", "곡선삭제", self.remove_curve,
                        accent=C["red"],
                        tip="선택한 PI의 곡선을 삭제합니다")

        GroupSep(ribbon).pack(side=tk.LEFT)

        # ④ 그룹: 보기 ────────────────────
        g_view = ToolGroup(ribbon, "보기")
        g_view.pack(side=tk.LEFT, fill=tk.Y)

        self.view_map_mode = tk.BooleanVar(value=False)
        g_view.add_toggle("🗺", "지도보기", self.view_map_mode,
                           command=lambda: self.event_controller.emit(
                               "map_view_mode_changed"),
                           tip="배경 지도 타일을 표시합니다")
        g_view.add_btn("↺", "지도갱신",
                       lambda: self.event_controller.emit("map_updated"),
                       accent=C["teal"],
                       tip="현재 뷰포트의 지도 타일을 다시 불러옵니다")

        GroupSep(ribbon).pack(side=tk.LEFT)

        # ⑤ 그룹: 파일 ────────────────────
        g_file = ToolGroup(ribbon, "파일")
        g_file.pack(side=tk.LEFT, fill=tk.Y)

        g_file.add_btn("💾", "저장",  self.save_to_json,
                       accent=C["green"],
                       tip="선형을 JSON 파일로 저장합니다")
        g_file.add_btn("📂", "로드",  self.load_from_json,
                       tip="JSON 파일에서 선형을 불러옵니다")

        GroupSep(ribbon).pack(side=tk.LEFT)

        # ⑥ 그룹: 시스템 ─────────────────
        g_sys = ToolGroup(ribbon, "시스템")
        g_sys.pack(side=tk.LEFT, fill=tk.Y)

        g_sys.add_btn("⟳", "초기화", self.reset_to_initial,
                      accent=C["amber"],
                      tip="모든 PI·곡선을 초기 상태로 되돌립니다")
        g_sys.add_btn("✕", "종료",   self.destroy,
                      accent=C["red"],
                      tip="프로그램을 종료합니다")

        # 툴바 하단 그림자선
        tk.Frame(self, bg=C["shadow"], height=2).pack(fill=tk.X)

    # ── 캔버스 영역 ─────────────────────
    def _build_workspace(self):
        self.canvas_frame = tk.Frame(self, bg=C["canvas_bg"],
                                     highlightthickness=0)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # ── 실제 사용 시 아래 주석 해제 ─────────────────────────
        from plotter.matplotter import Matplotter
        self.ploter = Matplotter( master=self.canvas_frame,events=self.event_controller,collection=self.collection)
        self.ploter.canvas.mpl_connect('pick_event',           self.on_pick)
        self.ploter.canvas.mpl_connect('motion_notify_event',  self.on_drag)
        self.ploter.canvas.mpl_connect('button_release_event', self.on_release)
        self.ploter.canvas.mpl_connect('button_press_event',   self.add_pi_click)
        # ────────────────────────────────────────────────────────

        # 데모용 플레이스홀더
        tk.Label(self.canvas_frame,
                 text="[ Matplotlib 캔버스 ]",
                 font=("맑은 고딕", 12),
                 fg=C["text_lo"], bg=C["canvas_bg"]).place(
            relx=0.5, rely=0.5, anchor="center")

    # ── 상태바 ─────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self, bg=C["statusbar"],
                       highlightthickness=1,
                       highlightbackground=C["border_hard"],
                       height=22)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        def vsep():
            tk.Frame(bar, bg=C["border_soft"], width=1).pack(
                side=tk.LEFT, fill=tk.Y, pady=3)

        # 상태 메시지
        self.status_var = tk.StringVar(value="준비")
        tk.Label(bar, textvariable=self.status_var,
                 font=FONT_MONO, fg=C["text_md"],
                 bg=C["statusbar"], anchor="w", padx=10).pack(side=tk.LEFT)

        vsep()

        # 현재 모드
        self.mode_var = tk.StringVar(value="● 일반")
        tk.Label(bar, textvariable=self.mode_var,
                 font=FONT_MONO, fg=C["accent"],
                 bg=C["statusbar"], padx=10).pack(side=tk.LEFT)

        # 오른쪽
        def vsep_r():
            tk.Frame(bar, bg=C["border_soft"], width=1).pack(
                side=tk.RIGHT, fill=tk.Y, pady=3)

        vsep_r()
        self.coord_var = tk.StringVar(value="X: ─────────  Y: ─────────")
        tk.Label(bar, textvariable=self.coord_var,
                 font=FONT_COORD, fg=C["text_lo"],
                 bg=C["statusbar"], padx=10).pack(side=tk.RIGHT)

        vsep_r()
        self.pi_disp_var = tk.StringVar(value="PI: 1")
        tk.Label(bar, textvariable=self.pi_disp_var,
                 font=FONT_MONO, fg=C["text_md"],
                 bg=C["statusbar"], padx=10).pack(side=tk.RIGHT)

        self.pi_index_var.trace_add(
            "write",
            lambda *_: self.pi_disp_var.set(f"PI: {self.pi_index_var.get()}")
        )

    # ── 모드 추적 ───────────────────────
    def _bind_mode_trace(self):
        def _upd(*_):
            if self.add_pi_mode.get():
                self.mode_var.set("● PI 추가 모드")
            elif self.view_map_mode.get():
                self.mode_var.set("● 지도 보기 모드")
            else:
                self.mode_var.set("● 일반")
        self.add_pi_mode.trace_add("write", _upd)
        self.view_map_mode.trace_add("write", _upd)

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
