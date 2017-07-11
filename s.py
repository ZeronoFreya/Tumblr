# -*- coding: utf-8 -*-
__author__ = 'djstava@gmail.com'

import sys

from PyQt5.QtWidgets import QApplication , QMainWindow

from untitled import *

def xxclickqq(self):
    QtWidgets.QMessageBox.information(self.pushButton,"标题","这是第一个PyQt5 GUI程序")

if __name__ == '__main__':
    '''
    主函数
    '''
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)

    # path = QPixmap(r'00.jpg')

    mainWindow.show()
    sys.exit(app.exec_())
