import struct
from .commands import DLCmd

fb = []


def readFile(binfile: str):
    global fb
    with open(binfile, "rb") as f:
        fb = f.read()


def readStruct(fmt: str, offset: int) -> list:
    global fb
    return struct.unpack_from(fmt, fb, offset)


class Command:
    def __init__(self, command: int, arg1: int, arg2: int, vec: list[float]):
        self.type = command
        self.arg1 = arg1
        self.arg2 = arg2
        self.vec = vec

    def __str__(self) -> str:
        return f"cmd {self.type}: ({self.arg1}, {self.arg2}) {self.vec}"


def readCMD(offset: int) -> Command:
    global fb
    argvals = struct.unpack_from(">LLLfff", fb, offset)
    return Command(
        argvals[0], argvals[1], argvals[2], [argvals[3], argvals[4], argvals[5]]
    )


def readDL(offset) -> list[Command]:
    print("Reading DL...")
    cmdList = [readCMD(offset)]
    offset += 24
    while cmdList[-1].type != DLCmd.EndList:
        cmdList.append(readCMD(offset))
        offset += 24
    return cmdList
