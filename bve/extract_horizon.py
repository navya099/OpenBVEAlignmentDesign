from curvedirection import CurveDirection
from data.segment.curve_segment import CurveSegment


def extract_horizon(segment_list):
    """BVE 수평선형(.bve) 텍스트 추출"""
    csv_txt = []
    for seg in segment_list:
        if isinstance(seg, CurveSegment):
            if seg.direction == CurveDirection.LEFT:
                text = f'{seg.start_sta:.2f},.CURVE -{seg.radius};\n'
                text2 = f'{seg.end_sta:.2f},.CURVE 0;\n'
            else:
                text = f'{seg.start_sta:.2f},.CURVE {seg.radius};\n'
                text2 = f'{seg.end_sta:.2f},.CURVE 0;\n'

            csv_txt.append(text)
            csv_txt.append(text2)

    return csv_txt