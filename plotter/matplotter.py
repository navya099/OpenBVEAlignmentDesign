import tkinter as tk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from pyproj import Transformer
import contextily as ctx
import numpy as np
from data.segment.segment_helper import SegmentHelper

transformer_to_3857 = Transformer.from_crs("EPSG:5186", "EPSG:3857", always_xy=True)
transformer_to_5186 = Transformer.from_crs("EPSG:3857", "EPSG:5186", always_xy=True)

class Matplotter:
    def __init__(self, master, events, collection):
        self.master = master      # Tkinter Frame/Window
        self.events = events
        self.collection = collection

        # matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.ax.set_facecolor('black')
        # canvas와 toolbar를 master에 붙임
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        self.toolbar.update()

        if self.events:
            self.events.bind('pi_added_finish', self.update_plot)
            self.events.bind('pi_removed_finish', self.update_plot)
            self.events.bind('pi_changed_finish', self.update_plot)
            self.events.bind('reset_to_initial_finish', self.update_plot)
            self.events.bind('curve_added_finish', self.update_plot)
            self.events.bind('curve_changed_finish', self.update_plot)
            self.events.bind('curve_removed_finish', self.update_plot)
            self.events.bind('pi_dragged_finish', self.update_plot)
            self.events.bind('midpoint_dragged_finish', self.update_plot)
            self.events.bind('map_view_mode_changed_finish', self.update_plot)
            self.events.bind('map_updated_finish', self.update_map_zoom)
            self.events.bind('load_from_json_finish', self.reset_view_to_data)

    def update_plot(self, force_xlim=None, force_ylim=None, view_map_mode=None):
        """전체 다시 그림 — 외부에서 force_xlim/ylim/zoom 전달 가능"""
        # 줌/이동 유지
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        self.ax.clear()
        self.ax.set_facecolor('black')

        if not self.collection.coord_list:
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
            self.canvas.draw_idle()  # <--- 데이터가 없을 때도 화면을 갱신해줘야 함
            return

        if view_map_mode:
            #지도 모드에서는 xlim ,ylim 좌표변환 필요
            xmin, xmax = xlim
            ymin, ymax = ylim
            # 좌하단
            x1, y1 = transformer_to_3857.transform(xmin, ymin)

            # 우상단
            x2, y2 = transformer_to_3857.transform(xmax, ymax)

            xlim = (x1, x2)
            ylim = (y1, y2)

            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)

            # 전달된 force_* 를 _draw_map_basemap 에서 사용하게 함
            self.ax.set_facecolor('white') #배경색 휜화면으로
            self._draw_map_basemap(xlim=xlim, ylim=ylim)

        self._draw_segments(view_map_mode)

        # force 가 있으면 우선 사용, 없으면 기본 extent 사용
        if force_xlim is not None and force_ylim is not None:
            self.ax.set_xlim(force_xlim)
            self.ax.set_ylim(force_ylim)
        else:
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)

        self.canvas.draw_idle()

    def _draw_map_basemap(self, zoom=None, xlim=None, ylim=None):
        """지도 배경 추가 — force_xlim/ylim 이 주어지면 그걸 우선 사용"""
        if not self.collection.coord_list:
            return

        # === zoom 결정: 호출자가 줌 전달하면 사용, 아니면 데이터 기반 계산 ===

        if zoom is None:
            dx = xlim[1] - xlim[0]
            dy = ylim[1] - ylim[0]
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

        self.mid_scatters = []

        for seg in self.collection.segment_list:
            pts = SegmentHelper.segment_to_xy(seg)
            if not pts:
                continue

            if view_map_mode:
                pts = [transformer_to_3857.transform(x, y) for x, y in pts]

            x, y = zip(*pts)
            color = SegmentHelper.get_color(seg)
            self.ax.plot(x, y, color=color, lw=2, zorder=2)

            mid = SegmentHelper.get_midpoint(seg)
            if mid:
                if view_map_mode:
                    mid = transformer_to_3857.transform(*mid)
                scatter = self.ax.scatter(mid[0], mid[1], color='purple', s=40, zorder=6, picker=5)
                self.mid_scatters.append((scatter, seg))
        self._draw_pi(view_map_mode)

    def _draw_pi(self, view_map_mode):
        # --- PI ---
        if view_map_mode:
            pi_pts = [transformer_to_3857.transform(pt.x, pt.y)
                      for pt in self.collection.coord_list]
        else:
            pi_pts = [(pt.x, pt.y) for pt in self.collection.coord_list]

        x, y = zip(*pi_pts)
        self.pi_scatter = self.ax.scatter(x, y, color='red', marker='x', s=60,
                                          zorder=6, picker=5)
        self.ax.plot(x, y, color='red', linestyle='--', lw=1, zorder=4)

        # --- PI 텍스트 ---
        for i, (px, py) in enumerate(pi_pts):
            if i == 0:
                label = "BP"
            elif i == len(pi_pts) - 1:
                label = "EP"
            else:
                label = f"IP.{i}"
            self.ax.text(px, py + 20, label, fontsize=9, ha='center', va='bottom',
                         bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))

        self.ax.set_aspect('equal', adjustable='datalim')
        self.ax.grid(False)

    def reset_view_to_data(self):
        """JSON LOAD 완료 시 데이터 전체 범위로 축 초기화"""
        if not self.collection.coord_list:
            return

        xs = [p.x for p in self.collection.coord_list]
        ys = [p.y for p in self.collection.coord_list]

        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        # update_plot 호출 시 force_xlim/ylim 전달
        self.update_plot(force_xlim=(x_min, x_max), force_ylim=(y_min, y_max))

    def update_map_zoom(self, view_map_mode=None):
        """현재 뷰 범위 기반으로 지도 타일만 다시 로드"""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        dx = xlim[1] - xlim[0]
        dy = ylim[1] - ylim[0]
        max_dim = max(dx, dy)

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