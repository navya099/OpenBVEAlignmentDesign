# ══════════════════════════════════════════════════
# 툴바 그룹 컨테이너
# ══════════════════════════════════════════════════


import tkinter as tk
from ui.design_tokens import C, FONT_GRP
from ui.toggle import CadToggle
from ui.toolbar import CadButton
from ui.tooltip import Tooltip

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