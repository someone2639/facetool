import os
import struct
import re

if __name__ != "__main__":
    from .commands import DLCmd

dynlists = {}
vtxdatas = {}
facedatas = {}
animdatas = {}

vtxinfos = {}
faceinfos = {}
animinfos = {}

fbl = {}

regexes: dict[str, str] = {
    r"s16\sanimdata_(\w+)\[\]\[(\d+)\]": "animdata",
    r"struct\sAnimDataInfo\sanim_(\w+)": "animinfo",
    r"s16\sverts_\[\]\[(\d+)\]": "vtxdata",
    r"struct\sGdVtxData\svtx_(\w+)": "vtxinfo",
    r"u16\sfacedata_(\w+)\[\]\[(\d+)\]": "facedata",
    r"struct\sGdFaceData\rfaces_(\w+)": "faceinfo",

    r"struct\sDynList\sdynlist_(\w+)": "dynlist",
}

def parseAllDynLists():
    for filename in fbl:
        file = fbl[filename]
        for line in file:
            for reg in regexes:
                match = re.search(reg, line)
                if match:
                    print(f"foudn {regexes[reg]}, groups: ", match.groups())


def readDynLists(folder_path: str):
    global fbl
    for _, _, files in os.walk(folder_path):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext != ".c":
                continue

            print(f"found file {file}")
            with open(f"{folder_path}/{file}", "r") as f:
                fbl[file] = f.readlines()


def readStruct(fmt, offset):
    global fb
    return struct.unpack_from(fmt, fb, offset)


class Command:
    def __init__(self, thetype, arg1, arg2, vec):
        self.type = thetype
        self.arg1 = arg1
        self.arg2 = arg2
        self.vec = vec

    def __str__(self):
        return f"cmd {self.type}: ({self.arg1}, {self.arg2}) {self.vec}"


def readCMD(offset):
    global fb
    argvals = struct.unpack_from(">LLLfff", fb, offset)
    return Command(
        argvals[0], argvals[1], argvals[2], [argvals[3], argvals[4], argvals[5]]
    )


def readDL(name):
    global dynlists
    print("Reading DL...")
    cmdList = dynlists[name]
    name += 24
    while cmdList[-1].type != DLCmd.EndList:
        cmdList.append(readCMD(name))
        name += 24
    return cmdList

if __name__ == '__main__':
    import sys
    readDynLists(sys.argv[1])
    parseAllDynLists()
