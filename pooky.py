#!/usr/bin/python

# Written by Andrew Wang.
# Turing complete translator for the Ook language, a BF variant.
#
# See http://www.dangermouse.net/esoteric/ook.html for more info.

import sys



def parse(raw):
    """Translates Ook into a more readable form."""
    a,b,c = "Ook.", "Ook?", "Ook!"
    elements = raw.split()
    raw_commands = [a+b, b+a, a+a, c+c, a+c, c+a, c+b, b+c]
    real_commands = ["next", "prev", "inc", "dec", "read",
                    "print", "j1", "j2"]

    translate = dict(zip(raw_commands, real_commands))

    for i in range(len(elements)/2):
        command = elements.pop(0) + elements.pop(0)
        yield translate[command]


class Ook:
    """Implements the Ook commands."""

    def __init__(self, raw):
        self.memory = [0]*15
        self.mp = 0
        self.commands = [x for x in parse(raw)]
        self.cp = 0

    def hasNext(self):
        if self.cp < len(self.commands):
            return True
        return False

    def next(self):
        cmd = self.commands[self.cp]
        Ook.__dict__["_"+cmd](self)
        self.cp += 1

    def _next(self):
        self.mp += 1

    def _prev(self):
        self.mp -= 1

    def _inc(self):
        self.memory[self.mp] += 1

    def _dec(self):
        self.memory[self.mp] -= 1

    def _read(self):
        print "In: ",
        c = raw_input()[0]
        self.memory[self.mp] = ord(c)

    def _print(self):
        sys.stdout.write(chr(self.memory[self.mp]))

    def _j1(self):
        if self.memory[self.mp] == 0:
            offset = self.commands[self.cp:].index("j2")
            self.cp += offset

    def _j2(self):
        if self.memory[self.mp] != 0:
            temp = self.commands[:self.cp+1]
            temp.reverse()
            offset = temp.index("j1")
            self.cp -= offset


def main():
    if len(sys.argv) < 2:
        print "Usage: pooky.py <filename>"
        sys.exit(0)

    o = Ook(open(sys.argv[1]).read())

    while o.hasNext():
        o.next()


if __name__ == "__main__":
    main()
