import os
import re
import struct

if __name__ != "__main__":
    from .commands import CommandToArguments, CommandToDLCmd, DLCmd
    from .Face import Face
else:
    from commands import CommandToArguments, CommandToDLCmd, DLCmd
    from Face import Face

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
    r"s16\sanim_(\w+)\[\]\[(\d+)\]": "animdata2",
    r"struct\sAnimDataInfo\sanim_(\w+)": "animinfo",
    r"s16\sverts_(\w+)\[\]\[(\d+)\]": "vtxdata",
    r"s16\s(\w+)_VtxData\[\]\[(\d+)\]": "vtxdata2",
    r"struct\sGdVtxData\s(\w+)": "vtxinfo",
    r"u16\sfacedata_(\w+)\[\]\[(\d+)\]": "facedata",
    r"u16\s(\w+)_FaceData\[\]\[(\d+)\]": "facedata2",
    r"struct\sGdFaceData\s(\w+)": "faceinfo",
    r"struct\sDynList\s(\w+)\[": "dynlist",
}

def findEndLine(data: list[str], startline: int) -> int:
    for i, line in enumerate(data[startline:]):
        if line.strip() == "};":
            return startline + i
    return -1

class Command:
    def __init__(self, cmdname: DLCmd, arg1, arg2, vec: list[float]):
        self.type = cmdname
        self.arg1 = arg1
        self.arg2 = arg2
        self.vec = vec

    def __init__(self, cmdname: DLCmd, argspec: dict[str, bool], args: list[str] = None):
        self.type = cmdname
        self.arg1 = 0
        self.arg2 = 0
        self.vec = [0,0,0]
        if "vec" in argspec:
            baseIdx = argspec["vec"]
            self.vec = [float(args[baseIdx]), float(args[baseIdx + 1]), float(args[baseIdx + 2])]
        if "float1" in argspec:
            self.vec = [float(args[argspec["float1"]]), 0, 0]
        if "arg1" in argspec:
            self.arg1 = args[argspec["arg1"]]
        if "arg2" in argspec:
            self.arg2 = args[argspec["arg2"]]



    def __str__(self):
        return f"cmd {self.type}: ({self.arg1}, {self.arg2}) {self.vec}"
    def __repr__(self):
        return f"Command({self.type}, ({self.arg1}, {self.arg2}) {self.vec})"

def parseDynlist(data: list[str], startline: int) -> list[Command]:
    cmd_list = [i.strip() for i in data[startline:findEndLine(data, startline)]]
    ret_commands = []

    for cmd in cmd_list:
        tokens = cmd.replace("(", " ").replace(")", " ").replace(",", " ").split()
        if len(tokens) > 0 and tokens[0] in CommandToDLCmd.keys():
            cmdname = tokens[0]
            cmdtype = CommandToDLCmd[cmdname]
            cmdargs = CommandToArguments[cmdname]
            ret_commands.append(Command(cmdtype, cmdargs, tokens[1:]))

    return ret_commands

def parseData(data: list[str], startline: int, datawidth: int) -> list[list[float]]:
    retvalues = []

    for parsedline in data[startline:findEndLine(data, startline)]:
        values = [int(i) for i in 
            parsedline.replace(",", " ").replace("{", " ").replace("}", " ").split()
        ]
        retvalues += [
            values[i : i + datawidth] for i in range(0, len(values), datawidth)
        ]

    return retvalues

def parseInfo(data: list[str], startline: int, num_lines: int):
    datapattern = r"ARRAY_COUNT\((\w+)\),\s(\w+),\s(\w+)"
    retinfo = []

    for i in range(num_lines):
        match = re.search(datapattern, data[startline + i])
        if match:
            retinfo += [match.groups()]
    return retinfo

def parseAnimInfo(data: list[str], startline: int):
    datapattern = r"ARRAY_COUNT\((\w+)\),\s(\w+),\s(\w+)"
    datapattern2 = r"0,\sGD_ANIM_EMPTY,\sNULL"
    retinfo = []
    num_lines = findEndLine(data, startline) - startline

    for i in range(num_lines):
        match = re.search(datapattern, data[startline + i])
        if match:
            retinfo += [match.groups()]
        match = re.search(datapattern2, data[startline + i])
        if match:
            retinfo += [["0", "GD_ANIM_EMPTY", "NULL"]]
    return retinfo

def parseAllDynLists():
    for filename in fbl:
        file = fbl[filename]
        for i, line in enumerate(file):
            for reg in regexes:
                match = re.search(reg, line)
                if match:
                    params = match.groups()

                    match regexes[reg]:
                        case "vtxinfo":
                            vtxinfos[params[0]] = parseInfo(file, i, 1)[0]
                            # if len(vtxinfos[params[0]]) > 1:
                            #     vtxinfos[params[0]] = vtxinfos[params[0]][0]
                        case "faceinfo":
                            faceinfos[params[0]] = parseInfo(file, i, 1)[0]
                        case "animinfo":
                            animinfos[f"anim_{params[0]}"] = parseAnimInfo(file, i)
                        case "vtxdata":
                            vtxdatas[f"verts_{params[0]}"] = parseData(file, i + 1, 3)
                        case "vtxdata2":
                            vtxdatas[f"{params[0]}_VtxData"] = parseData(file, i + 1, 3)
                        case "facedata":
                            facedatas[f"facedata_{params[0]}"] = parseData(file, i + 1, 4)
                        case "facedata2":
                            facedatas[f"{params[0]}_FaceData"] = parseData(file, i + 1, 4)
                        case "animdata":
                            animdatas[f"animdata_{params[0]}"] = parseData(file, i + 1, int(params[1]))
                        case "animdata2":
                            animdatas[f"anim_{params[0]}"] = parseData(file, i + 1, int(params[1]))
                        case "dynlist":
                            dynlists[params[0]] = parseDynlist(file, i)
    return Face(
        dynlists,
        vtxdatas,
        facedatas,
        animdatas,
        vtxinfos,
        faceinfos,
        animinfos
    )


def readDynLists(folder_path: str):
    global fbl
    for _, _, files in os.walk(folder_path):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext != ".c":
                continue

            with open(f"{folder_path}/{file}", "r") as f:
                fbl[file] = f.readlines()


def readStruct(fmt, offset):
    return struct.unpack_from(fmt, fb, offset)

def readCMD(offset):
    argvals = struct.unpack_from(">LLLfff", fb, offset)
    return Command(
        argvals[0], argvals[1], argvals[2], [argvals[3], argvals[4], argvals[5]]
    )


def readDL(name):
    print("Reading DL...")
    cmdList = dynlists[name]
    name += 24
    while cmdList[-1].type != DLCmd.EndList:
        cmdList.append(readCMD(name))
        name += 24
    return cmdList


if __name__ == "__main__":
    import sys

    readDynLists(sys.argv[1])
    parseAllDynLists()
    print(animdatas)
