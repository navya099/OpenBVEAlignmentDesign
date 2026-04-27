from app_con.cuve_controllr import CurveController
from app_con.file_controller import FileController
from app_con.mp_controller import MidPointController
from app_con.pi_controller import PIController
from curve_edit.curve_editor import CurveEditor
from data.segment.segment_collection import SegmentCollection
from event.event_controller import EventController
from mid_edit.mid_editor import MidPointEditor
from seg_edit.segment_editor import SegmentCollectionEditor
from ui.main_app_ui import SegmentVisualizer
from pi_edit.pi_editor import PIEditor

class AppController:
    def __init__(self):
        self.event_controller = EventController()
        self.collection = SegmentCollection()

        # UI 생성
        self.app = SegmentVisualizer(
            controller=self,
            collection=self.collection,
        )
        #메인 플로터 연결
        # 2. 플로터 생성 및 장착 (비즈니스 로직과 UI를 연결하는 시점)
        from plotter.matplotter import Matplotter
        self.app.setup_plotter(Matplotter, self.event_controller)

        # PIEditor 생성 및 연결

        self.pi_editor = PIEditor(
            collection=self.collection,
            events=self.event_controller)

        self.mid_editor = MidPointEditor(collection=self.collection, events=self.event_controller)

        self.collection_editor = SegmentCollectionEditor(
            segmentcollection=self.collection,
            events=self.event_controller
        )
        self.curve_editor = CurveEditor(collection=self.collection, events=self.event_controller)

        #컨트롤러 연결
        self.curve_ctrl = CurveController(self.app, self.event_controller)
        self.pi_ctrl = PIController(self.app, self.event_controller)
        self.mid_ctrl = MidPointController(self.app, self.event_controller)
        self.file_ctrl = FileController(self.app, self.event_controller)

    def run(self):
        self.app.mainloop()

