# curve_editor.py
class CurveEditor:
    """곡선 편집 클래스"""
    def __init__(self, collection=None, events=None):
        self.collection = collection
        self.events = events

        if self.events:
            self.events.bind('curve_added', self.add_curve)
            self.events.bind('curve_removed', self.remove_curve)
            self.events.bind('curve_updated', self.update_curve)

    def add_curve(self, idx, radius):
        """PI에 곡선 반경 추가"""
        try:
            self.collection.update_curve(index=idx, radius=radius)
        except Exception as e:
            raise e

    def remove_curve(self, idx):
        """PI에서 곡선 반경 제거"""
        try:
            self.collection.update_curve(index=idx, radius=None)
        except Exception as e:
            raise e

    def update_curve(self, idx, radius):
        """PI의 곡선 반경 수정"""
        try:
            self.collection.update_curve(index=idx, radius=radius)
        except Exception as e:
            raise e