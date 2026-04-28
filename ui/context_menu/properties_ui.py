# ── 속성 창 ─────────────────────────
from tkinter import ttk

from data.segment.segment_helper import SegmentHelper
from ui.design_tokens import FONT_MONO, C, FONT_TITL, FONT_GRP
from ui.toolbar import CadButton
import tkinter as tk

class PropertiesUI:
    def __init__(self, app):
        self.app  =app
        self.show_properties()

    def show_properties(self):
        """선형 속성 테이블 창 (PI좌표 / 반경 / 스테이션)"""

        rows = self._collect_properties()

        win = tk.Toplevel(self.app)
        win.title("선형 속성")
        win.configure(bg=C["chrome"])
        win.geometry("820x500")
        win.minsize(640, 340)
        win.resizable(True, True)

        # ── 타이틀바 ──────────────────────
        hdr = tk.Frame(win, bg=C["shadow"], height=28)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📋  선형 속성  —  PI / 곡선 / 스테이션",
                 font=FONT_TITL, fg=C["accent"],
                 bg=C["shadow"]).pack(side=tk.LEFT, padx=12)
        tk.Label(hdr, text=f"총 {len(rows)} 개 PI",
                 font=FONT_MONO, fg=C["text_lo"],
                 bg=C["shadow"]).pack(side=tk.RIGHT, padx=12)

        tk.Frame(win, bg=C["border_soft"], height=1).pack(fill=tk.X)

        # ── Treeview 테이블 ───────────────
        COLS = [
            ("idx", "IDX", 48, tk.CENTER),
            ("x", "X 좌표 (m)", 165, tk.RIGHT),
            ("y", "Y 좌표 (m)", 165, tk.RIGHT),
            ("radius", "반경 R (m)", 110, tk.RIGHT),
            ("sta_bc", "시작 스테이션", 125, tk.RIGHT),
            ("sta_ec", "끝 스테이션", 125, tk.RIGHT),
            ("length", "길이 (m)", 110, tk.RIGHT),
        ]

        # TTK 스타일 (창 전용)
        s = ttk.Style(win)
        s.theme_use("clam")
        s.configure("Prop.Treeview",
                    background=C["canvas_bg"],
                    foreground=C["text_hi"],
                    fieldbackground=C["canvas_bg"],
                    rowheight=26,
                    font=FONT_MONO,
                    borderwidth=0,
                    relief="flat")
        s.configure("Prop.Treeview.Heading",
                    background=C["group_bg"],
                    foreground=C["text_md"],
                    font=FONT_GRP,
                    relief="flat",
                    borderwidth=0,
                    padding=(4, 4))
        s.map("Prop.Treeview",
              background=[("selected", C["accent_dim"])],
              foreground=[("selected", C["text_hi"])])
        s.map("Prop.Treeview.Heading",
              background=[("active", C["btn_hover"])])

        tbl_frame = tk.Frame(win, bg=C["canvas_bg"])
        tbl_frame.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tbl_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tbl_frame, orient=tk.HORIZONTAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        tree = ttk.Treeview(
            tbl_frame,
            columns=[c[0] for c in COLS],
            show="headings",
            style="Prop.Treeview",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="browse",
        )
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        tree.pack(fill=tk.BOTH, expand=True)

        # 컬럼 헤더 설정 (클릭 시 정렬)
        for cid, title, w, anc in COLS:
            tree.heading(cid, text=title,
                         command=lambda c=cid: self._sort_tree(tree, c, False))
            tree.column(cid, width=w, minwidth=44, anchor='center', stretch=False)

        # 행 스타일 태그
        tree.tag_configure("odd", background=C["canvas_bg"])
        tree.tag_configure("even", background=C["btn_pressed"])
        tree.tag_configure("curve", foreground=C["green"])
        tree.tag_configure("straight", foreground=C["text_md"])

        self._populate_tree(tree, rows)

        # ── 하단 버튼/요약 바 ─────────────
        btn_bar = tk.Frame(win, bg=C["statusbar"], height=36)
        btn_bar.pack(fill=tk.X, side=tk.BOTTOM)
        btn_bar.pack_propagate(False)
        tk.Frame(btn_bar, bg=C["border_soft"], height=1).pack(
            fill=tk.X, side=tk.TOP)

        total_len = sum(r["length"] for r in rows if r["length"] is not None)
        # 라벨을 self.total_label로 저장하여 나중에 접근 가능하게 함
        self.total_label = tk.Label(btn_bar,
                                    text=f"총 노선 연장:  {total_len:,.2f} m",
                                    font=FONT_MONO, fg=C["teal"],
                                    bg=C["statusbar"])
        self.total_label.pack(side=tk.LEFT, padx=14)

        CadButton(btn_bar, "↺", "새로고침",
                  command=lambda: self._refresh_tree(tree),
                  accent=C["teal"], width=72, height=30
                  ).pack(side=tk.RIGHT, padx=6, pady=3)
        CadButton(btn_bar, "✕", "닫기",
                  command=win.destroy,
                  accent=C["red"], width=62, height=30
                  ).pack(side=tk.RIGHT, padx=4, pady=3)

    def _collect_properties(self) -> list:
        rows = []
        if not self.app.collection or not self.app.collection.coord_list:
            return rows

        # 1:1:1 대응 관계 데이터
        pis = self.app.collection.coord_list
        radis = self.app.collection.radius_list
        groups = self.app.collection.groups

        # 생성된 결과물 (직선/곡선 혼합)
        # segs는 [직선, 곡선, 직선, 곡선...] 식의 순서로 쌓여있을 것임
        segs = self.app.collection.segment_list

        for i in range(len(pis)):
            pi = pis[i]
            r = radis[i]
            g = groups[i]

            # 기본값 (데이터가 없는 BP/EP 등 대비)
            row_data = {
                "idx": i, "x": pi.x, "y": pi.y, "radius": r,
                "sta_bc": 0.0, "sta_ec": 0.0, "length": 0.0
            }

            try:
                # CASE 1: PI에 곡선(Group)이 존재하는 경우
                if g is not None and hasattr(g, 'segments') and len(g.segments) > 0:
                    # Group 내부의 핵심 세그먼트(보통 첫 번째가 원곡선)에서 정보 추출
                    main_seg = g.segments[0]
                    row_data.update({
                        "sta_bc": main_seg.start_sta,
                        "sta_ec": main_seg.end_sta,
                        "length": sum(s.length for s in g.segments)  # 그룹 전체 길이
                    })

                # CASE 2: Group은 없지만 연결된 선분이 있는 경우 (BP, EP 또는 굴절 없는 PI)
                # 보통 i번째 PI는 i-1번째 혹은 i번째 세그먼트와 연관됨
                elif len(segs) > 0:
                    # 리스트 범위를 벗어나지 않도록 안전하게 참조
                    target_idx = min(i, len(segs) - 1)
                    seg = segs[target_idx]
                    row_data.update({
                        "sta_bc": seg.start_sta,
                        "sta_ec": seg.end_sta,
                        "length": seg.length
                    })

                rows.append(row_data)

            except Exception as e:
                print(f"Error collecting row {i}: {e}")
                rows.append(row_data)  # 에러 시 기본값이라도 삽입

        return rows

    def _populate_tree(self, tree: ttk.Treeview, rows: list):
        for item in tree.get_children():
            tree.delete(item)

        def fmt(v, d=2):
            return f"{v:,.{d}f}" if v is not None else "—"

        for i, r in enumerate(rows):
            tags = ("even" if i % 2 == 0 else "odd",
                    "curve" if r["radius"] else "straight")
            tree.insert("", tk.END, values=(
                r["idx"],
                fmt(r["x"], 3), fmt(r["y"], 3),
                fmt(r["radius"], 1),
                fmt(r["sta_bc"]), fmt(r["sta_ec"]),
                fmt(r["length"]),
            ), tags=tags)

    def _refresh_tree(self, tree: ttk.Treeview):
        # 1. 최신 데이터 수집
        new_rows = self._collect_properties()

        # 2. 테이블 갱신
        self._populate_tree(tree, new_rows)

        # 3. 총 연장 합계 재계산 및 라벨 갱신 (핵심!)
        total_len = sum(r["length"] for r in new_rows if r["length"] is not None)
        self.total_label.config(text=f"총 노선 연장:  {total_len:,.2f} m")

        self.app.set_status("속성 창 데이터 및 총 연장 갱신 완료")


    def _sort_tree(self, tree: ttk.Treeview, col: str, descending: bool):
        """컬럼 헤더 클릭 시 정렬 (숫자/문자 자동 구분)"""
        data = [(tree.set(k, col), k) for k in tree.get_children("")]

        def _key(v):
            try:
                return (0, float(v[0].replace(",", "")))
            except ValueError:
                return (1, v[0])

        data.sort(key=_key, reverse=descending)
        for idx, (_, k) in enumerate(data):
            tree.move(k, "", idx)
        tree.heading(col, command=lambda: self._sort_tree(
            tree, col, not descending))