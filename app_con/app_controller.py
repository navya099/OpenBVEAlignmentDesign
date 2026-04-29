import threading
import os
import webview
from app_con.cuve_controllr import CurveController
from app_con.file_controller import FileController
from app_con.mp_controller import MidPointController
from app_con.pi_controller import PIController
from app_con.view_controller import ViewController
from curve_edit.curve_editor import CurveEditor
from data.segment.segment_collection import SegmentCollection
from event.event_controller import EventController
from map.map_bridge import MapBridge
from mid_edit.mid_editor import MidPointEditor
from plotter.matplotter import MapPlotter
from seg_edit.segment_editor import SegmentCollectionEditor
from ui.main_app_ui import SegmentVisualizer
from pi_edit.pi_editor import PIEditor

class AppController:
    def __init__(self):
        self.ploter = None
        self.map_bridge = None
        self._map_window = None
        self.event_controller = EventController()
        self.collection = SegmentCollection()
        self._initialize_editors()
        """
        #메인 플로터 연결
        # 2. 플로터 생성 및 장착 (비즈니스 로직과 UI를 연결하는 시점)
        from plotter.matplotter import Matplotter
        self.app.setup_plotter(Matplotter, self.event_controller)
        """


    def _initialize_editors(self):
        """Editor 생성 및 연결"""
        self.pi_editor = PIEditor(
            collection=self.collection,
            events=self.event_controller)

        self.mid_editor = MidPointEditor(collection=self.collection, events=self.event_controller)

        self.collection_editor = SegmentCollectionEditor(
            segmentcollection=self.collection,
            events=self.event_controller
        )
        self.curve_editor = CurveEditor(collection=self.collection, events=self.event_controller)

    def _initialize_controllers(self):
        """컨트롤러 연결"""
        self.curve_ctrl = CurveController(self.app, self.event_controller)
        self.pi_ctrl = PIController(self.app, self.event_controller)
        self.mid_ctrl = MidPointController(self.app, self.event_controller)
        self.file_ctrl = FileController(self.app, self.event_controller)
        self.view_ctrl = ViewController(self.app, self.event_controller)

    def _run_tkinter_thread(self):
        """보조 스레드 내부에서 Tkinter를 생성하고 실행"""
        # 이 스레드 안에서 생성해야 '주인'이 이 스레드가 됩니다.


        self.app = SegmentVisualizer(
            controller=self,
            collection=self.collection,
        )

        # 나머지 컨트롤러 연결 로직도 여기서 수행 (self.app이 필요하므로)
        self._initialize_controllers()

        print("Tkinter UI가 준비되었습니다.")
        self.app.mainloop()

    def run(self):
        # 1. Tkinter 시작
        tk_thread = threading.Thread(target=self._run_tkinter_thread, daemon=True)
        tk_thread.start()

        # 2. Bridge 생성 (초기화 시 self를 넘기지 않음)
        self.map_bridge = MapBridge()

        # 3. WebView 창 생성 (이 시점에 pywebview가 Bridge를 스캔함 - 안전함)
        self._map_window = webview.create_window(
            'Alignment Map View',
            url='assets/map.html',
            js_api=self.map_bridge,
            width=1000, height=800
        )

        # 4. 분석이 끝난 후, 필요한 참조를 '후주입'함
        # MapBridge 내부에서 self._controller와 같이 언더바를 붙여서 관리해야 안전합니다.
        self.map_bridge.init_with_app(self, self._map_window)
        self.ploter = MapPlotter(self.event_controller, collection=self.collection, bridge=self.map_bridge)
        self.ploter.set_window(self._map_window)
        print("WebView를 메인 스레드에서 시작합니다...")
        webview.start(debug=True)

