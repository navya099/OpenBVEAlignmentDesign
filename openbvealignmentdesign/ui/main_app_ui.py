import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt

from AutoCAD.point2d import Point2d
from event.event_controller import EventController
from pyproj import Transformer
from plotter.matplotter import Matplotter

transformer_to_3857 = Transformer.from_crs("EPSG:5186", "EPSG:3857", always_xy=True)
transformer_to_5186 = Transformer.from_crs("EPSG:3857", "EPSG:5186", always_xy=True)

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class SegmentVisualizer(tk.Tk):
    """SegmentCollection 시각화 + 지도 모드 + 드래그 가능한 PI"""

    def __init__(self, event_controller, collection):
        super().__init__()
        self.collection = collection
        self.dragging_midpoint_seg = None
        self.dragging_midpoint_index = None
        self.title("OPENBVE용 선형설계 프로그램")
        self.geometry("1200x1000")
        self.event_controller = event_controller #이벤트 컨트롤러 등록
        # matplotlib figure
        self.ploter = Matplotter(master=self, events=self.event_controller, collection=self.collection)

        # UI 컨트롤
        control = ttk.Frame(self)
        control.pack(fill=tk.X, pady=5)
        ttk.Label(control, text="PI 인덱스:").pack(side=tk.LEFT, padx=5)
        self.pi_index_var = tk.IntVar(value=1)
        ttk.Entry(control, textvariable=self.pi_index_var, width=5).pack(side=tk.LEFT)
        ttk.Button(control, text="PI 삭제", command=self.remove_pi).pack(side=tk.LEFT, padx=5)
        ttk.Button(control, text="초기화", command=self.reset_to_initial).pack(side=tk.LEFT, padx=5)

        self.add_pi_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(control, text="PI 추가", variable=self.add_pi_mode).pack(side=tk.LEFT, padx=10)

        self.remove_curve_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control, text="곡선만 삭제", variable=self.remove_curve_var).pack(side=tk.LEFT, padx=10)

        self.view_map_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(control, text="지도 보기", variable=self.view_map_mode,
                        command=lambda: self.event_controller.emit("map_view_mode_changed")).pack(side=tk.LEFT, padx=10)

        ttk.Button(control, text="곡선 추가", command=self.add_curve_ui).pack(side=tk.LEFT, padx=10)
        ttk.Button(control, text="곡선 변경", command=self.update_radius_ui).pack(side=tk.LEFT, padx=10)

        # ✅ 지도 갱신 버튼 추가
        ttk.Button(control, text="지도 갱신", command=self.event_controller.emit('map_updated')).pack(side=tk.LEFT, padx=10)

        # ✅저장 버튼 추가
        ttk.Button(control, text="저장", command=self.save_to_json).pack(side=tk.LEFT, padx=10)

        # ✅로드 버튼 추가
        ttk.Button(control, text="로드", command=self.load_from_json).pack(side=tk.LEFT, padx=10)
        ttk.Button(control, text="종료", command=self.destroy).pack(side=tk.LEFT, padx=10)
        # 상태
        self.dragging_index = None
        self._overlay_artists = []

        # 이벤트 등록
        self.ploter.canvas.mpl_connect('pick_event', self.on_pick)
        self.ploter.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.ploter.canvas.mpl_connect('button_release_event', self.on_release)
        self.ploter.canvas.mpl_connect('button_press_event', self.add_pi)

    def add_pi(self, event):
        """마우스 클릭으로 PI 추가"""
        if not self.add_pi_mode.get():
            return
        if event.xdata is None or event.ydata is None:
            return

        if self.view_map_mode.get():
            x, y = transformer_to_5186.transform(event.xdata, event.ydata)
        else:
            x, y = event.xdata, event.ydata

        coord = Point2d(x, y)

        try:
            # 이벤트 발생만 담당
            self.event_controller.emit('pi_added', coord)
            self.event_controller.emit('pi_added_finish', coord)
        except Exception as e:
            messagebox.showerror("PI 추가 오류", f'{e}')

    #객체관리
    def remove_pi(self):
        """PI삭제"""
        is_only_remove_curve = self.remove_curve_var.get()
        pi_idx = self.pi_index_var.get()
        try:
            self.event_controller.emit('pi_removed', is_only_remove_curve, pi_idx)
            self.event_controller.emit('pi_removed_finish', is_only_remove_curve, pi_idx)
        except Exception as e:
            messagebox.showerror("PI 삭제 오류", f'{e}')

    def reset_to_initial(self):
        """컬렉션 초기화"""
        try:
            self.event_controller.emit('reset_to_initial')
            self.event_controller.emit('reset_to_initial_finish')
        except Exception as e:
            messagebox.showerror('초기화 중 오류 발생',f'{e}')

    def add_curve_ui(self):
        """곡선 추가"""
        idx = self.pi_index_var.get()
        radius = simpledialog.askfloat("곡선 추가", "곡선 반경 (R)을 입력하세요:", parent=self)
        if not radius:
            raise ValueError("반경이 유효하지 앖습니다.")
        if radius <= 0:
            raise ValueError("반경은 양수여야 합니다.")
        try:
            # 이벤트 발생만 담당
            self.event_controller.emit('curve_added', idx, radius)
            self.event_controller.emit('curve_added_finish', idx, radius)
            messagebox.showinfo("완료", f"PI {idx}에 반경 {radius:.2f}m 곡선 추가 완료")
        except Exception as e:
            messagebox.showerror("곡선 추가 에러", f'{e}')

    def update_radius_ui(self):
        """곡선 반경 변경"""
        try:
            idx = self.pi_index_var.get()
            radius = simpledialog.askfloat("곡선반경 수정", "곡선 반경 (R)을 입력하세요:", parent=self)
            if not radius:
                raise ValueError("반경이 유효하지 앖습니다.")
            if radius <= 0:
                raise ValueError("반경은 양수여야 합니다.")
            self.event_controller.emit('curve_changed', idx, radius)
            self.event_controller.emit('curve_changed_finish', idx, radius)
            messagebox.showinfo("완료", f"PI {idx}->곡선 변경 {radius:.2f}m")
        except Exception as e:
            messagebox.showerror("곡선 수정 에러", f'{e}')

    # ────────────────────────────────
    # 드래그 이벤트
    # ────────────────────────────────

    def on_pick(self, event):
        # PI인지 확인
        if event.artist == self.ploter.pi_scatter:
            self.dragging_index = event.ind[0]
            self.dragging_midpoint_seg = None
            return

        # MIDPOINT인지 확인
        for scatter, seg in self.ploter.mid_scatters:
            if event.artist == scatter:
                self.dragging_midpoint_seg = seg
                self.dragging_index = None
                return

    def on_drag(self, event):
        if self.dragging_index is not None:
            self._drag_pi(event)
        elif self.dragging_midpoint_seg is not None:
            self._drag_mid_point(event)

    def _drag_pi(self, event):
        """PI 드래그 중 (지도 갱신 생략)"""
        if self.dragging_index is None:
            return
        if event.xdata is None or event.ydata is None:
            return

        new_point = self._event_to_xy(event)
        if new_point is None:
            return
        try:
            self.event_controller.emit('pi_dragged', new_point, self.dragging_index)
            self.event_controller.emit('pi_dragged_finish', new_point)

        except Exception as e:
            messagebox.showerror('업데이트 실패', str(e))

    def on_release(self, event):
        if self.dragging_index is None and self.dragging_midpoint_seg is None:
            return
        new_point = self._event_to_xy(event)
        if new_point is None:
            return
        try:
            if self.dragging_index is not None:
                self.event_controller.emit('pi_dragged', new_point, self.dragging_index)
                self.event_controller.emit('pi_dragged_finish')
            elif self.dragging_midpoint_seg is not None:
                self.event_controller.emit('midpoint_dragged', self.dragging_midpoint_seg, new_point)
                self.event_controller.emit('midpoint_dragged_finish')
        except Exception as e:
            messagebox.showerror('업데이트 실패', str(e))

        # 상태 초기화
        self.dragging_index = None
        self.dragging_midpoint_seg = None

    def save_to_json(self):
        try:
            save_path = filedialog.asksaveasfilename()
            self.event_controller.emit('save_to_json', save_path)
            messagebox.showinfo("저장 완료", f"JSON 저장 완료: {save_path}")
        except Exception as e:
            messagebox.showerror('json 저장 실패', str(e))
    def load_from_json(self):
        try:
            load_path = filedialog.askopenfilename()
            self.event_controller.emit('load_from_json', load_path)
            self.event_controller.emit('load_from_json_finish')
            messagebox.showinfo("로드 완료", f"JSON 로드 완료: {load_path}")
        except Exception as e:
            messagebox.showerror('json 로드 실패', str(e))

    def _event_to_xy(self, event):
        """마우스 이벤트 → 내부 좌표(x,y) 변환 (공통 메서드)"""
        if event.xdata is None or event.ydata is None:
            return None

        if self.view_map_mode.get():
            x, y = transformer_to_5186.transform(event.xdata, event.ydata)
        else:
            x, y = event.xdata, event.ydata

        return Point2d(x, y)


    def _drag_mid_point(self, event):
        if self.dragging_midpoint_seg is None:
            return
        if event.xdata is None or event.ydata is None:
            return

        try:
            new_mid = self._event_to_xy(event)
            # 이벤트 발생만 담당
            self.event_controller.emit('midpoint_dragged', self.dragging_midpoint_seg, new_mid)
            self.event_controller.emit('midpoint_dragged_finish', new_mid)
        except Exception as e:
            messagebox.showerror('업데이트 실패', str(e))