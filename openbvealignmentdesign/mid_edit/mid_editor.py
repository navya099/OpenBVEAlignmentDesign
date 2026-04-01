from data.alignment.exception.alignment_error import GroupNullError
from transaction import Transaction
import math

class MidPointEditor:
    def __init__(self, collection=None, events=None):
        self.collection = collection
        self.events = events
        if self.events:
            self.events.bind('midpoint_dragged', self.drag_midpoint)

    def drag_midpoint(self, seg, new_mid):
        """중간점 드래그 처리"""
        group = None
        idx = seg.current_index
        for gr in self.collection.groups:
            if gr:
                for sg in gr.segments:
                    if sg.current_index == idx:
                        group = gr
                        break
            if group:
                break
        if group is None:
            raise GroupNullError(group)

        gr_indx = group.group_id
        current_pi = self.collection.coord_list[gr_indx]

        # 새 반경 계산
        new_e = current_pi.distance_to(new_mid)

        new_r = new_e / (1 / math.cos(group.internal_angle / 2) - 1)

        with Transaction(self.collection):
            self.collection.update_radius_by_index(new_r, gr_indx)