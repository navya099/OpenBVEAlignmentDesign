# coordinate_utils.py
import pyproj
from functools import lru_cache

@lru_cache(maxsize=8)
def _get_transformer(src: int, target: int):
    """Transformer 객체 캐싱 - 매 호출마다 재생성 방지"""
    return pyproj.Transformer.from_crs(src, target, always_xy=True)

def convert_coordinates(coords, src: int, target: int):
    """
    좌표 변환 (단일 또는 리스트/튜플)

    Args:
        coords: (x, y) 또는 [(x1, y1), (x2, y2), ...]
        src: 소스 EPSG
        target: 타겟 EPSG
    Returns:
        tuple 또는 list[tuple]
    """
    transformer = _get_transformer(src, target)  # ✅ 캐시에서 꺼냄

    # 단일 좌표
    if isinstance(coords[0], (int, float)):
        return transformer.transform(coords[0], coords[1])

    # ✅ 배치 변환 - 루프 없이 한번에 처리
    xs, ys = zip(*coords)
    result_xs, result_ys = transformer.transform(xs, ys)
    return list(zip(result_xs, result_ys))