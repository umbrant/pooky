#!/usr/bin/python
"""Interpreter for the Ook! programing language, a variant on the more widelyknown brainf*** language, an exercise in designing a minimal Turing complete language. However, Ook! is definitely the choice of the discerning primate.

If you prefer messy characters to simple Ook!, then this interpreter can be coerced into speaking brainf*** too. But it won't like it."""

# Written by Andrew Wang.
# See http://www.dangermouse.net/esoteric/ook.html for more info.
#
# Source code available at GitHub, the place of all good things:
#
#   git clone git://github.com/azuriel/pooky.git

import os, sys
import time
import threading
from PyQt4 import QtCore,QtGui
from PyQt4.QtCore import QThread, QString, SIGNAL
from pookyUi import Ui_MainWindow

class ExecThread(QThread):

    def __init__(self, parent):
        QThread.__init__(self, parent)

        self.playing = False
        self.stepping = False
        self.exit = False
        self.parent = parent

        self.connect(self.parent, SIGNAL("play()"), self.play)
        self.connect(self.parent, SIGNAL("stop()"), self.stop)
        self.connect(self.parent, SIGNAL("step()"), self.step)

        self.connect(self.parent, SIGNAL("opened()"), self.init)

        # Set if the GUI stuff needs to be cleared/reset on next play
        self.dirty = False


    def play(self):
        if self.dirty:
            self.emit(SIGNAL("clearStdout()"))
            self.highlight()
            self.dirty = False
        self.playing = True
    def stop(self):
        self.playing = False
    def step(self):
        if self.dirty:
            self.emit(SIGNAL("clearStdout()"))
            self.highlight()
            self.dirty = False
        self.stepping = True


    def quickinit(self):
        # Reset, use this when the input file hasn't changed
        self.memory = [0]*30000
        self.mp = 0
        self.cp = 0
        self.sp = 0

    def init(self):

        self.quickinit()

        self.filename = self.parent.filename
        print "Init", self.filename

        self.raw = open(self.filename, "r").readlines()
        # This is populated by parse to have the bf translation
        self.code = []

        # Look for "stdin" as the last line
        self.stdin = ""
        if self.raw[-1][0] == "!":
            self.stdin = self.raw[-1][1:]
            self.raw = self.raw[:-1]
        self.emit(SIGNAL("stdin(QString)"), QString("stdin: " + self.stdin))

        # Plop all the lines together now that stdin is parsed
        self.raw = "".join(self.raw)

        # Check the extension
        ext = self.filename.split(".")[-1]
        if ext == "ook":
            # It's an Ook! file
            self.commands = [x for x in self.parse()]
        else:
            # It's a bf file
            self.commands = list(self.raw)


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

        self.highlight()


    def run(self):
        self.init()
        print "Starting exec loop."
        while not self.exit:
            self.execute()
        print "Run terminating."


    def execute(self):
        end = len(self.commands)

        # Set this to exit the loop
        done = False

        # Reset if at the end
        if self.cp == end or (self.sp == len(self.stdin) and self.stdin):
            #print "Resetting w/ quickinit"
            self.quickinit()
            # We're in need of a good wipedown
            self.dirty = True

        while self.cp < end and not done:
            # Pass if not stepping or playing
            if not self.stepping and not self.playing:
                QThread.msleep(100)
                return

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
                if self.sp < len(self.stdin):
                    c = self.stdin[self.sp]
                    self.sp += 1
                    self.memory[self.mp] = ord(c)
                else:
                    done = True

            elif cmd is ".":
                #sys.stdout.write(chr(self.memory[self.mp]))
                self.emit(SIGNAL("stdout(QString)"),QString(""+chr(self.memory[self.mp])))

            elif cmd is "[":
                if self.memory[self.mp] == 0:
                    # Skipping the loop, condition not met
                    self.cp = self.j1[self.cp]

            elif cmd is "]":
                if self.memory[self.mp] != 0:
                    # Jump back to starting bracket
                    self.cp = self.j2[self.cp]

            if not self.playing or self.cp+1 == end:
                self.highlight()

            # Increment command pointer
            self.cp += 1

            # We're done stepping, return
            if self.stepping:
                done = True

        if self.playing or self.stepping:
            # We're done stepping if we're stepping
            if self.stepping:
                self.stepping = False
            # Stop playing after running through the program once
            if self.playing:
                self.stop()
                self.emit(SIGNAL("donePlaying()"))
            self.highlight()


    def highlight(self):
        # Do this to fix the autoincrementation past len(commands)
        cp = self.cp
        if cp >= len(self.commands):
            cp = len(self.commands)-1
        # Highlight the just executed command
        html = " ".join(self.code[:cp]) +\
                ' <span style="background-color: red">' +\
                self.code[cp] + "</span> " +\
                " ".join(self.code[cp+1:])
        #self.parent.setCode(html)
        self.emit(SIGNAL("code(QString)"), QString(html))

        # Update the registers
        registers = [str(x).zfill(3) for x in self.memory[:100]]
        html = " ".join(registers[:self.mp]) +\
                ' <span style="background-color: red">' +\
                registers[self.mp] + "</span> " +\
                " ".join(registers[self.mp+1:])
        #self.parent.setRegisters(html)
        self.emit(SIGNAL("registers(QString)"), QString(html))


    def parse(self):
        """Translates Ook! into a more parseable form. JK, I actually mean brainf*** :)"""
        a,b,c = "Ook.", "Ook?", "Ook!"
        elements = self.raw.split()
        raw_commands = [a+b, b+a, a+a, c+c, a+c, c+a, c+b, b+c]
        real_commands = [">", "<", "+", "-", ",",
                        ".", "[", "]"]

        translate = dict(zip(raw_commands, real_commands))

        for i in xrange(len(elements)/2):
            e1 = elements.pop(0)
            e2 = elements.pop(0)
            self.code += [e1 + " " + e2]
            yield translate[e1 + e2]


class Main(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # This is always the same
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)

        # Disable the stop button, enabled when you click start
        self.ui.stop.setEnabled(False)

        # Open up a file dialog
        self.filename = ""

        # Create our exec thread, separate from the GUI thread
        self.execthread = ExecThread(self)

        # Connect up the outputs and such
        self.connect(self.execthread, SIGNAL("stdin(QString)"),
                     self.setStdin)
        self.connect(self.execthread, SIGNAL("code(QString)"), self.setCode)
        self.connect(self.execthread, SIGNAL("registers(QString)"),
                     self.setRegisters)
        self.connect(self.execthread, SIGNAL("stdout(QString)"),
                     self.setStdout)

        self.connect(self.execthread, SIGNAL("donePlaying()"),
                     self.donePlaying)
        self.connect(self.execthread, SIGNAL("clearStdout()"),
                     self.clearStdout)


    def getFile(self):
        while True:
            filename = \
                    QtGui.QFileDialog.getOpenFileName(self, "Open", ".")
            ext = filename.split(".")[-1]
            # User hits cancel
            if filename == "":
                return False
            # Bad extension
            elif ext not in ("ook", "bf"):
                print "Valid input files must end in .ook or .bf"
            # Good extension
            else:
                break

        self.filename = filename
        self.ui.filename.setText(self.filename)

        # Start the main thread if it's not running
        if not self.execthread.isRunning():
            self.execthread.start()

        return True


    def setStdin(self, string):
        self.ui.stdin.setText(string)
    def setCode(self, string):
        self.ui.code.setText(string)
    def setRegisters(self, string):
        self.ui.registers.setText(string)
    def setStdout(self, string):
        self.ui.stdout.insertPlainText(string)
    def clearStdout(self):
        self.ui.stdout.setText("")
    def donePlaying(self):
        self.ui.start.setEnabled(True)
        self.ui.stop.setEnabled(False)
        self.ui.step.setEnabled(True)


    def on_start_released(self):
        # Button states
        #print "Start triggered"
        self.ui.start.setEnabled(False)
        self.ui.stop.setEnabled(True)
        self.ui.step.setEnabled(False)

        self.emit(SIGNAL("play()"))


    def on_stop_released(self):
        #print "Stop triggered"
        # Button states
        self.ui.start.setEnabled(True)
        self.ui.stop.setEnabled(False)
        self.ui.step.setEnabled(True)

        self.emit(SIGNAL("stop()"))


    def on_step_released(self):
        #print "Step triggered"
        self.emit(SIGNAL("step()"))


    def on_actionOpen_triggered(self, checked=None):
        if checked is None:
            return
        #print "Open triggered"
        if self.getFile():
            self.clearStdout()
            self.emit(SIGNAL("opened()"))


    def on_actionExit_triggered(self):
        sys.exit(0)


def main():


    # PyQt boilerplate
    app = QtGui.QApplication(sys.argv)
    window=Main()
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
