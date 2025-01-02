# need to store nets so that i can properly handle the behavior
#  of Type 3 nets (position copied to its attached joint)

class Net:
    def __init__(self, name):
        self.name = name
        self.type = 0
        self.shape = 0
        self.bone = None
        self.mesh = None
