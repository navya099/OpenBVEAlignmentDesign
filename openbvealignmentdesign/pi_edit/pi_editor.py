from AutoCAD.point2d import Point2d


class PIEditor:
    """PI편집 클래스"""
    def __init__(self,collection=None, events=None):
        self.events = events
        self.collection = collection

        if self.events:
            self.events.bind('pi_dragged', self.update_pi)
            self.events.bind('pi_removed', self.remove_pi)
            self.events.bind('pi_added', self.add_pi)

    def update_pi(self, point, index):
        """마우스 클릭으로 PI 갱신"""
        try:
            if index != 0 and index != len(self.collection.coord_list) - 1:
                self.collection.update_pi_and_radius_by_index(pipoint=point, radius=None, index=index)
            else:
                self.collection.update_bp_ep(index=index, point=point)
        except Exception as e:
            raise e

    def add_pi(self, coord, radius):
        """마우스 클릭으로 PI 추가"""
        try:
            self.collection.add_pi(pipoint=coord, radius=radius)
        except Exception as e:
            raise e

    def remove_pi(self, is_only_remove_curve, idx):
        """PI삭제"""
        try:
            if is_only_remove_curve:
                self.collection.update_pi_and_radius_by_index(idx)
            else:
                self.collection.update_pi_and_radius_by_index(idx)
        except Exception as e:
            raise e
