from AutoCAD.point2d import Point2d
from data.segment.segment_collection import SegmentCollection
from data.segment.segment_helper import SegmentHelper
import matplotlib.pyplot as plt

def run_real_group_test_case(name, coords, radii):
    print(f"\n=== Real Group Test Case: {name} ===")
    cl = SegmentCollection()

    cl.create_by_pi_coords(coords, radii)
    for seg in cl.segment_list:
        start = seg.start_coord
        end = seg.end_coord
        print(f"{seg.__class__.__name__} {seg.current_index}: "
              f"({start.x:.2f},{start.y:.2f}) -> ({end.x:.2f},{end.y:.2f}), "
              f"STA {seg.start_sta:.2f}-{seg.end_sta:.2f}, length={seg.length:.2f}")
    return cl


def visualize_multiple_cases(cases):
    n = len(cases)
    cols = 3
    import math
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(12, 6 * rows))
    axes = axes.flatten()
    for i, (name, segment_list) in enumerate(cases):
        ax = axes[i]
        for seg in segment_list:
            if seg.__class__.__name__ == "StraightSegment":
                xs = [seg.start_coord.x, seg.end_coord.x]
                ys = [seg.start_coord.y, seg.end_coord.y]
                ax.plot(xs, ys, 'b-', label="Straight" if "Straight" not in ax.get_legend_handles_labels()[1] else "")
            elif seg.__class__.__name__ == "CurveSegment":
                curve_points = SegmentHelper.segment_to_xy(seg)
                xs = [p[0] for p in curve_points]
                ys = [p[1] for p in curve_points]
                ax.plot(xs, ys, 'r-', label="Curve" if "Curve" not in ax.get_legend_handles_labels()[1] else "")
        ax.set_title(name)
        ax.set_aspect('equal', adjustable='box')
        ax.legend()

    # 남는 subplot은 숨기기
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()


def test_add_pi():
    # 초기 BP–PI1–PI2–EP
    bp = Point2d(198322.295865, 551717.440486)
    pi1 = Point2d(198989.169204, 548303.499112)
    pi2 = Point2d(202935.041692, 545189.094109)
    ep = Point2d(199139.705729, 536601.555990)

    # SegmentCollection 초기화
    cl = SegmentCollection()
    cl.create_by_pi_coords([bp, pi1, pi2, ep],[None, None, None, None])

    # 추천 좌표들
    pi_bp_side = Point2d(198500, 550000)
    pi_middle = Point2d(200500, 546500)
    pi_before_ep = Point2d(201500, 539000)
    pi_ep_side = Point2d(199200, 537000)

    test_points = [
        ("BP 바로 뒤", pi_bp_side),
        ("중간 (PI1–PI2)", pi_middle),
        ("PI2–EP 사이", pi_before_ep),
        ("EP 바로 앞", pi_ep_side),
    ]
    cl_temps = []
    for name, pt in test_points:
        print(f"\n=== add_pi 테스트: {name} ===")
        import copy
        cl_temp = copy.deepcopy(cl)
        cl_temp.add_pi(pt, radius=None)
        cl_temp.create_by_pi_coords(cl_temp.coord_list, cl_temp.radius_list)
        cl_temps.append(cl_temp)
        for i, c in enumerate(cl_temp.coord_list):
            print(f"PI{i}: ({c.x:.2f}, {c.y:.2f})")

        for seg in cl_temp.segment_list:
            print(f"{seg.__class__.__name__}: "
                  f"({seg.start_coord.x:.2f},{seg.start_coord.y:.2f}) -> "
                  f"({seg.end_coord.x:.2f},{seg.end_coord.y:.2f}), length={seg.length:.2f}")
    return cl_temps

# 좌표 예시
bp = Point2d(198322.295865,551717.440486)
pi1 = Point2d(198989.169204,548303.499112)
pi2 = Point2d(202935.041692,545189.094109)
pi3 = Point2d(202128.99422160457, 540887.2039212119)
ep = Point2d(199139.705729,536601.555990)

# 반경 리스트 (None이면 직선, 값 있으면 곡선 그룹 생성)
radii_case1 = [None, None, None, None, None]   # bp-pi-pi-pi-ep
radii_case2 = [None, None, 1200, None, None]   # bp-pi-gr-pi-ep
radii_case3 = [None, 1200, 1200, 1200, None]   # bp-gr-gr-gr-ep
radii_case4 = [None, 1200, None, 1200, None]   # bp-gr-pi-gr-ep

# 실행
case1 = run_real_group_test_case("bp-pi-pi-pi-ep", [bp, pi1, pi2, pi3, ep], radii_case1)
case2 = run_real_group_test_case("bp-pi-gr-pi-ep", [bp, pi1, pi2, pi3, ep], radii_case2)
case3 = run_real_group_test_case("bp-gr-gr-gr-ep", [bp, pi1, pi2, pi3, ep], radii_case3)
case4 = run_real_group_test_case("bp-gr-pi-gr-ep", [bp, pi1, pi2, pi3, ep], radii_case4)
#add_pi 테스트
clss = test_add_pi()

visualize_multiple_cases([
    ("bp-pi-pi-pi-ep", case1.segment_list),
    ("bp-pi-gr-pi-ep", case2.segment_list),
    ("bp-gr-gr-gr-ep", case3.segment_list),
    ("bp-gr-pi-gr-ep", case4.segment_list),
])

visualize_multiple_cases([
    ("BP 바로 뒤", clss[0].segment_list),
    ("중간 (PI1–PI2)", clss[1].segment_list),
    ("PI2–EP 사이", clss[2].segment_list),
    ("EP 바로 앞", clss[3].segment_list),
])


