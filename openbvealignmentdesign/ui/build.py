# ui/ui_builder.py
import tkinter as tk
from ui.design_tokens import C, FONT_TITL, FONT_MONO, FONT_COORD
from ui.pi_idx_widget import PiIndexWidget
from ui.toolbar_grouop import ToolGroup, GroupSep


class UIBuilder:
    """
    UI 위젯 조립만 담당.
    - 상태 변수(BooleanVar 등)는 app이 소유, builder는 참조만 함
    - 이벤트 핸들러는 app의 메서드를 연결
    - self.app = 루트 윈도우(tk.Tk)이자 비즈니스 로직 소유자
    """

    def __init__(self, app):
        self.app = app  # SegmentVisualizer (tk.Tk 상속)

    def build(self):
        self._build_titlebar()
        self._build_toolbar()
        self._build_workspace()
        self._build_statusbar()

    # ── 타이틀바 ────────────────────────
    def _build_titlebar(self):
        bar = tk.Frame(self.app, bg=C["shadow"], height=30)  # self.app으로 통일
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
        outer = tk.Frame(self.app, bg=C["border_hard"])
        outer.pack(fill=tk.X)
        tk.Frame(outer, bg=C["border_soft"], height=1).pack(fill=tk.X)

        ribbon = tk.Frame(outer, bg=C["toolbar_bg"])
        ribbon.pack(fill=tk.X)

        # ── 상태 변수는 app이 소유, builder는 app에서 참조
        PiIndexWidget(ribbon, self.app.pi_index_var).pack(
            side=tk.LEFT, padx=(8, 0), fill=tk.Y)

        GroupSep(ribbon).pack(side=tk.LEFT)

        g_pi = ToolGroup(ribbon, "PI 편집")
        g_pi.pack(side=tk.LEFT, fill=tk.Y)
        g_pi.add_toggle("📍", "PI추가", self.app.add_pi_mode,
                        tip="활성화 후 캔버스 클릭 → PI 추가")
        g_pi.add_btn("✎", "PI편집", self.app.edit_pi,
                     accent=C["red"],
                     tip="선택한 인덱스의 PI를 수정합니다")
        g_pi.add_btn("✂", "PI삭제", self.app.remove_pi,
                     accent=C["red"],
                     tip="선택한 인덱스의 PI를 삭제합니다")
        GroupSep(ribbon).pack(side=tk.LEFT)

        g_curve = ToolGroup(ribbon, "곡선")
        g_curve.pack(side=tk.LEFT, fill=tk.Y)
        g_curve.add_btn("＋", "곡선추가", self.app.add_curve_ui,
                        accent=C["green"],
                        tip="선택한 PI에 곡선 반경을 추가합니다")
        g_curve.add_btn("✎", "곡선변경", self.app.update_radius_ui,
                        accent=C["accent"],
                        tip="선택한 PI의 곡선 반경을 수정합니다")
        g_curve.add_btn("✂", "곡선삭제", self.app.remove_curve,
                        accent=C["red"],
                        tip="선택한 PI의 곡선을 삭제합니다")

        GroupSep(ribbon).pack(side=tk.LEFT)

        g_view = ToolGroup(ribbon, "보기")
        g_view.pack(side=tk.LEFT, fill=tk.Y)
        g_view.add_toggle("🗺", "지도보기", self.app.view_map_mode,
                          command=lambda: self.app.event_controller.emit(
                              "map_view_mode_changed"),
                          tip="배경 지도 타일을 표시합니다")
        g_view.add_btn("↺", "지도갱신",
                       lambda: self.app.event_controller.emit("map_updated"),
                       accent=C["teal"],
                       tip="현재 뷰포트의 지도 타일을 다시 불러옵니다")

        GroupSep(ribbon).pack(side=tk.LEFT)

        g_file = ToolGroup(ribbon, "파일")
        g_file.pack(side=tk.LEFT, fill=tk.Y)
        g_file.add_btn("💾", "저장", self.app.save_to_json,
                       accent=C["green"],
                       tip="선형을 JSON 파일로 저장합니다")
        g_file.add_btn("📂", "로드", self.app.load_from_json,
                       tip="JSON 파일에서 선형을 불러옵니다")

        GroupSep(ribbon).pack(side=tk.LEFT)

        g_sys = ToolGroup(ribbon, "시스템")
        g_sys.pack(side=tk.LEFT, fill=tk.Y)
        g_sys.add_btn("⟳", "초기화", self.app.reset_to_initial,
                      accent=C["amber"],
                      tip="모든 PI·곡선을 초기 상태로 되돌립니다")
        g_sys.add_btn("✕", "종료", self.app.destroy,
                      accent=C["red"],
                      tip="프로그램을 종료합니다")

        tk.Frame(self.app, bg=C["shadow"], height=2).pack(fill=tk.X)

    # ── 캔버스 영역 ─────────────────────
    def _build_workspace(self):

        canvas_frame = tk.Frame(self.app, bg=C["canvas_bg"],
                                highlightthickness=0)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.app.canvas_frame = canvas_frame  # app에 참조 저장

    # ── 상태바 ─────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self.app, bg=C["statusbar"],
                       highlightthickness=1,
                       highlightbackground=C["border_hard"],
                       height=22)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        def vsep(side=tk.LEFT):
            tk.Frame(bar, bg=C["border_soft"], width=1).pack(
                side=side, fill=tk.Y, pady=3)

        # 상태 메시지 — app의 StringVar 참조
        tk.Label(bar, textvariable=self.app.status_var,
                 font=FONT_MONO, fg=C["text_md"],
                 bg=C["statusbar"], anchor="w", padx=10).pack(side=tk.LEFT)
        vsep()

        tk.Label(bar, textvariable=self.app.mode_var,
                 font=FONT_MONO, fg=C["accent"],
                 bg=C["statusbar"], padx=10).pack(side=tk.LEFT)

        vsep(tk.RIGHT)
        tk.Label(bar, textvariable=self.app.coord_var,
                 font=FONT_COORD, fg=C["text_lo"],
                 bg=C["statusbar"], padx=10).pack(side=tk.RIGHT)

        vsep(tk.RIGHT)
        tk.Label(bar, textvariable=self.app.pi_disp_var,
                 font=FONT_MONO, fg=C["text_md"],
                 bg=C["statusbar"], padx=10).pack(side=tk.RIGHT)