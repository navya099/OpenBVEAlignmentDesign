from ezdxf.addons.hpgl2.plotter import Plotter

from data.segment.segment_collection.segment_collection import SegmentCollection
from event.event_controller import EventController
from mid_edit.mid_editor import MidPointEditor
from ui.main_app_ui import SegmentVisualizer
from pi_edit.pi_editor import PIEditor

class AppController:
    def __init__(self):
        self.event_controller = EventController()
        self.collection = SegmentCollection()

        # UI 생성
        self.app = SegmentVisualizer(
            event_controller=self.event_controller,
            collection=self.collection,
        )

        # PIEditor 생성 및 연결

        self.pi_editor = PIEditor(
            collection=self.collection,
            events=self.event_controller)

        self.mid_editor = MidPointEditor()

    def run(self):
        self.app.mainloop()