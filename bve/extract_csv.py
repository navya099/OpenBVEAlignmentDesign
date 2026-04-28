from bve.base_txt import create_base_txt
from bve.extract_horizon import extract_horizon


def save_bve(segment_list):
    """BVE로 저장"""
    lines = []
    lines.extend(extract_horizon(segment_list))
    txt = '\n'.join(lines)
    with open("c:/temp/평면선형.txt", "w", encoding="utf-8") as f:
        f.write(txt)