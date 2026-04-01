from AutoCAD.point2d import Point2d


class PIEditor:
    """PI편집 클래스"""
    def __init__(self,collection=None, events=None):
        self.events = events
        self.collection = collection

        if self.events:
            self.events.bind('pi_removed', self.remove_pi)
            self.events.bind('pi_added', self.add_pi)

    def add_pi(self, coord):
        """마우스 클릭으로 PI 추가"""
        try:
            self.collection.add_pi_by_coord(coord)
        except Exception as e:
            raise e

    def remove_pi(self, is_only_remove_curve, idx):
        """PI삭제"""
        try:
            if is_only_remove_curve:
                self.collection.remove_curve_at_pi_by_index(idx)
            else:
                self.collection.remove_pi_at_index(idx)
        except Exception as e:
            raise e
