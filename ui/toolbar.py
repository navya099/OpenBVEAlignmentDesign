# ══════════════════════════════════════════════════
# CAD 툴바 버튼 (아이콘 위 + 레이블 아래)
# ══════════════════════════════════════════════════
import tkinter as tk
from ui.design_tokens import C, FONT_GRP


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

    def set_text(self, new_text):
        """하단 레이블의 텍스트를 동적으로 변경"""
        if hasattr(self, '_lbl'):
            self._lbl.config(text=new_text)

    def set_icon(self, new_icon):
        """상단 아이콘(이모지)을 동적으로 변경"""
        if hasattr(self, '_ico'):
            self._ico.config(text=new_icon)