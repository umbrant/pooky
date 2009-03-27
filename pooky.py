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
    real_commands = ["n", "p", "i", "d", "r",
                    "w", "(", ")"]

    translate = dict(zip(raw_commands, real_commands))

    for i in xrange(len(elements)/2):
        command = elements.pop(0) + elements.pop(0)
        yield translate[command]


def main():
    if len(sys.argv) < 2:
        print "Usage: pooky.py <filename>"
        sys.exit(0)

    # Initialize
    memory = [0]*30000
    mp = 0
    raw = open(sys.argv[1], "r").readlines()

    # Look for "stdin" as the last line
    stdin = ""
    if raw[-1][0] == "!":
        stdin = raw[-1][1:]
        raw = raw[:-1]

    commands = [x for x in parse("".join(raw))]
    cp = 0
    # Cached j location, lookup
    j1 = {}
    j2 = {}

    # Populate the cache, make a pass through the input
    s = []
    for i, cmd in enumerate(commands):
        cmd = commands[i]
        if cmd is "(":
            s.append(i)
        elif cmd is ")":
            j = s.pop()
            j1[j] = i

    j2 = dict(zip(j1.values(), j1.keys()))

    end = len(commands)
    while cp < end:
        cmd = commands[cp]

        if cmd is "n":
            mp += 1

        elif cmd is "p":
            mp -= 1

        elif cmd is "i":
            memory[mp] += 1
            if memory[mp] > 255:
                memory[mp] = 0

        elif cmd is "d":
            memory[mp] -= 1
            if memory[mp] < 0:
                memory[mp] = 255

        elif cmd is "r":
            if len(stdin):
                c = stdin[0]
                stdin = stdin[1:]
                memory[mp] = ord(c)
            else:
                return

        elif cmd is "w":
            sys.stdout.write(chr(memory[mp]))
            #sys.stdout.flush()

        elif cmd is "(":
            if memory[mp] == 0:
                # Skipping the loop, condition not met
                cp = j1[cp]

        elif cmd is ")":
            if memory[mp] != 0:
                # Jump back to stored j1
                cp = j2[cp]

        # Increment command pointer
        cp += 1



if __name__ == "__main__":
    main()
