#!/usr/bin/python
"""Interpreter for the Ook! programing language, a variant on the more widelyknown brainf*** language, an exercise in designing a minimal Turing complete language. However, Ook! is definitely the choice of the discerning primate.

If you prefer messy characters to simple Ook!, then this interpreter can be coerced into speaking brainf*** too. But it won't like it."""

# Written by Andrew Wang.
# See http://www.dangermouse.net/esoteric/ook.html for more info.
#

import os, sys
import time
from PyQt4 import QtCore,QtGui
from pookyUi import Ui_MainWindow


class Main(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # This is always the same
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize GUI state
        self.playing = False

        # Get a filename and go for it
        self.on_actionOpen_2_triggered()

    def init(self):
        # Initialize
        self.memory = [0]*30000
        self.mp = 0
        self.raw = open(self.filename, "r").readlines()
        self.code = []
        self.ui.stdout.setText("")

        self.ui.filename.setText(self.filename)

        # Look for "stdin" as the last line
        self.stdin = ""
        if self.raw[-1][0] == "!":
            self.stdin = self.raw[-1][1:]
            self.raw = self.raw[:-1]
        self.ui.stdin.setText("stdin: " + self.stdin)

        self.raw = "".join(self.raw)
        self.ui.code.setText(self.raw)
        self.ui.registers.setText(" ".join([str(x).zfill(3) for x in
                                       self.memory[0:100]]))

        ext = self.filename.split(".")[-1]
        if ext == "ook":
            # It's an Ook! file
            self.commands = [x for x in self.parse(self.raw)]
        elif ext == "bf":
            # It's a bf file
            self.commands = list(self.raw)
        else:
            print "Valid input files must end in .ook or .bf"
            self.on_actionOpen_2_triggered()

        self.cp = 0

        # Precalculate the jump locations for a speed up
        self.j1 = {}
        self.j2 = {}
        s = []
        for i, cmd in enumerate(self.commands):
            cmd = self.commands[i]
            if cmd is "[":
                s.append(i)
            elif cmd is "]":
                j = s.pop()
                self.j1[j] = i
        self.j2 = dict(zip(self.j1.values(), self.j1.keys()))

    def on_start_released(self):
        # Execute commands until done
        self.playing = True
        self.on_step_released()
        self.playing = False


    def on_step_released(self):
        end = len(self.commands)

        # Reset if at the end
        if self.cp == end:
            self.init()

        while self.cp < end:
            cmd = self.commands[self.cp]

            if cmd is ">":
                self.mp += 1

            elif cmd is "<":
                self.mp -= 1

            elif cmd is "+":
                self.memory[self.mp] += 1
                if self.memory[self.mp] > 255:
                    self.memory[self.mp] = 0

            elif cmd is "-":
                self.memory[self.mp] -= 1
                if self.memory[self.mp] < 0:
                    self.memory[self.mp] = 255

            elif cmd is ",":
                if len(self.stdin):
                    c = self.stdin[0]
                    self.stdin = self.stdin[1:]
                    self.memory[self.mp] = ord(c)
                else:
                    return

            elif cmd is ".":
                #sys.stdout.write(chr(self.memory[self.mp]))
                self.ui.stdout.insertPlainText(""+chr(self.memory[self.mp]))

            elif cmd is "[":
                if self.memory[self.mp] == 0:
                    # Skipping the loop, condition not met
                    self.cp = self.j1[self.cp]

            elif cmd is "]":
                if self.memory[self.mp] != 0:
                    # Jump back to starting bracket
                    self.cp = self.j2[self.cp]

            if not self.playing or self.cp+1 == end:
                # Highlight the just executed command
                html = " ".join(self.code[:self.cp]) +\
                        ' <span style="background-color: red">' +\
                        self.code[self.cp] + "</span> " +\
                        " ".join(self.code[self.cp+1:])
                self.ui.code.setHtml(html)

                # Update the registers
                registers = [str(x).zfill(3) for x in self.memory[:100]]
                html = " ".join(registers[:self.mp]) +\
                        ' <span style="background-color: red">' +\
                        registers[self.mp] + "</span> " +\
                        " ".join(registers[self.mp+1:])
                self.ui.registers.setHtml(html)

            # Increment command pointer
            self.cp += 1

            if not self.playing:
                # Only execute the step once if not playing
                return

    def on_actionOpen_2_triggered(self):
        self.filename = QtGui.QFileDialog.getOpenFileName(self, "Open", ".")
        self.init()

    def on_actionExit_triggered(self):
        sys.exit(0)

    def parse(self, raw):
        """Translates Ook! into a more parseable form. JK, I actually mean brainf*** :)"""
        a,b,c = "Ook.", "Ook?", "Ook!"
        elements = raw.split()
        raw_commands = [a+b, b+a, a+a, c+c, a+c, c+a, c+b, b+c]
        real_commands = [">", "<", "+", "-", ",",
                        ".", "[", "]"]

        translate = dict(zip(raw_commands, real_commands))

        for i in xrange(len(elements)/2):
            e1 = elements.pop(0)
            e2 = elements.pop(0)
            self.code += [e1 + " " + e2]
            yield translate[e1 + e2]


def main():


    # PyQt boilerplate
    app = QtGui.QApplication(sys.argv)
    window=Main()
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
