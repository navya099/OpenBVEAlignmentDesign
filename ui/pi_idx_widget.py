# ══════════════════════════════════════════════════
# PI 인덱스 스피너 (툴바 내장)
# ══════════════════════════════════════════════════
import tkinter as tk

from ui.design_tokens import FONT_GRP, C, FONT_COORD


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
