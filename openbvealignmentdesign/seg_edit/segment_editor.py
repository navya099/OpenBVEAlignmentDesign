from file_io_module.json_module import JsonFileIO


class SegmentCollectionEditor:
    def __init__(self, segmentcollection, events=None):
        self.collection = segmentcollection
        self.events = events

        if self.events:
            self.events.bind('save_to_json', self.on_save_to_json)
            self.events.bind('load_from_json', self.on_load_from_json)
    # SegmentCollection 또는 Controller
    def on_save_to_json(self, save_path):
        try:
            JsonFileIO.save_json(save_path, self.collection.coord_list, self.collection.radius_list)
        except Exception as e:
            raise e

    def on_load_from_json(self, load_path):
        try:
            coord_list, radius_list = JsonFileIO.load_json(load_path)
            self.collection.create_by_pi_coords(coord_list, radius_list)
        except Exception as e:
            raise e