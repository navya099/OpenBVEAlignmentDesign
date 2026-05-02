import json
from utils.coordinate_utils import convert_coordinates
from myalignment.segment.segment_helper import SegmentHelper

class MapPlotter:
    def __init__(self, events, collection, bridge=None): # master(AppController/UI) 추가
        self.events = events
        self.collection = collection
        self.bridge = bridge  # dragging_index 확인을 위해 필요
        self.webview_window = None

        if self.events:
            full_update_events = [
                'pi_added_finish', 'pi_removed_finish', 'pi_changed_finish',
                'reset_to_initial_finish', 'curve_added_finish',
                'curve_changed_finish', 'curve_removed_finish',
                'pi_dragged_finish', 'midpoint_dragged_finish',
                'load_from_json_finish'
            ]
            for event in full_update_events:
                self.events.bind(event, self.update_plot)

            self.events.bind('pi_dragging', self.update_segments_only)

    def set_window(self, window):
        self.webview_window = window

    # map_plotter.py

    def update_plot(self, *args, **kwargs):
        if not self.webview_window or self.bridge.dragging_index is not None:
            return

        import time
        t0 = time.perf_counter()

        # 1. PI 마커 및 PI 보조선 (BP -> IP -> EP 점선)
        pi_list = []
        raw_pi_coords = []  # 보조선용
        for i, p in enumerate(self.collection.coord_list):
            coord = convert_coordinates([p.x, p.y], 5186, 4326)
            lat, lng = coord[1], coord[0]
            label = "BP" if i == 0 else ("EP" if i == len(self.collection.coord_list) - 1 else f"IP.{i}")
            pi_list.append({'index': i, 'lat': lat, 'lng': lng, 'label': label})
            raw_pi_coords.append([lat, lng])

        # 2. 곡선 세그먼트 및 Midpoint
        segments_list = []
        midpoints_list = []
        for i, seg in enumerate(self.collection.segment_list):
            # 선형(Path) 추출
            points = SegmentHelper.segment_to_xy(seg)
            path = [[lat, lng] for lng, lat in (convert_coordinates(pt, 5186, 4326) for pt in points)]
            segments_list.append({'path': path, 'color': SegmentHelper.get_color(seg)})

            # 중간점(Midpoint) 추출
            mid = SegmentHelper.get_midpoint(seg)
            if mid:
                m_coord = convert_coordinates(mid, 5186, 4326)
                midpoints_list.append({'index': i, 'lat': m_coord[1], 'lng': m_coord[0]})

        # 최종 페이로드 구성
        payload = json.dumps({
            'pi': pi_list,
            'pi_line': raw_pi_coords,  # PI끼리 연결하는 빨간 점선
            'segments': segments_list,
            'midpoints': midpoints_list
        })

        t1 = time.perf_counter()
        self.webview_window.evaluate_js(f"window.renderAll({payload})")
        print(f"  데이터 준비: {(t1 - t0) * 1000:.1f}ms")

    def update_segments_only(self, *args, **kwargs):
        """드래그 시 노란색 점선으로 곡선만 빠르게 업데이트 (마커 건드리지 않음)"""
        if not self.webview_window:
            return

        segments_list = []
        for seg in self.collection.segment_list:
            points = SegmentHelper.segment_to_xy(seg)
            path = [[lat, lng] for lng, lat in (convert_coordinates(pt, 5186, 4326) for pt in points)]
            segments_list.append({'path': path})

        # JS의 updatePathsOnly가 기대하는 구조 {'segments': ...} 로 맞춰서 보냄
        payload = json.dumps({'segments': segments_list})
        self.webview_window.evaluate_js(f"window.updatePathsOnly({payload})")