# ── 속성 창 ─────────────────────────
from tkinter import ttk

from myalignment.segment.segment_helper import SegmentHelper
from ui.design_tokens import FONT_MONO, C, FONT_TITL, FONT_GRP
from ui.toolbar import CadButton
import tkinter as tk


class PropertiesUI:
    def __init__(self, app):
        self.app = app
        self.mode = "PI"  # 초기 모드는 PI 요약 모드
        self.tree = None
        self.rows = []
        self.show_properties()

    def show_properties(self):
        win = tk.Toplevel(self.app)
        win.title("선형 속성 분석")
        win.configure(bg=C["chrome"])
        win.geometry("900x550")  # 상세 데이터를 위해 조금 더 넓게 설정
        win.minsize(700, 400)

        # ── 타이틀바 ──────────────────────
        self.hdr_frame = tk.Frame(win, bg=C["shadow"], height=32)
        self.hdr_frame.pack(fill=tk.X)

        self.title_label = tk.Label(self.hdr_frame, text="📋  선형 속성 (PI 요약)",
                                    font=FONT_TITL, fg=C["accent"], bg=C["shadow"])
        self.title_label.pack(side=tk.LEFT, padx=12)

        # ── Treeview 테이블 (설정은 동일하지만 컬럼 가변화 준비) ──
        self.tbl_frame = tk.Frame(win, bg=C["canvas_bg"])
        self.tbl_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.tbl_frame, show="headings", style="Prop.Treeview")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        vsb = ttk.Scrollbar(self.tbl_frame, orient=tk.VERTICAL, command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)

        # 태그 설정
        self.tree.tag_configure("odd", background=C["canvas_bg"])
        self.tree.tag_configure("even", background=C["btn_pressed"])
        self.tree.tag_configure("curve", foreground=C["green"])
        self.tree.tag_configure("transition", foreground=C["teal"])  # 완화곡선용 컬러 추가

        # ── 하단 버튼 바 ─────────────────
        btn_bar = tk.Frame(win, bg=C["statusbar"], height=40)
        btn_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # 총 연장 라벨
        self.total_label = tk.Label(btn_bar, text="", font=FONT_MONO, fg=C["teal"], bg=C["statusbar"])
        self.total_label.pack(side=tk.LEFT, padx=14)

        # [핵심] 모드 전환 버튼
        self.mode_btn = CadButton(btn_bar, "⇄", "전체 세그먼트 보기",
                                  command=self._toggle_mode,
                                  accent=C["accent"], width=140, height=30)
        self.mode_btn.pack(side=tk.RIGHT, padx=6)

        CadButton(btn_bar, "↺", "새로고침",
                  command=self._refresh_tree,
                  accent=C["teal"], width=80, height=30
                  ).pack(side=tk.RIGHT, padx=4)

        CadButton(btn_bar, "✕", "닫기",
                  command=win.destroy,
                  accent=C["red"], width=62, height=30
                  ).pack(side=tk.RIGHT, padx=4)

        # show_properties 내부 tree 설정 부분에 추가
        self.tree.bind("<Control-c>", lambda e: self._copy_to_clipboard(mode="selected"))

        # 우클릭 메뉴 정의
        self.context_menu = tk.Menu(self.tree, tearoff=0, bg=C["chrome"], fg=C["text_hi"])
        self.context_menu.add_command(label="선택한 행 복사 (Ctrl+C)",
                                      command=lambda: self._copy_to_clipboard(mode="selected"))
        self.context_menu.add_command(label="전체 내용 복사",
                                      command=lambda: self._copy_to_clipboard(mode="all"))

        def show_menu(event):
            self.context_menu.post(event.x_root, event.y_root)

        self.tree.bind("<Button-3>", show_menu)  # 우클릭 바인딩
        self._refresh_tree()  # 데이터 로드

    def _toggle_mode(self):
        """PI 모드 <-> 세그먼트 모드 전환"""
        if self.mode == "PI":
            self.mode = "SEG"
            self.mode_btn.set_text("PI 요약 보기")
            self.title_label.config(text="📋  전체 세그먼트 상세 데이터")
        else:
            self.mode = "PI"
            self.mode_btn.set_text("전체 세그먼트 보기")
            self.title_label.config(text="📋  선형 속성 (PI 요약)")

        self._refresh_tree()

    def _refresh_tree(self):
        """현재 모드에 맞춰 컬럼 재설정 및 데이터 갱신"""
        # 1. 컬럼 정의
        if self.mode == "PI":
            cols = [("idx", "IDX", 50), ("x", "X 좌표", 150), ("y", "Y 좌표", 150),
                    ("radius", "반경 R", 100), ("sta_bc", "시작 STA", 120),
                    ("sta_ec", "끝 STA", 120), ("length", "곡선장", 100)]
            rows = self._collect_properties()
        else:
            # 세그먼트 모드 컬럼
            cols = [("type", "유형", 100), ("start", "시작 지점", 140), ("end", "종료 지점", 140),
                    ("s_sta", "시작 STA", 130), ("e_sta", "끝 STA", 130), ("len", "연장 (m)", 110)]
            rows = self._collect_segments()

        # 2. Treeview 컬럼 재설정
        self.tree["columns"] = [c[0] for c in cols]
        for cid, title, w in cols:
            self.tree.heading(cid, text=title)
            self.tree.column(cid, width=w, anchor=tk.CENTER if cid == "type" else tk.CENTER)

        # 3. 데이터 삽입
        for item in self.tree.get_children(): self.tree.delete(item)

        def fmt(v, d=3):
            return f"{float(v):,.{d}f}" if (v is not None and v != "-") else "—"

        for i, r in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            if self.mode == "PI":
                vals = (r["idx"], fmt(r["x"]), fmt(r["y"]), fmt(r["radius"], 1),
                        fmt(r["start_sta"]), fmt(r["end_sta"]), fmt(r["length"]))
                if r["radius"]: tag = (tag, "curve")
            else:
                vals = (r["type"], r["pos_s"], r["pos_e"], fmt(r["s_sta"]), fmt(r["e_sta"]), fmt(r["len"]))
                if "곡선" in r["type"]:
                    tag = (tag, "curve")
                elif "완화" in r["type"]:
                    tag = (tag, "transition")

            self.tree.insert("", tk.END, values=vals, tags=tag)

        # 4. 총 연장 갱신
        t_len = sum(seg.length for seg in self.app.collection.segment_list) if self.app.collection.segment_list else 0
        self.total_label.config(text=f"총 노선 연장:  {t_len:,.3f} m")

    def _collect_segments(self) -> list:
        """모든 개별 세그먼트(직선/곡선/완화곡선)를 평탄화하여 수집"""
        seg_rows = []
        if not self.app.collection: return []

        for seg in self.app.collection.segment_list:
            # 유형 판별 (Segment 객체의 클래스나 속성에 따라 분기)
            stype = getattr(seg, 'type', '직선')
            # 예: "LineSegment" -> "직선", "ArcSegment" -> "원곡선" 등 매핑 필요

            row = {
                "type": stype.name,
                "pos_s": f"{seg.start_coord.x:.1f}, {seg.start_coord.y:.1f}",
                "pos_e": f"{seg.end_coord.x:.1f}, {seg.end_coord.y:.1f}",
                "s_sta": seg.start_sta,
                "e_sta": seg.end_sta,
                "len": seg.length
            }
            seg_rows.append(row)
        return seg_rows

    def _collect_properties(self) -> list:
        rows = []
        if not self.app.collection or not self.app.collection.coord_list:
            return rows

        pis = self.app.collection.coord_list
        radis = self.app.collection.radius_list
        groups = self.app.collection.groups
        num_pis = len(pis)

        for i in range(num_pis):
            pi = pis[i]
            r = radis[i]
            g = groups[i]

            # 1. 공통 속성 (이름 및 좌표)
            label = "BP" if i == 0 else ("EP" if i == num_pis - 1 else f"IP.{i}")
            row_data = {
                "idx": i,
                "label": label,
                "x": round(pi.x, 3),
                "y": round(pi.y, 3),
                "radius": r if 0 < i < num_pis - 1 else None,  # BP, EP는 반경 없음
                "start_sta": None,
                "end_sta": None,
                "length": None
            }

            try:
                # 2. IP(중간점)인 경우에만 곡선 속성 추출 시도
                if 0 < i < num_pis - 1:
                    if g is not None and hasattr(g, 'segments') and len(g.segments) > 0:
                        # 곡선 그룹이 존재하는 경우 (원곡선, 클로소이드 등 포함)
                        row_data.update({
                            "start_sta": round(g.segments[0].start_sta, 3),
                            "end_sta": round(g.segments[-1].end_sta, 3),
                            "length": round(sum(s.length for s in g.segments), 3)
                        })
                    else:
                        # 곡선이 없는 단순 굴절점(Radius=0)인 경우 None 처리 (또는 "-" 유지)
                        row_data.update({
                            "start_sta": None,
                            "end_sta": None,
                            "length": None
                        })

                # 3. BP/EP는 위에서 설정한 기본값("-" 혹은 좌표만) 유지
                rows.append(row_data)

            except Exception as e:
                print(f"Error collecting PI properties at index {i}: {e}")
                rows.append(row_data)
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
                fmt(r["start_sta"]), fmt(r["end_sta"]),
                fmt(r["length"]),
            ), tags=tags)

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

    def _copy_to_clipboard(self, mode="all"):
        """테이블 내용을 클립보드에 복사 (Tab 구분자 사용)"""
        import pandas as pd  # 데이터 처리가 편하도록 사용 (혹은 리스트로 직접 구현 가능)

        # 1. 컬럼 헤더 가져오기
        cols = self.tree["columns"]
        header = "\t".join([self.tree.heading(c)["text"] for c in cols])

        # 2. 데이터 가져오기
        lines = [header]

        if mode == "selected":
            # 선택된 행만 복사
            items = self.tree.selection()
        else:
            # 전체 행 복사
            items = self.tree.get_children()

        if not items:
            self.app.set_status("복사할 데이터가 없습니다.")
            return

        for item in items:
            vals = self.tree.item(item)["values"]
            lines.append("\t".join(map(str, vals)))

        # 3. 클립보드에 쓰기
        final_text = "\n".join(lines)
        self.app.clipboard_clear()
        self.app.clipboard_append(final_text)
        self.app.update()  # 클립보드 갱신 확정

        count = len(items)
        self.app.set_status(f"테이블 데이터({count}개 행)가 클립보드에 복사되었습니다.")