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
            self.events.bind('reset_to_initial', self.reset)

    def update_pi(self, point, index):
        """마우스 클릭으로 PI 갱신"""
        try:
            if index != 0 and index != len(self.collection.coord_list) - 1:
                self.collection.update_pi(pipoint=point, index=index)
            else:
                self.collection.update_bp_ep(index=index, point=point)
        except Exception as e:
            raise e

    def add_pi(self, coord):
        """마우스 클릭으로 PI 추가"""
        try:
            self.collection.add_pi(pipoint=coord)
        except Exception as e:
            raise e

    def remove_pi(self, idx):
        """PI삭제"""
        try:
            self.collection.remove_pi(idx)
        except Exception as e:
            raise e

    def reset(self):
        """모든 PI삭제(초기화)"""
        try:
            self.collection.reset()
        except Exception as e:
            raise e