import json
from coordinate_utils import convert_coordinates
from data.segment.segment_helper import SegmentHelper

class MapPlotter:
    def __init__(self, events, collection, master=None): # master(AppController/UI) 추가
        self.events = events
        self.collection = collection
        self.master = master  # dragging_index 확인을 위해 필요
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

    def update_plot(self, *args, **kwargs):
        """전체 데이터를 지도로 배달 (마커 재생성 포함)"""
        if not self.webview_window:
            return

        # [핵심 추가] 드래그 중에는 전체 갱신(renderAll)을 절대 하지 않음!
        # 마커가 새로 그려지는 순간 드래그 이벤트 연결이 끊어집니다.
        if self.master and hasattr(self.master, 'dragging_index'):
            if self.master.dragging_index is not None:
                return

        pi_list = []
        for i, p in enumerate(self.collection.coord_list):
            coord = convert_coordinates([p.x, p.y], 5186, 4326)
            pi_list.append({'index': i, 'lat': coord[1], 'lng': coord[0]})

        segments_list = []
        for seg in self.collection.segment_list:
            points = SegmentHelper.segment_to_xy(seg)
            path = [[lat, lng] for lng, lat in (convert_coordinates(pt, 5186, 4326) for pt in points)]
            segments_list.append({'path': path, 'color': 'red'})

        payload = json.dumps({'pi': pi_list, 'segments': segments_list})
        self.webview_window.evaluate_js(f"window.renderAll({payload})")

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