import json

from AutoCAD.point2d import Point2d


class JsonFileIO:
    @staticmethod
    def save_json(save_path, coord_list, radius_list):
        """현재 SegmentCollection을 JSON으로 저장"""
        data = []
        for idx, (pt, r) in enumerate(zip(coord_list, radius_list)):
            data.append({
                "pi_index": idx,
                "pi_coord": [pt.x, pt.y],
                "radius": r
            })
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_json(open_file_path):
        """JSON 파일을 읽어서 coord_list, radius_list 반환"""
        with open(open_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        coord_list = [Point2d(x, y) for x, y in (item["pi_coord"] for item in data)]
        radius_list = [item.get("radius") for item in data]
        return coord_list, radius_list
