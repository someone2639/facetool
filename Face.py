

class Face:
    def __init__(self):
        self.dynlists = {}
        self.vtxdatas = {}
        self.facedatas = {}
        self.animdatas = {}

        self.vtxinfos = {}
        self.faceinfos = {}
        self.animinfos = {}

    from .face_reader import __init__
    from .face_writer import export
