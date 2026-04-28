# controller/curve_controller.py
from tkinter import simpledialog, messagebox, filedialog

from bve.extract_csv import save_bve


class FileController:
    """파일 IO 컨트롤러"""
    def __init__(self, app, event_controller):
        self.app = app
        self.events = event_controller

    def request_load(self):
        """로드 요청 처리"""
        path = filedialog.askopenfilename(
            filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")])
        if not path:
            return
        try:
            self.events.emit('load_from_json', path)
            self.events.emit('load_from_json_finish')
            self.app.set_status(f"로드 완료: {path}")
            messagebox.showinfo("로드 완료", f"로드:\n{path}")
        except Exception as e:
            messagebox.showerror("로드 실패", str(e))


    def request_save(self):
            """저장 요청 처리"""
            path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")])
            if not path:
                return
            try:
                self.events.emit('save_to_json', path)
                self.app.set_status(f"저장 완료: {path}")
                messagebox.showinfo("저장 완료", f"저장:\n{path}")
            except Exception as e:
                messagebox.showerror("저장 실패", str(e))

    def request_export_bve(self):
        """BVE EXPORT 처리"""
        try:
            save_bve(self.app.collection.segment_list)
            self.app.set_status(f"BVE 저장 완료")
            messagebox.showinfo("저장 완료", f"저장:\n")
        except Exception as e:
            messagebox.showerror("BVE 저장 실패", str(e))