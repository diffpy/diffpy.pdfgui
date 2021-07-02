from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys
import os
import numpy as np

class window(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        self.set_ui()

    def done(self):
        self.close()

    def keyPressEvent(self, event):

        if (event.key() == "enter") or (event.key() == "space"):
            self.done()

    #def mousePressEvent(self, event):
    #    print("press",event.GrabMouse,event.DragMove, event.MouseButtonPress, event.MouseButtonRelease)
    #    self.hold = True
        
    #def mouseReleaseEvent(self, event):
    #    self.hold = False
    #    print("release")

    def set_ui(self):
        #self.hold = False
        #self.new = True
        #self.mag = 1
        icon = QIcon('icon.png')
        self.setWindowIcon(icon)
        self.setWindowTitle('Instructions')
        self.setGeometry(50,50,300,200)
        self.setMouseTracking(True)

        lab = "<b>Mouse Controls</b>:<br><br><b>L. Click</b>: Select atoms for next spin assignment<br><b>R. Click</b>: Undo previous spin assignments<br><br><b>Keyboard Controls</b>:<br><br><b>Enter</b>: Assign Spins after selecting<br><b>t</b> : Toggle non-magnetic atoms<br><b>b</b> : Toggle bounding box<br><b>g</b> : Toggle plot grid<br><b>n</b> : Toggle ploted numbers on axes ticks<br><b>i</b> : Instructions popup<br><b>f</b>: Enter fullscreen mode<br><b>Escape</b>: Exit Program<br><b>CTRL +</b> / <b>CTRL -</b> : Zoom in or out<br><b>U / D Arrows</b>: Change atom size<br><b>R</b> / <b>L Arrows</b>: Change vector length"

        self.l1 = QtWidgets.QLabel()
        self.l1.setText(lab)
        self.l1.move(50,0)

        self.b1 = QtWidgets.QPushButton()
        self.b1.setText("Done")
        self.b1.move(50,25)
        self.b1.setAutoDefault(True)
        self.b1.clicked.connect(self.done)
                    
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.l1)
        layout.addWidget(self.b1)
        self.setLayout(layout)


app = QtWidgets.QApplication(sys.argv)
win = window()
win.show()
"""
qwindow = win.windowHandle()

if qwindow is not None:
    
    def handle_activeChanged():
        if win.new:
            win.new = False
        #elif (not qwindow.isActive()) or (win.hold) :
        #    win.close()
    
    qwindow.activeChanged.connect(handle_activeChanged)
"""
sys.exit(app.exec_())

