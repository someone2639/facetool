import os
import re
import struct

if __name__ != "__main__":
    from .commands import DLCmd, CommandToDLCmd, CommandToArguments
else:
    from commands import DLCmd, CommandToDLCmd, CommandToArguments

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
    r"s16\sverts_(\w+)\[\]\[(\d+)\]": "vtxdata",
    r"struct\sGdVtxData\svtx_(\w+)": "vtxinfo",
    r"u16\sfacedata_(\w+)\[\]\[(\d+)\]": "facedata",
    r"struct\sGdFaceData\sfaces_(\w+)": "faceinfo",
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
            self.vec = [args[argspec["float1"]], 0, 0]
        if "arg1" in argspec:
            self.vec = args[argspec["arg1"]]
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
        values = (
            parsedline.replace(",", " ").replace("{", " ").replace("}", " ").split()
        )
        retvalues += [
            values[i : i + datawidth] for i in range(0, len(values), datawidth)
        ]

    return retvalues

def parseAllDynLists():
    for filename in fbl.keys():
        file = fbl[filename]
        for i, line in enumerate(file):
            for reg in regexes.keys():
                match = re.search(reg, line)
                if match:
                    params = match.groups()

                    match regexes[reg]:
                        case "vtxinfo":
                            datapattern = r"ARRAY_COUNT\((\w+)\),\s(\w+),\s(\w+)"
                            match2 = re.search(datapattern, line)
                            vtxinfos[f"vtx_{params[0]}"] = match2.groups()[0]
                        case "faceinfo":
                            datapattern = r"ARRAY_COUNT\((\w+)\),\s(\w+),\s(\w+)"
                            match2 = re.search(datapattern, line)
                            faceinfos[f"faces_{params[0]}"] = match2.groups()[0]
                        case "vtxdata":
                            vtxdatas[f"verts_{params[0]}"] = parseData(file, i + 1, 3)
                        case "facedata":
                            facedatas[f"facedata_{params[0]}"] = parseData(file, i + 1, 4)
                        case "dynlist":
                            dynlists[params[0]] = parseDynlist(file, i + 1)


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
    print(dynlists)
