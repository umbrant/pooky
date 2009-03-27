#!/usr/bin/python

# Written by Andrew Wang.
# Turing complete translator for the Ook language, a BF variant.
#
# See http://www.dangermouse.net/esoteric/ook.html for more info.

import sys
import cProfile



def parse(raw):
    """Translates Ook into a more readable form."""
    a,b,c = "Ook.", "Ook?", "Ook!"
    elements = raw.split()
    raw_commands = [a+b, b+a, a+a, c+c, a+c, c+a, c+b, b+c]
    real_commands = ["next", "prev", "inc", "dec", "read",
                    "print", "j1", "j2"]

    translate = dict(zip(raw_commands, real_commands))

    for i in xrange(len(elements)/2):
        command = elements.pop(0) + elements.pop(0)
        yield translate[command]


class Ook:
    """Implements the Ook commands."""

    def __init__(self, raw):
        self.memory = [0]*30000
        self.mp = 0
        self.commands = [x for x in parse(raw)]
        self.cp = 0
        # Cached j location, lookup
        self.j1 = {}
        self.j2 = {}

        # Populate the cache, make a pass through the input
        s = []
        for i, cmd in enumerate(self.commands):
            cmd = self.commands[i]
            if cmd is "j1":
                s.append(i)
            elif cmd is "j2":
                j1 = s.pop()
                self.j1[j1] = i

        self.j2 = dict(zip(self.j1.values(), self.j1.keys()))

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
        if self.memory[self.mp] > 255:
            self.memory[self.mp] = 0

    def _dec(self):
        self.memory[self.mp] -= 1
        if self.memory[self.mp] < 0:
            self.memory[self.mp] = 255

    def _read(self):
        print "In:",
        c = raw_input()
        if c:
            c = c[0]
            self.memory[self.mp] = ord(c)

    def _print(self):
        sys.stdout.write(chr(self.memory[self.mp]))
        #sys.stdout.flush()

    def _j1(self):
        if self.cp not in self.j1:
            offset = self.commands[self.cp:].index("j2")
            # Cache the j1 and j2 locations
            self.j1[self.cp] = self.cp + offset
            self.j2[self.cp+offset] = self.cp
        if self.memory[self.mp] == 0:
            # Skipping the loop, condition not met
            self.j1[self.cp]

    def _j2(self):
        if self.memory[self.mp] != 0:
            #temp = self.commands[:self.cp+1]
            #temp.reverse()
            #offset = temp.index("j1")
            #self.cp -= offset

            # Jump back to stored j1
            self.cp = self.j2[self.cp]


def main():
    if len(sys.argv) < 2:
        print "Usage: pooky.py <filename>"
        sys.exit(0)

    o = Ook(open(sys.argv[1]).read())

    print o.commands[:117]

    end = len(o.commands)
    while o.cp < end:
        o.next()


if __name__ == "__main__":
    cProfile.run("main()")
