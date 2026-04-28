# ══════════════════════════════════════════════════
# CAD 토글 버튼 (ON 상태 강조)
# ══════════════════════════════════════════════════

import tkinter as tk
from ui.design_tokens import C, FONT_GRP

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
