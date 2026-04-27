# ══════════════════════════════════════════════════
# 유틸: 툴팁
# ══════════════════════════════════════════════════
from ui.design_tokens import FONT_MONO, C
import tkinter as tk

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