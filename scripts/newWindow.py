import sys
from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def main():
  app = QtGui.QApplication(sys.argv)
  
  w = QtGui.QWidget()
  w.resize(250,150)
  w.move(300,300)
  w.setWindowTitle('Test')
  b = QtGui.QPushButton(w)
  b.clicked.connect(selectFile)
  l = QLineEdit()
  w.show()
  
  sys.exit(app.exec_())

def selectFile():
    l.setText(QFileDialog.getOpenFileName())

if __name__ == '__main__':
  main()
