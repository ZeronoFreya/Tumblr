
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QTextCursor
from gui import Ui_MainWindow
from fun import TextFun
import conf

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.lastPrefix = ''
        self.setupUi(self)
        self.pushButton.clicked.connect(self.mkdirOrFile)
        self.textEdit.installEventFilter(self)
        self.setWindowTitle("Root-")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def backPrevious(self, obj):
        '''返回上一级'''
        textCursor = obj.textCursor()
        lineContent = TextFun.getLineUnderCursor(textCursor)

        if not lineContent: #删除空白行
            return TextFun.resetText( textCursor )
        endChars = lineContent[-2:]
        if endChars not in conf.prefixList:
            '''建立子文件夹'''
            sibling = False #是否改为同辈文件夹
            if '.' in lineContent:
                sibling = True
            pos = textCursor.position() #光标位置此时处于选择行的最后

            rs = TextFun.cursorToPrefix(textCursor, lineContent)
            if rs == -1:
                textCursor.movePosition(QTextCursor.StartOfLine)
            #判断是否有子文件
            while True:
                if not textCursor.movePosition(QTextCursor.Down):
                    textCursor.movePosition(QTextCursor.EndOfLine)
                    # print('7')
                    break
                endPos = textCursor.position()
                textCursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                i = textCursor.selectedText().rstrip().rfind('─')
                if i == -1:
                    # print('8')
                    textCursor.movePosition(QTextCursor.Up)
                    textCursor.movePosition(QTextCursor.EndOfLine)
                    break
                endPos += i
                textCursor.setPosition(endPos)
                textCursor.movePosition(QTextCursor.Left,  QTextCursor.KeepAnchor)
                char = textCursor.selectedText()
                textCursor.setPosition(endPos)
                if char == '└':
                    # print('1')
                    continue
                elif char in ('│', '├'):
                    while True:
                        endPos = TextFun.cursorDown( textCursor )
                        if endPos == -1:
                            # print('2')
                            break
                        textCursor.movePosition(QTextCursor.Left,  QTextCursor.KeepAnchor)
                        char = textCursor.selectedText()
                        textCursor.setPosition(endPos)
                        if char in ('│', '├'):
                            # print('4')
                            continue
                        else:
                            # print('5')
                            break
                    continue
                else:
                    print('6')
                    break

            obj.setTextCursor(textCursor)
            TextFun.saveDocAboveCursor( textCursor )
            self.lastPrefix = TextFun.getNextLayerPrefix( lineContent, sibling )
            textCursor.clearSelection()
            textCursor.insertText( '\n' + self.lastPrefix  + ' ')
        else:
            if lineContent in conf.prefixList:
                TextFun.delLineUnderCursor(textCursor)
                self.lastPrefix = ''
                return TextFun.resetText(textCursor, True)

            self.lastPrefix = TextFun.getPrevLayerPrefix( lineContent )

            textCursor.clearSelection()
            i = lineContent.rfind('─')
            if not i == -1:
                i = i - conf.placeholderNum
                textCursor.movePosition(QTextCursor.StartOfLine)
                endPos = textCursor.position() + i
                textCursor.setPosition(endPos)
                textCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
                ts = textCursor.selectedText()
                textCursor.clearSelection()
                textCursor.setPosition(endPos)
                if ts == '│':
                    textCursor.movePosition(QTextCursor.EndOfLine)
                    TextFun.resetText( textCursor )
                    textCursor.setPosition(endPos)

                    if TextFun.functionss(textCursor, endPos):
                        obj.setTextCursor(textCursor)
                        self.lastPrefix = '\n' + self.lastPrefix
                    else:
                        # print("xxx")
                        pass
                else:
                    textCursor.select(QTextCursor.LineUnderCursor)

            textCursor.insertText( self.lastPrefix + ' ')
            textCursor.clearSelection()
        TextFun.changeChar(textCursor)
        return True

    def eventFilter(self, obj, event):
        if obj == self.textEdit:
            if event.type()== QEvent.KeyPress:
                # print(event.key())
                if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                    return self.backPrevious(obj)
                # elif event.key() in (Qt.Key_Slash, Qt.Key_Backslash): # / or \
                #     return self.mkChild(obj)
                elif event.key() == Qt.Key_Tab:
                    return self.buildPath()
                # elif event.key() == Qt.Key_Up:
                #     textCursor = obj.textCursor()
                #     TextFun.cursorUp(textCursor)
                #     # textCursor.movePosition(QTextCursor.Up)
                #     obj.setTextCursor(textCursor)
                #     return True
                # elif event.key() == Qt.Key_Down:
                #     textCursor = obj.textCursor()
                #     TextFun.cursorDown(textCursor)
                #     # textCursor.movePosition(QTextCursor.Up)
                #     obj.setTextCursor(textCursor)
                #     return True
            return False

    def mkdirOrFile(self):
        dict = TextFun.buildPath( self.textEdit.toPlainText() )
        root = self.windowTitle()[5:].strip()
        if root == '':
            return
        paths = TextFun.mkPaths( root, dict )
        # print( paths )
        QtWidgets.QMessageBox.information(self.pushButton,"paths",paths)
        return
        import os
        import codecs
        import conf

        # for p in self.textEdit.toPlainText().split('\n'):
        for p in paths.splitlines():
            if not p:
                continue;
            p = p.strip()
            if p.startswith('/') or p.startswith('\\'):
                p = p[1:]
            # p = conf.root+p
            pa = os.path.split(p)
            if pa[1] and not pa[1].endswith('.') and '.' in pa[1]: #是文件
                try:
                    if not os.path.exists(pa[0]):
                        os.makedirs(pa[0])
                    f=codecs.open(p,'w', 'UTF-8')
                    f.close()
                except Exception as e:
                    print(e)
            else:  #是文件夹
                try:
                    os.makedirs(p)
                except Exception as e:
                    print(e)
        self.close()
