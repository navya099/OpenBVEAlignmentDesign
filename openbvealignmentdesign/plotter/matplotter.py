import tkinter as tk
from tkinter import messagebox

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from pyproj import Transformer
import contextily as ctx

transformer_to_3857 = Transformer.from_crs("EPSG:5186", "EPSG:3857", always_xy=True)
transformer_to_5186 = Transformer.from_crs("EPSG:3857", "EPSG:5186", always_xy=True)

class Matplotter:
    def __init__(self, master, events, collection):
        self.master = master      # Tkinter Frame/Window
        self.events = events
        self.collection = collection

        # matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 6))

        # canvas와 toolbar를 master에 붙임
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        self.toolbar.update()

        if self.events:
            self.events.bind('pi_added', self.update_plot)
            self.events.bind('pi_removed', self.update_plot)
            self.events.bind('pi_changed', self.update_plot)
            self.events.bind('reset_to_initial', self.update_plot)
            self.events.bind('curve_added', self.update_plot)
            self.events.bind('curve_changed', self.update_plot)
            self.events.bind('pi_dragged', self.update_plot)
            self.events.bind('midpoint_dragged', self.update_plot)


    def update_plot(self, force_xlim=None, force_ylim=None, zoom=None, view_map_mode=None):
        """전체 다시 그림 — 외부에서 force_xlim/ylim/zoom 전달 가능"""
        self.fig.clf()
        self.ax.clear()

        if view_map_mode:
            # 전달된 force_* 를 _draw_map_basemap 에서 사용하게 함
            self._draw_map_basemap(zoom=zoom,
                                   force_xlim=force_xlim,
                                   force_ylim=force_ylim)

        self._draw_segments(view_map_mode)
        self.canvas.draw_idle()

    def _draw_map_basemap(self, zoom=None, force_xlim=None, force_ylim=None):
        """지도 배경 추가 — force_xlim/ylim 이 주어지면 그걸 우선 사용"""
        if not self.collection.coord_list:
            return

        xs, ys = zip(*[transformer_to_3857.transform(pt.x, pt.y)
                       for pt in self.collection.coord_list])

        # default extent (데이터 기반)
        margin_x = (max(xs) - min(xs)) * 0.15 or 500
        margin_y = (max(ys) - min(ys)) * 0.15 or 500
        default_xlim = (min(xs) - margin_x, max(xs) + margin_x)
        default_ylim = (min(ys) - margin_y, max(ys) + margin_y)

        # force 가 있으면 우선 사용, 없으면 기본 extent 사용
        if force_xlim is not None and force_ylim is not None:
            self.ax.set_xlim(force_xlim)
            self.ax.set_ylim(force_ylim)
        else:
            # 최초 표시나 강제 재계산 시 기본 영역 적용
            self.ax.set_xlim(default_xlim)
            self.ax.set_ylim(default_ylim)

        self.ax.set_aspect('equal', adjustable='datalim')

        # === zoom 결정: 호출자가 줌 전달하면 사용, 아니면 데이터 기반 계산 ===
        import numpy as np
        if zoom is None:
            dx = self.ax.get_xlim()[1] - self.ax.get_xlim()[0]
            dy = self.ax.get_ylim()[1] - self.ax.get_ylim()[0]
            max_dim = max(dx, dy)
            zoom = int(18 - np.log2(max_dim / 500))
            zoom = int(np.clip(zoom, 5, 18))
        else:
            zoom = int(np.clip(zoom, 5, 18))

        try:
            ctx.add_basemap(
                self.ax,
                crs="EPSG:3857",
                source=ctx.providers.OpenStreetMap.Mapnik,
                zoom=zoom
            )
        except Exception as e:
            print(f"[지도 로드 실패]: {e}, zoom={zoom}")

    def _draw_segments(self, view_map_mode):
        colors = {"StraightSegment": "blue", "CurveSegment": "orange", "CUBICSegment": "green"}
        self.mid_scatters = []

        for seg in self.collection.segment_list:
            pts = self.segment_to_xy(seg)
            if not pts:
                continue

            if view_map_mode:
                pts = [transformer_to_3857.transform(x, y) for x, y in pts]

            x, y = zip(*pts)
            color = colors.get(seg.__class__.__name__, "gray")
            self.ax.plot(x, y, color=color, lw=2, zorder=2)

            mid = seg.midpoint
            if mid:
                if view_map_mode:
                    mid = transformer_to_3857.transform(*mid)
                scatter = self.ax.scatter(mid[0], mid[1], color='purple', s=40, zorder=6, picker=5)
                self.mid_scatters.append((scatter, seg))

    def segment_to_xy(self, seg):
        """이동예정"""
        if isinstance(seg, StraightSegment):
            return [(seg.start_coord.x, seg.start_coord.y),
                    (seg.end_coord.x, seg.end_coord.y)]
        if isinstance(seg, CurveSegment):
            x_arc, y_arc = draw_arc(seg.direction, seg.start_coord, seg.end_coord, seg.center_coord)
            return list(zip(x_arc, y_arc))
        return None

    def update_map_zoom(self):
        """현재 뷰 범위 기반으로 지도 타일만 다시 로드"""
        if not self.view_map_mode.get():
            messagebox.showinfo("안내", "지도 보기 모드를 먼저 켜세요.")
            return

        try:
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            dx = xlim[1] - xlim[0]
            dy = ylim[1] - ylim[0]
            max_dim = max(dx, dy)

            import numpy as np
            zoom = int(18 - np.log2(max_dim / 500))
            zoom = int(np.clip(zoom, 5, 18))

            # 현재 지도 타일만 다시 추가 (Axes는 그대로 유지)
            # 기존 타일 제거
            for im in list(self.ax.images):
                im.remove()

            # 새 타일 불러오기
            ctx.add_basemap(
                self.ax,
                crs="EPSG:3857",
                source=ctx.providers.OpenStreetMap.Mapnik,
                zoom=zoom
            )

            # 기존 확대/이동 상태 그대로 복원
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
            self.canvas.draw_idle()

            print(f"[지도 갱신 완료] zoom={zoom}")

        except Exception as e:
            messagebox.showerror("지도 갱신 실패", str(e))