import struct

fb = []

def readFile():
    global fb
    with open("/home/faris/Devel/goddard/gd.bin", "rb") as f:
        fb = f.read()

def readStruct(fmt, offset):
    global fb
    return struct.unpack_from(fmt, fb, offset)

class Command():
    def __init__(self, type, arg1, arg2, vec):
        self.type = type
        self.arg1 = arg1
        self.arg2 = arg2
        self.vec = vec
    def __str__(self):
        return f"cmd {self.type}: ({self.arg1}, {self.arg2}) {self.vec}"

def readCMD(offset):
    global fb
    argvals = struct.unpack_from(">LLLfff", fb, offset)
    return Command(
        argvals[0],
        argvals[1],
        argvals[2],
        [ argvals[3], argvals[4], argvals[5] ]
    )

def readDL(offset):
    print("Reading DL...")
    cmdList = [readCMD(offset)]
    offset += 24
    while cmdList[-1].type != 58:
        cmdList.append(readCMD(offset))
        offset += 24
    return cmdList
