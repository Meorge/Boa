# A window test.

import os
import struct
import socket
import sys
import traceback
import signal
import syntax
import threading
import dweepy
import subprocess
import tempfile
import functools
import requests, pip, site

from PyQt5 import QtCore, QtGui, QtWidgets
from coolGUIs.coolGUI import SearchBox
#from pastebin import PastebinAPI
Qt = QtCore.Qt

import TPLLib

global completeParentheses, isCollabing, username, partnerUsername
completeParentheses = True
isCollabing = False


class Window(QtWidgets.QMainWindow):
    """Main Window"""
    
    def __init__(self, parent=None):
        global IRCThread
        super(Window, self).__init__(parent)

        '''thing = pip.get_installed_distributions()
        for i in thing:
            print(i)'''
        #print(help('modules'))
        print(site.getsitepackages())
        self.resize(1200,700)
        
        self.setStyleSheet("""QMainWindow {background-color: #202020;}""")
        self.textedit = LineTextWidget()
        
        stuffToRecognize = syntax.PythonHighlighter.keywords + syntax.PythonHighlighter.operators
        
        self.textedit.edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.completer = QtWidgets.QCompleter(stuffToRecognize)
        #self.completer.setStyleSheet('''QCompleter {font-family: 'Courier'}''')
        #self.completer.setModel(QtCore.QStringListModel(['print', 'def', 'jeebus']))
        self.textedit.edit.setCompleter(self.completer)
        #self.texteditNumbers = LineTextWidget.NumberBar()
        #self.texteditNumbers.setTextEdit(self.textedit)
        
        #self.layout = QtWidgets.QHBoxLayout()
        #self.layout.addWidget(self.texteditNumbers)
        #self.layout.addWidget(self.textedit)
        #self.layoutW = QtWidgets.QWidget()
        #self.layoutW.setLayout(self.layout)
        self.cursorGS = QtWidgets.QGraphicsScene()
        self.cursorGV = QtWidgets.QGraphicsView(self.cursorGS)
        self.cursorGV.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.texteditScrollV = self.textedit.edit.verticalScrollBar()
        self.texteditScrollV.valueChanged.connect(self.verticalScrolling)
        self.texteditScrollH = self.textedit.edit.horizontalScrollBar()
        self.texteditScrollH.valueChanged.connect(self.horizontalScrolling)

        self.cursorGV_ScrollV = self.cursorGV.verticalScrollBar()

        self.installEventFilter(self)
        self.textedit.edit.setFocus()

        transColor = QtGui.QColor('red')
        #transColor.setAlpha(0)
        self.cursorGV.setStyleSheet('QGraphicsView {background-color: transparent;}')
        transparentBrush = QtGui.QBrush(transColor)
        #self.cursorGV.setBackgroundBrush(transparentBrush)


        self.overallWidget = QtWidgets.QWidget()
        self.overallWidgetL = QtWidgets.QGridLayout()
        self.overallWidgetL.addWidget(self.textedit, 0,0)
        self.overallWidgetL.addWidget(self.cursorGV, 0,0)
        self.cursorGV.setGeometry(self.textedit.edit.geometry())
        self.overallWidget.setLayout(self.overallWidgetL)
        self.setCentralWidget(self.overallWidget)
        self.syntax = syntax.PythonHighlighter(self.textedit.edit)

        self.textedit.edit.document().contentsChange.connect(self.checkforHighlight)
        self.terminalDock = QtWidgets.QDockWidget('Terminal')
        self.terminalDock.setStyleSheet("""QDockWidget::title {background-color: #333333; text-align: center; border-top: 1px solid #555555;} QDockWidget {color: white;}
            QPushButton {background-color: #343434; color: white; border-radius: 5px; padding-top: 4px; padding-right: 6px; padding-left: 6px; padding-bottom: 4px;}
            QPushButton::pressed {background-color: #1e1e1e;}""")
        self.terminalDock.setWindowTitle('Terminal')
        self.addDockWidget(Qt.BottomDockWidgetArea, self.terminalDock)


        self.runButton = QtWidgets.QPushButton('Run Code')
        self.runButton.clicked.connect(self.runCode)
        self.clearButton = QtWidgets.QPushButton('Clear Terminal')
        self.clearButton.clicked.connect(self.clearTerminal)
        
        
        self.buttonsLayout = QtWidgets.QVBoxLayout()
        self.buttonsLayout.addWidget(self.runButton)
        self.buttonsLayout.addWidget(self.clearButton)
        self.buttonsLayoutW = QtWidgets.QWidget()
        self.buttonsLayoutW.setLayout(self.buttonsLayout)
        
        self.terminalArea = QtWidgets.QTextEdit()
        self.terminalArea.setStyleSheet('''QTextEdit {font-family: 'Courier'; background-color: #343434; color: white; border-radius: 6px;}''')
        self.terminalArea.setFontFamily('Courier')
        self.terminalArea.setReadOnly(True)
        
        self.terminalLayout = QtWidgets.QHBoxLayout()
        self.terminalLayout.addWidget(self.buttonsLayoutW)
        self.terminalLayout.addWidget(self.terminalArea)
        

        self.terminalWidget = QtWidgets.QWidget()
        self.terminalWidget.resize(self.width(), 300)
        self.terminalWidget.setMaximumHeight(100)
        self.terminalWidget.setLayout(self.terminalLayout)
        
        self.terminalDock.setWidget(self.terminalWidget)
    
        self.openAction = QtWidgets.QAction('&Open', self)
        self.openAction.setShortcut(QtGui.QKeySequence.Open)
        self.openAction.setStatusTip('Open an existing Python script.')
        self.openAction.triggered.connect(self.openFile)
        
        self.newAction = QtWidgets.QAction('&New', self)
        self.newAction.setShortcut(QtGui.QKeySequence.New)
        self.newAction.setStatusTip('Create an empty Python script')
        self.newAction.triggered.connect(self.newFile)
        
        self.saveAction = QtWidgets.QAction('&Save', self)
        self.saveAction.setShortcut(QtGui.QKeySequence.Save)
        self.saveAction.setStatusTip('Save file')
        self.saveAction.triggered.connect(self.saveFile)


        self.buildAction = QtWidgets.QAction('Build...', self)
        self.buildAction.setShortcut(QtGui.QKeySequence('Ctrl+B'))
        #self.buildAction.triggered.connect(self.buildWindow)
        
        self.quickBuildAction = QtWidgets.QAction('Quick Build...', self)
        self.quickBuildAction.setShortcut(QtGui.QKeySequence('Ctrl+Alt+B'))
        #self.quickBuildAction.triggered.connect(self.buildWindow)
        
        self.menubar = QtWidgets.QMenuBar()
        self.fileMenu = self.menubar.addMenu('&File')
        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.buildAction)
        self.fileMenu.addAction(self.quickBuildAction)
        
        ###
        
        self.cutAction = QtWidgets.QAction('&Cut', self)
        self.cutAction.setShortcut(QtGui.QKeySequence.Cut)
        self.cutAction.setStatusTip('Cut text')
        self.cutAction.triggered.connect(self.textedit.edit.cut) 

        self.copyAction = QtWidgets.QAction('&Copy', self)
        self.copyAction.setShortcut(QtGui.QKeySequence.Copy)
        self.copyAction.setStatusTip('Copy text')
        self.copyAction.triggered.connect(self.textedit.edit.copy) 
        
        self.pasteAction = QtWidgets.QAction('&Paste', self)
        self.pasteAction.setShortcut(QtGui.QKeySequence.Paste)
        self.pasteAction.setStatusTip('Paste text')
        self.pasteAction.triggered.connect(self.textedit.edit.paste) 
 
        self.completeAction = QtWidgets.QAction('&Complete Keywords', self, checkable=True)
        self.completeAction.setChecked(False)
        self.pasteAction.setShortcut(QtGui.QKeySequence.Refresh)
        self.completeAction.setStatusTip('Complete things')
        self.completeAction.triggered.connect(self.toggleCompletion)
 
        self.parenthesesAction = QtWidgets.QAction('&Complete Quotes/Parentheses', self, checkable=True)
        self.parenthesesAction.setChecked(False)
        self.parenthesesAction.setStatusTip('Complete things')
        self.parenthesesAction.triggered.connect(self.toggleParentheses)
               
        self.syntaxAction = QtWidgets.QAction('&Syntax Highlighting', self, checkable=True)
        self.syntaxAction.setChecked(True)
        self.syntaxAction.setShortcut('Ctrl+H')
        self.syntaxAction.setStatusTip('Complete things')
        self.syntaxAction.triggered.connect(self.toggleSyntax) 
        
        self.moduleThingy = QtWidgets.QAction('&Modules', self)
        self.moduleThingy.setShortcut(QtGui.QKeySequence.Paste)
        self.moduleThingy.setStatusTip('Currently imported modules')
        self.moduleThingy.triggered.connect(self.moduleWindow) 

        
        self.editMenu = self.menubar.addMenu('&Edit')
        self.editMenu.addAction(self.cutAction)
        self.editMenu.addAction(self.copyAction)
        self.editMenu.addAction(self.pasteAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.completeAction)
        self.editMenu.addAction(self.parenthesesAction)
        self.editMenu.addAction(self.syntaxAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.moduleThingy)
        ###

        self.insertFunctionAction = QtWidgets.QAction('&Function', self)
        self.insertFunctionAction.setShortcut(QtGui.QKeySequence('Ctrl+Alt+F'))
        self.insertFunctionAction.setStatusTip('Insert a blank function')
        self.insertFunctionAction.triggered.connect(self.insertFunctionDialog) 

        self.insertClassAction = QtWidgets.QAction('&Class', self)
        self.insertClassAction.setShortcut(QtGui.QKeySequence('Ctrl+Alt+C'))
        self.insertClassAction.setStatusTip('Insert a blank class')
        self.insertClassAction.triggered.connect(self.insertClassDialog) 

        self.insertIfStatement = QtWidgets.QAction('&If Statement', self)
        self.insertIfStatement.setShortcut(QtGui.QKeySequence('Ctrl+Alt+I'))
        self.insertIfStatement.setStatusTip('Insert a blank \'if\' statement')
        self.insertIfStatement.triggered.connect(self.insertIfDialog)

        self.insertWithStatement = QtWidgets.QAction('&With Statement', self)
        self.insertWithStatement.setShortcut(QtGui.QKeySequence('Ctrl+Alt+W'))
        self.insertWithStatement.setStatusTip('Insert a blank \'with\' statement')
        self.insertWithStatement.triggered.connect(self.insertWithStatementDialog)
 
        self.insertForLoopStatement = QtWidgets.QAction('&For Loop', self)
        self.insertForLoopStatement.setShortcut(QtGui.QKeySequence('Ctrl+Alt+L'))
        self.insertForLoopStatement.setStatusTip('Insert a blank \'for\' loop')
        self.insertForLoopStatement.triggered.connect(self.insertForLoopDialog)

        self.insertWhileLoopStatement = QtWidgets.QAction('&While Loop', self)
        self.insertWhileLoopStatement.setShortcut(QtGui.QKeySequence('Ctrl+Alt+Shift+W'))
        self.insertWhileLoopStatement.setStatusTip('Insert a blank \'while\' loop')
        self.insertWhileLoopStatement.triggered.connect(self.insertWhileLoopDialog)

        self.insertTryExceptStatement = QtWidgets.QAction('&Try/Except', self)
        self.insertTryExceptStatement.setShortcut(QtGui.QKeySequence('Ctrl+Alt+E'))
        self.insertTryExceptStatement.setStatusTip('Insert a blank try/except statement')
        self.insertTryExceptStatement.triggered.connect(self.insertTryExcept) 

        self.insertNameEqMainStatement = QtWidgets.QAction('&if __name__ == \'__main__\'', self)
        self.insertNameEqMainStatement.setShortcut(QtGui.QKeySequence('Ctrl+Alt+E'))
        self.insertNameEqMainStatement.setStatusTip('Insert a blank try/except statement')
        self.insertNameEqMainStatement.triggered.connect(self.insertNameEqMainF) 
        
        self.insertMenu = self.menubar.addMenu('&Insert')
        self.insertMenu.addAction(self.insertFunctionAction)
        self.insertMenu.addAction(self.insertClassAction)
        self.insertMenu.addAction(self.insertIfStatement)
        self.insertMenu.addAction(self.insertWithStatement)
        self.insertMenu.addAction(self.insertForLoopStatement)
        self.insertMenu.addAction(self.insertWhileLoopStatement)
        self.insertMenu.addAction(self.insertTryExceptStatement)
        self.insertMenu.addSeparator()
        self.insertMenu.addAction(self.insertNameEqMainStatement)

        
        ###

        self.collabStatusLabel = QtWidgets.QAction('Current Status: Disconnected', self)
        self.collabStatusLabel.setEnabled(False)
                
        self.collabNewSessionAction = QtWidgets.QAction('&Begin New Session', self)
        self.collabNewSessionAction.triggered.connect(self.beginNewSession_C) 
                
        self.collabConnectAction = QtWidgets.QAction('&Connect To Session', self)
        self.collabConnectAction.triggered.connect(self.connectToSession_C)                 
        
        self.collabMenu = self.menubar.addMenu('&Collaboration')
        self.collabMenu.addAction(self.collabStatusLabel)
        self.collabMenu.addSeparator()
        self.collabMenu.addAction(self.collabNewSessionAction)
        self.collabMenu.addAction(self.collabConnectAction)
                
        ###
        
        
        self.setMenuBar(self.menubar)
    
        self.statusBar = QtWidgets.QStatusBar()
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.setStyleSheet("""
            QStatusBar {background-color: #424242; color: white; border-top: 1px solid #666666;}""")
        self.statusBar_Lines = QtWidgets.QLabel()
        self.statusBar_Lines.setStyleSheet("""QLabel {color: white;}""")
        self.statusBar_FunctionList = QtWidgets.QComboBox()
        self.statusBar_FunctionList.setMinimumWidth(400)
        #self.statusBar_FunctionList.setMinimumHeight(20)
        self.statusBar_FunctionList.activated.connect(self.goToDef)
        
        self.statusBar.addPermanentWidget(self.statusBar_Lines)
        self.statusBar.addWidget(self.statusBar_FunctionList)
        self.setStatusBar(self.statusBar)
        self.textedit.edit.cursorPositionChanged.connect(self.printCursorPos)
        self.textedit.edit.document().contentsChange.connect(self.sendDweeps_)
    

        
        IRCThread = SpecialThread()

        IRCThread.thingSignal.connect(self.makeTheChanges)

        self.changesSaved = True

        self.setFixedSize(self.size())


    '''def buildWindow(self):
        self.buildWindow ='''


    def moduleWindow(self):
        ## collect the modules
        importList = []
        moduleNames = []
        bob = False
        firstPart = self.textedit.edit.toPlainText().replace('\t', '').replace('    ', '').split('\n')
        #print(firstPart)
        for i in firstPart:
            if i[:7] == 'import ' or i[:5] == 'from ':
                importList.append(i)



        for i2 in importList:
            if ',' not in i2:
                splitStuff = i2.split(' ')
                print('Without commas, ', splitStuff)
                moduleName = splitStuff[1]

                #if moduleName
                moduleNames.append(moduleName)

            else:
                splitStuff = i2.split(', ')

                firstPart_2 = splitStuff[0].split()
                print(firstPart_2)
                if firstPart_2[0] == 'from':
                    #moduleNames.append(splitStuff[0].split()[1] + '.' + firstPart_2[3])
                    bob = True


                print('With commas, ', splitStuff)

                moduleNames.append(splitStuff[0].split()[1])

                for item in splitStuff[1:]:
                    if bob:
                        pass
                        #moduleNames.append(splitStuff[0].split()[1] + '.' + item)
                    else:
                        moduleNames.append(item)





        print('Our modules:', moduleNames)

        self.modulesWindow_W = QtWidgets.QWidget(self)
        self.modulesWindow_W.setWindowFlags(Qt.Sheet)

        self.currentModulesList = DraggableListWidget()

        self.currentModulesList_L = QtWidgets.QLabel('IMPORTED MODULES')
        self.currentModulesList_L.setStyleSheet('QLabel {font-size: 9px; color: #333333;}')

        self.currentModulesListWidget__ = QtWidgets.QWidget()
        self.currentModulesListWidget__L = QtWidgets.QVBoxLayout()
        self.currentModulesListWidget__.setLayout(self.currentModulesListWidget__L)

        self.currentModulesListWidget__L.addWidget(self.currentModulesList_L)
        self.currentModulesListWidget__L.addWidget(self.currentModulesList)

        for item in moduleNames:
            if len(item) < 30:
                self.currentModulesList.addItem(item)
            else:
                self.currentModulesList.addItem(item[:28] + '...')


        #self.modulesWindow_L.addWidget(self.currentModulesList)



        thing = pip.get_installed_distributions()

        installedModuleNames = []
        for i in thing:
            if len(i.key) < 30:
                installedModuleNames.append(i.key)
            else:
                installedModuleNames.append(i.key[:28] + '...')

        #currentModules_Pt1 = exec('help(\'modules\')')

        #print(currentModules_Pt1.split())

        self.installedModulesList = DraggableListWidget()
        for i in installedModuleNames:
            self.installedModulesList.addItem(i)


        self.installedModulesList_L = QtWidgets.QLabel('INSTALLED MODULES')
        self.installedModulesList_L.setStyleSheet('QLabel {font-size: 9px; color: #333333;}')

        self.installedModulesListWidget__ = QtWidgets.QWidget()
        self.installedModulesListWidget__L = QtWidgets.QVBoxLayout()
        self.installedModulesListWidget__.setLayout(self.installedModulesListWidget__L)

        self.installedModulesListWidget__L.addWidget(self.installedModulesList_L)
        self.installedModulesListWidget__L.addWidget(self.installedModulesList)

        self.modulesWindow_XButton = QtWidgets.QPushButton('Close')
        self.modulesWindow_XButton.clicked.connect(self.hideModulesWindow)


        self.innerLayout = QtWidgets.QHBoxLayout()
        self.innerLayout.addWidget(self.currentModulesListWidget__)
        self.innerLayout.addWidget(self.installedModulesListWidget__)

        self.innerWidget = QtWidgets.QWidget()
        self.innerWidget.setLayout(self.innerLayout)
        self.overallLayout_currentModules = QtWidgets.QVBoxLayout()
        self.modulesWindow_W.setLayout(self.overallLayout_currentModules)
        self.overallLayout_currentModules.addWidget(self.innerWidget, 0)
        self.overallLayout_currentModules.addWidget(self.modulesWindow_XButton, 1)







        print(installedModuleNames)

        self.modulesWindow_W.show()


    def hideModulesWindow(self):
        self.modulesWindow_W.hide()

    def verticalScrolling(self):
        value = self.texteditScrollV.value()
        self.cursorGV.verticalScrollBar().setValue(value)

    def horizontalScrolling(self):
        value = self.texteditScrollH.value()
        self.cursorGV.horizontalScrollBar().setValue(value)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Resize:
            geometry = self.textedit.edit.geometry()
            tl = self.textedit.edit.rect().topLeft()
            self.cursorGV.setGeometry(geometry.x(),geometry.y(), geometry.width(), geometry.height())
            #event.ignore()
            self.cursorGS.setSceneRect(geometry.x()+245,geometry.y()+7, geometry.width(), geometry.height())
            #self.cursorGV.set
            #self.cursorGS.setGeometry(geometry)
        return super(Window, self).eventFilter(obj, event)


    def printCursorPos(self):
        global isCollabing
        x = float(self.textedit.edit.cursorRect().x())
        y = float(self.textedit.edit.cursorRect().y()) 
        width = float(self.textedit.edit.cursorRect().width())
        height = float(self.textedit.edit.cursorRect().height())

        newQRectF = QtCore.QRectF(x, y, width + 2, height)

        newBrush = QtGui.QBrush(QtGui.QColor('#0066FF'))
        newPen = QtGui.QPen(QtGui.QColor('#0066FF'))
        #self.cursorGS.clear()
        #self.cursorGS.addRect(newQRectF, brush=newBrush, pen=newPen)
        #self.cursorGS.addRect(QtCore.QRectF(0,0,300,300))
        #print(self.textedit.edit.cursorRect())

        if isCollabing:
            if self.textedit.edit.textCursor().selectionStart() == self.textedit.edit.textCursor().selectionEnd():
                Command = 'M ' + str(self.textedit.edit.textCursor().position())
            else:
                Command = 'M! ' + str(self.textedit.edit.textCursor().selectionStart()) + ' ' + str(self.textedit.edit.textCursor().selectionEnd())
            dweepy.dweet_for('boa_editor_' + pastebin_code, {'command': Command, 'person': username})

    def closeEvent(self,event):
        if self.changesSaved:

            event.accept()

        else:

            popup = QtWidgets.QMessageBox(self)

            popup.setIcon(QtWidgets.QMessageBox.Warning)

            popup.setText("The document has been modified")

            popup.setInformativeText("Do you want to save your changes?")

            popup.setStandardButtons(QtWidgets.QMessageBox.Save    |
                                      QtWidgets.QMessageBox.Cancel |
                                      QtWidgets.QMessageBox.Discard)

            popup.setDefaultButton(QtWidgets.QMessageBox.Save)

            answer = popup.exec_()

            if answer == QtWidgets.QMessageBox.Save:
                self.saveFile()

            elif answer == QtWidgets.QMessageBox.Discard:
                event.accept()

            else:
                event.ignore()             
    def toggleParentheses(self):
        global completeParentheses
        if self.parenthesesAction.isChecked():
            completeParentheses = True
        else:
            completeParentheses = False
    
    def insertNameEqMainF(self):
        self.insertNameEqMain = """if __name__ == '__main__':\n\tmain()"""
        cursor = self.textedit.edit.textCursor()
        
        line=cursor.block().text()
        ind=len(line)-len(line.lstrip('\t'))
        
        cursor.insertText(self.insertNameEqMain.replace('\n', '\n' + ''.join(['\t' for x in range(ind)])))
    
    def insertWithStatementDialog(self):
        self.WithStatementCode = """with ITEM """ 
        self.WithStatementCode2 = """as VAR:\n\tpass"""
        
        self.insertWithStatementDialog_D = QtWidgets.QDialog()
        self.insertWithStatementDialog_L1 = QtWidgets.QLabel('With')
        self.insertWithStatementDialog_L2 = QtWidgets.QLabel('as')
        self.insertWithStatementDialog_T1 = QtWidgets.QLineEdit('item')
        self.insertWithStatementDialog_T2 = QtWidgets.QLineEdit('variable')
        
        self.insertWithStatementDialog_OK = QtWidgets.QPushButton('OK')
        
        
        self.insertWithStatementDialog_Layout = QtWidgets.QVBoxLayout()
        
        self.insertWithStatementDialog_InnerL = QtWidgets.QHBoxLayout()
        self.insertWithStatementDialog_InnerL.addWidget(self.insertWithStatementDialog_L1)
        self.insertWithStatementDialog_InnerL.addWidget(self.insertWithStatementDialog_T1)
        self.insertWithStatementDialog_InnerL.addWidget(self.insertWithStatementDialog_L2)
        self.insertWithStatementDialog_InnerL.addWidget(self.insertWithStatementDialog_T2)
        self.insertWithStatementDialog_InnerLW = QtWidgets.QWidget()
        self.insertWithStatementDialog_InnerLW.setLayout(self.insertWithStatementDialog_InnerL)
        
        
        
        self.insertWithStatementDialog_Layout.addWidget(self.insertWithStatementDialog_InnerLW)
        self.insertWithStatementDialog_Layout.addWidget(self.insertWithStatementDialog_OK)
        
        self.insertWithStatementDialog_D.setLayout(self.insertWithStatementDialog_Layout)
        self.insertWithStatementDialog_D.show()
        self.insertWithStatementDialog_OK.clicked.connect(self.insertWithStatementF)
    
    def insertWithStatementF(self):
        thing = self.WithStatementCode.replace('ITEM', self.insertWithStatementDialog_T1.text()) + self.WithStatementCode2.replace('VAR', self.insertWithStatementDialog_T2.text())
        self.insertWithStatementDialog_D.hide()
        cursor = self.textedit.edit.textCursor()
        
        line=cursor.block().text()
        ind=len(line)-len(line.lstrip('\t'))
        
        cursor.insertText(thing.replace('\n', '\n' + ''.join(['\t' for x in range(ind)])))
    
    def insertWhileLoopDialog(self):
        self.whileLoopCode = """While THING:\n\tpass"""
        
        self.insertWhileLoopDialog_D = QtWidgets.QDialog()
        self.insertWhileLoopDialog_L = QtWidgets.QLabel('While:')
        self.insertWhileLoopDialog_T = QtWidgets.QLineEdit('True')
        self.insertWhileLoopDialog_OK = QtWidgets.QPushButton('OK')
        
        
        self.insertWhileLoopDialog_Layout = QtWidgets.QVBoxLayout()
        self.insertWhileLoopDialog_Layout.addWidget(self.insertWhileLoopDialog_L)
        self.insertWhileLoopDialog_Layout.addWidget(self.insertWhileLoopDialog_T)
        self.insertWhileLoopDialog_Layout.addWidget(self.insertWhileLoopDialog_OK)
        
        self.insertWhileLoopDialog_D.setLayout(self.insertWhileLoopDialog_Layout)
        self.insertWhileLoopDialog_D.show()
        self.insertWhileLoopDialog_OK.clicked.connect(self.insertWhileLoop)
    
    def insertWhileLoop(self):
        self.insertWhileLoopDialog_D.hide()
        WhileLoopCodeReplace = self.whileLoopCode.replace('THING', self.insertWhileLoopDialog_T.text())
        cursor = self.textedit.edit.textCursor()
        
        line=cursor.block().text()
        ind=len(line)-len(line.lstrip('\t'))
        
        cursor.insertText(WhileLoopCodeReplace.replace('\n', '\n' + ''.join(['\t' for x in range(ind)])))
    
    def insertTryExcept(self):
        self.tryExcept = """try:\n\tpass\nexcept Exception as e:\n\tpass"""
        cursor = self.textedit.edit.textCursor()
        
        line=cursor.block().text()
        ind=len(line)-len(line.lstrip('\t'))
        
        cursor.insertText(self.tryExcept.replace('\n', '\n' + ''.join(['\t' for x in range(ind)])))       
    
    def insertForLoopDialog(self):
        self.forLoopCode = """for ITEM """ 
        self.forLoopCode2 = """in VAR:\n\tpass"""
        
        self.insertForLoopDialog_D = QtWidgets.QDialog()
        self.insertForLoopDialog_L1 = QtWidgets.QLabel('For')
        self.insertForLoopDialog_L2 = QtWidgets.QLabel('in')
        self.insertForLoopDialog_T1 = QtWidgets.QLineEdit('item')
        self.insertForLoopDialog_T2 = QtWidgets.QLineEdit('variable')
        
        self.insertForLoopDialog_OK = QtWidgets.QPushButton('OK')
        
        
        self.insertForLoopDialog_Layout = QtWidgets.QVBoxLayout()
        
        self.insertForLoopDialog_InnerL = QtWidgets.QHBoxLayout()
        self.insertForLoopDialog_InnerL.addWidget(self.insertForLoopDialog_L1)
        self.insertForLoopDialog_InnerL.addWidget(self.insertForLoopDialog_T1)
        self.insertForLoopDialog_InnerL.addWidget(self.insertForLoopDialog_L2)
        self.insertForLoopDialog_InnerL.addWidget(self.insertForLoopDialog_T2)
        self.insertForLoopDialog_InnerLW = QtWidgets.QWidget()
        self.insertForLoopDialog_InnerLW.setLayout(self.insertForLoopDialog_InnerL)
        
        
        
        self.insertForLoopDialog_Layout.addWidget(self.insertForLoopDialog_InnerLW)
        self.insertForLoopDialog_Layout.addWidget(self.insertForLoopDialog_OK)
        
        self.insertForLoopDialog_D.setLayout(self.insertForLoopDialog_Layout)
        self.insertForLoopDialog_D.show()
        self.insertForLoopDialog_OK.clicked.connect(self.insertForLoop)
    
    def insertForLoop(self):
        thing = self.forLoopCode.replace('ITEM', self.insertForLoopDialog_T1.text()) + self.forLoopCode2.replace('VAR', self.insertForLoopDialog_T2.text())
        self.insertForLoopDialog_D.hide()
        cursor = self.textedit.edit.textCursor()
        
        line=cursor.block().text()
        ind=len(line)-len(line.lstrip('\t'))
        
        cursor.insertText(thing.replace('\n', '\n' + ''.join(['\t' for x in range(ind)])))
    
    
    def insertIfDialog(self):
        self.ifCode = """if INSERT:\n\tpass\n"""
        self.elifCode = """elif INSERT:\n\tpass\n"""
        self.elseCode = """else:\n\tpass"""
        
        self.insertIfDialog_ = QtWidgets.QDialog()
        self.insertIfDialog_L1 = QtWidgets.QLabel('If ')
        self.insertIfDialog_L2 = QtWidgets.QLabel('Else if ')
        self.insertIfDialog_L3 = QtWidgets.QLabel('Else ')
        
        
        self.insertIfDialog_T1 = QtWidgets.QLineEdit('1 == 1')
        self.insertIfDialog_T2 = QtWidgets.QLineEdit('2 == 2')
        
        
        '''self.insertIfDialog_C2 = QtWidgets.QCheckBox()
        self.insertIfDialog_C3 = QtWidgets.QCheckBox()'''
        self.insertIfDialog_OK = QtWidgets.QPushButton('OK')
        
        
        self.insertIfDialog_Layout = QtWidgets.QGridLayout()
        self.insertIfDialog_Layout.addWidget(self.insertIfDialog_L1, 0,0)
        self.insertIfDialog_Layout.addWidget(self.insertIfDialog_T1, 0,1)
        self.insertIfDialog_Layout.addWidget(self.insertIfDialog_L2, 1,0)
        self.insertIfDialog_Layout.addWidget(self.insertIfDialog_T2, 1,1)
        
        self.insertIfDialog_Layout.addWidget(self.insertIfDialog_L3, 2,0)
        
        self.insertIfDialog_Layout.addWidget(self.insertIfDialog_OK, 3,0)
        
        self.insertIfDialog_.setLayout(self.insertIfDialog_Layout)
        self.insertIfDialog_.show()
        self.insertIfDialog_OK.clicked.connect(self.insertIf)
    
    def insertIf(self):
        newIf = self.ifCode.replace('INSERT', self.insertIfDialog_T1.text())
        newElif = self.elifCode.replace('INSERT', self.insertIfDialog_T2.text())
        
        fullThing = newIf + newElif + self.elseCode
        
        self.insertIfDialog_.hide()
        cursor = self.textedit.edit.textCursor()
        
        line=cursor.block().text()
        ind=len(line)-len(line.lstrip('\t'))
        
        cursor.insertText(fullThing.replace('\n', '\n' + ''.join(['\t' for x in range(ind)])))      
        
        
        
    def insertFunctionDialog(self):
        self.functionCode = """def function():\n\tpass"""
        
        self.insertFunctionDialog = QtWidgets.QDialog()
        self.insertFunctionDialog_L = QtWidgets.QLabel('Set a function name:')
        self.insertFunctionDialog_T = QtWidgets.QLineEdit('function')
        self.insertFunctionDialog_OK = QtWidgets.QPushButton('OK')
        
        
        self.insertFunctionDialog_Layout = QtWidgets.QVBoxLayout()
        self.insertFunctionDialog_Layout.addWidget(self.insertFunctionDialog_L)
        self.insertFunctionDialog_Layout.addWidget(self.insertFunctionDialog_T)
        self.insertFunctionDialog_Layout.addWidget(self.insertFunctionDialog_OK)
        
        self.insertFunctionDialog.setLayout(self.insertFunctionDialog_Layout)
        self.insertFunctionDialog.show()
        self.insertFunctionDialog_OK.clicked.connect(self.insertFunction)
        
    def insertFunction(self):
        self.insertFunctionDialog.hide()
        functionCodeReplace = self.functionCode.replace('function', self.insertFunctionDialog_T.text())
        cursor = self.textedit.edit.textCursor()
            
        line=cursor.block().text()
        ind=len(line)-len(line.lstrip('\t'))
        
        cursor.insertText(functionCodeReplace.replace('\n', '\n' + ''.join(['\t' for x in range(ind)])))
    #cursor.movePosition(QtGui.QTextCursor.Up, QtGui.QTextCursor.MoveAnchor, 1)
    #cursor.select(QtGui.QTextCursor.WordUnderCursor)
    #self.textedit.edit.setTextCursor(cursor)
    
    def insertClassDialog(self):
        self.classCode = """class thing():\n\tdef __init__(self, parent=None):\n\t\tsuper(thing, self).__init__()"""
        
        self.insertClassDialog = QtWidgets.QDialog()
        self.insertClassDialog_L = QtWidgets.QLabel('Set a class name:')
        self.insertClassDialog_T = QtWidgets.QLineEdit('EmptyClass')
        self.insertClassDialog_OK = QtWidgets.QPushButton('OK')
        
        
        self.insertClassDialog_Layout = QtWidgets.QVBoxLayout()
        self.insertClassDialog_Layout.addWidget(self.insertClassDialog_L)
        self.insertClassDialog_Layout.addWidget(self.insertClassDialog_T)
        self.insertClassDialog_Layout.addWidget(self.insertClassDialog_OK)
        
        self.insertClassDialog.setLayout(self.insertClassDialog_Layout)
        self.insertClassDialog.show()
        self.insertClassDialog_OK.clicked.connect(self.insertClass)        
        
    def insertClass(self):
        self.insertClassDialog.hide()
        classCodeReplace = self.classCode.replace('thing', self.insertClassDialog_T.text())
        cursor = self.textedit.edit.textCursor()
        
        line=cursor.block().text()
        ind=len(line)-len(line.lstrip('\t'))
        
        cursor.insertText(classCodeReplace.replace('\n', '\n' + ''.join(['\t' for x in range(ind)])))

    
    def sendDweeps_(self, pos, charsRemoved, charsAdded):
        global IRCThreadS
        thing = [pos, charsRemoved, charsAdded]
        #IRCThreadS = threading.Thread(None, functools.partial(self.sendDweeps, thing))
        self.changesSaved = False
        if isCollabing:
            #IRCThreadS.start()
            self.sendDweeps(pos, charsRemoved, charsAdded)
        else:
            pass





    def makeTheChanges(self, char, pos, posEnd, type, username):
        print('---\nchar:', char)
        if type == 'DEL': ## deleting
            print('set the cursor to ' + str(pos))

            cursor = self.textedit.edit.textCursor()

            if posEnd != 0:
                cursor.setPosition(int(posEnd))
                cursor.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor, posEnd - pos)
            else:
                cursor.setPosition(int(pos))
                cursor.clearSelection()

            self.textedit.edit.document().blockSignals(True)
            cursor.deleteChar()
            self.textedit.edit.document().blockSignals(False)


            cursorRect = self.textedit.edit.cursorRect(cursor)

            x = float(cursorRect.x())
            y = float(cursorRect.y()) 
            width = float(cursorRect.width())
            height = float(cursorRect.height())

            newQRectF = QtCore.QRectF(x, y, width + 1, height)

            newBrush = QtGui.QBrush(QtGui.QColor('#0066FF'))
            newPen = QtGui.QPen(QtGui.QColor('#0066FF'))
            self.cursorGS.clear()
            self.cursorGS.addRect(newQRectF, brush=newBrush, pen=newPen)
                      
        elif type == 'PONG':
            self.connectionWindow.hide()

        elif type == 'MOVE':
            cursor = self.textedit.edit.textCursor()
            cursor.setPosition(int(pos))     
            cursorRect = self.textedit.edit.cursorRect(cursor)

            x = float(cursorRect.x())
            y = float(cursorRect.y()) 
            width = float(cursorRect.width())
            height = float(cursorRect.height())

            newQRectF = QtCore.QRectF(x, y, width + 1, height)

            newBrush = QtGui.QBrush(QtGui.QColor('#0066FF'))
            newPen = QtGui.QPen(QtGui.QColor('#0066FF'))
            self.cursorGS.clear()
            self.cursorGS.addRect(newQRectF, brush=newBrush, pen=newPen)

            #self.cursorGS.addRect(QtCore.QRectF(0,0,300,300))
        elif type == 'ADD': ## adding
            print('set the cursor to ' + str(pos) + ', add the character \'' + char + '\'')
            cursor = self.textedit.edit.textCursor()
            cursor.setPosition(int(pos))
            cursor.clearSelection()

            if char == 'SPACE': char = ' '
            if char == "RETURN": char = """
"""
                       
            self.textedit.edit.document().blockSignals(True)
            cursor.insertText(char)           
            self.textedit.edit.document().blockSignals(False)


            cursorRect = self.textedit.edit.cursorRect(cursor)

            x = float(cursorRect.x())
            y = float(cursorRect.y()) 
            width = float(cursorRect.width())
            height = float(cursorRect.height())

            newQRectF = QtCore.QRectF(x, y, width + 1, height)

            newBrush = QtGui.QBrush(QtGui.QColor('#0066FF'))
            newPen = QtGui.QPen(QtGui.QColor('#0066FF'))
            self.cursorGS.clear()
            self.cursorGS.addRect(newQRectF, brush=newBrush, pen=newPen)


        elif type == 'MSG':
            self.dockWidget_TextBox.addItem('<' + username + '>' + char)

    def sendDweeps(self, pos, charsRemoved, charsAdded):
        #print(thing)
        #position = thing[0]
        #charsRemoved = thing[1]
        #charsAdded = thing[2]
        global username, partnerUsername
        cursor = self.textedit.edit.textCursor()
        #cursor.select(QtGui.QTextCursor.WordUnderCursor)
        cursor.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor, 1)
        lastCharacter = cursor.selectedText()
        if lastCharacter == ' ':
            print('Typed a space!')
            lastCharacter = 'SPACE'
        if lastCharacter == """
""":
            print('Typed a return!')
            lastCharacter = 'RETURN'

        print('Last character:', lastCharacter)
        
        cursor.clearSelection()
        
        if charsAdded == 1 or charsRemoved == 1:
            if charsAdded >= 1 and charsRemoved == 0:
                cursor = self.textedit.edit.textCursor()
                cursor.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor, charsAdded)
                lastCharacter = cursor.selectedText()
                if lastCharacter == ' ':
                    print('Typed a space!')
                    lastCharacter = 'SPACE'
                if lastCharacter == """
""":
                    print('Typed a return!')
                    lastCharacter = 'RETURN'
                #if lastCharacter == '\n': print('A new line!')

                if lastCharacter == 'SPACE':
                    self.Command = 'AS ' + str(pos) + ' ' + str(lastCharacter)
                elif lastCharacter == 'RETURN':
                    self.Command = 'AR ' + str(pos) + ' ' + str(lastCharacter)
                else:
                    self.Command = 'A ' + str(pos) + ' ' + str(lastCharacter)
            elif charsAdded == 0 and charsRemoved >= 1:
                if charsRemoved > 1:
                    self.Command = 'R! ' + str(self.textedit.edit.cursor().selectionStart()) + ' ' + str(self.textedit.edit.cursor().selectionEnd())
                else:
                    self.Command = 'R ' + str(pos)

            #if username != partnerUsername:
            print('Dweeting for \'boa_editor_' + pastebin_code + '\' under the username \'' + username + '\', and with the code \'' + self.Command + '\'')
            dweepy.dweet_for('boa_editor_' + pastebin_code, {'command': self.Command, 'person': username})
            #else:
                #print('oh no, it\'s me!')
                
        else:
            pass
        



    def returnChangedText(self, position, charsRemoved=0, charsAdded=0):
        if charsAdded == 1 and charsRemoved == 0:
            self.Command = 'A ' + str(position) + ' ' + str(charsAdded)
        elif charsAdded == 0 and charsRemoved == 1:
            self.Command = 'R ' + str(position) + ' ' + str(charsRemoved)
            
        else: 
            pass
        
        print(self.Command)
        return
        
        
        
    def toggleCompletion(self):
        if self.completeAction.isChecked():
            self.textedit.edit.setCompleter(self.completer)
        else:
            self.textedit.edit.setCompleter(QtWidgets.QCompleter(self))

    def toggleSyntax(self):
        if self.syntaxAction.isChecked():
            self.syntax = syntax.PythonHighlighter(self.textedit.edit)
        else:
            self.syntax = syntax.NullHighlighter(self.textedit.edit)


    def goToDef(self):
        
        text = self.statusBar_FunctionList.currentText()
        #text = self.FunctionList[index]
        lineno = int(str(text).split(' - ')[0])
        
        print(lineno)
        textCursor = self.textedit.edit.textCursor()
        block = self.textedit.edit.document().findBlockByLineNumber(lineno)
        textCursor.setPosition(block.position())
        self.textedit.edit.setTextCursor(textCursor)

    def openFile(self):
        fileToOpen = QtWidgets.QFileDialog.getOpenFileName(self, "Choose a File", '', ('Python Scripts (*.py);;All Files (*)'))[0]
        filename = fileToOpen.split("/")[-1]
        
        fo = open(fileToOpen, 'r')
        fileContents = fo.read()
        self.textedit.edit.setPlainText(fileContents)
    
    def newFile(self):
        self.textedit.edit.setPlainText('')
        
        
    def saveFile(self):
        pathToSave = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", '', ('Python Scripts (*.py);;All Files (*)'))
        
        actualFile = pathToSave[0]
        openFile = open(actualFile, 'w')

        openFile.write(self.textedit.edit.toPlainText())
        openFile.close()

        self.changesSaved = True
    
    def checkforHighlight(self, position, charsRemoved, charsAdded):
        """
        not actually for highlighting!
        """
        #wordsInCode = self.textedit.edit.toPlainText().split(' ')
        
        #everythingToRecognize = stuffToRecognize + wordsInCode
        
        #print(everythingToRecognize)
        
        
        #self.completer.setModel(QtCore.QStringListModel(everythingToRecognize))
        
        #self.textedit.edit.completer.setModel(model)
        
        carrot = 5
        
        self.statusBar_FunctionList.clear()
        self.textCursor = self.textedit.edit.textCursor()
        #self.textCursor.select(QtGui.QTextCursor.WordUnderCursor)
        self.textCursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor)
        currentWord = self.textCursor.selectedText()
        #print(currentWord)
        
        #print('Chars Added: ' + str(charsAdded) + '\nChars Removed: ' + str(charsRemoved))
        
        
        numberOfLines = len(self.textedit.edit.toPlainText().split('\n'))
        self.statusBar_Lines.setText(str(numberOfLines) + ' lines')
        
        FunctionList = []
        everyLineList = self.textedit.edit.toPlainText().split('\n')
        for item in everyLineList:
            print(item.lstrip().replace('#', '').replace(' ', '').replace('\t', '')[:4])
            if item.lstrip()[:3] == 'def': ### it's a function

                FunctionList.append(str(everyLineList.index(item) + 1) + ' - ' + item.replace(':', ''))

            elif item.lstrip()[:5] == 'class': ### it's a class
                FunctionList.append(str(everyLineList.index(item) + 1) + ' - ' + item.replace(':', ''))

            '''elif item.lstrip().replace('#', '').replace(' ', '').replace('\t', '')[:4] == 'TODO':
                #itemA = QtWidgets.QComboBoxItem(str(everyLineList.index(item) + 1) + ' - ' + item)
                #itemA.setItemData(0, QtGui.QFont('Helvetica Neue', bold=True), Qt.FontRole)
                print('It\'s a todo!')
                FunctionList.append(item.lstrip().replace('#', ''))'''





        
        for item in FunctionList:
            print(item.split(' - ')[1].replace('\t', '').replace('    ', '')[:3])
            '''if item[:4] == 'TODO':
                self.statusBar_FunctionList.addItem(item)'''
            if item.split(' - ')[1][:5] == 'class':
                self.statusBar_FunctionList.addItem(QtGui.QIcon('class icon.png'), item)
            elif item.split(' - ')[1].replace('\t', '').replace('    ', '')[:3] == 'def':
                self.statusBar_FunctionList.addItem(QtGui.QIcon('function icon.png'), item)
                


        #print(FunctionList)
        self.FunctionList = FunctionList
        if completeParentheses:
            self.textedit.edit.document().blockSignals(True)
            if charsAdded == 1 and charsRemoved == 0 and currentWord in ['\'', '\"', '(', '[', '{']:
                if currentWord == '\'':
                    #self.textCursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, 1)
                    #nextChar = self.textCursor.selectedText()
        
                    '''if nextChar == "\'":
                        print('Already a quote here!')
                        self.textedit.edit.moveCursor(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor)
                        return
                    else:'''
                    self.textCursor.setKeepPositionOnInsert(True)
                    self.textCursor.movePosition(QtGui.QTextCursor.Right)
                    self.textCursor.insertText('\'')
                    self.textCursor.setKeepPositionOnInsert(False)

                    
            
                elif currentWord == '\"':
                    #self.textCursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, 1)
                    #nextChar = self.textCursor.selectedText()
            
                    '''if nextChar == '\"':
                        print('Already a quote here!')
                        self.textedit.edit.moveCursor(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor)
                        return
                    else:
                        print('no quote here')'''
                    self.textCursor.setKeepPositionOnInsert(True)
                    self.textCursor.movePosition(QtGui.QTextCursor.Right)
                    self.textCursor.insertText('\"')
                    self.textCursor.setKeepPositionOnInsert(False)

                        
                
                elif currentWord == '(':
                    self.textCursor.setKeepPositionOnInsert(True)
                    self.textCursor.movePosition(QtGui.QTextCursor.Right)
                    self.textCursor.insertText(')')
                    self.textCursor.setKeepPositionOnInsert(False)

                        

                elif currentWord == '[':
                    self.textCursor.setKeepPositionOnInsert(True)
                    self.textCursor.movePosition(QtGui.QTextCursor.Right)
                    self.textCursor.insertText(']')
                    self.textCursor.setKeepPositionOnInsert(False)

                          

                elif currentWord == '{':
                    self.textCursor.setKeepPositionOnInsert(True)
                    self.textCursor.movePosition(QtGui.QTextCursor.Right)
                    self.textCursor.insertText('}')
                    self.textCursor.setKeepPositionOnInsert(False)
                    
                    

                self.textedit.edit.moveCursor(QtGui.QTextCursor.Left, QtGui.QTextCursor.MoveAnchor)
            
                #self.textedit.edit.setTextCursor(self.textCursor)
                

        listofLines = self.textedit.edit.toPlainText().split('\n')
        for item in listofLines:
            if 'time.sleep' in item:
            #self.highlightLineNew(listofLines.index(item))
                self.highlightLineNew(stuff=[listofLines.index(item), 'white', False])
        
        self.textedit.edit.document().blockSignals(False)
    
    '''def highlightLine(self, index):
        index = index
        block = self.textedit.edit.document().findBlockByLineNumber(index)
        
        diff = index - block.firstLineNumber()
        count = 0
        if diff == 0:
            line_len = len(block.text().split("\n")[0])
        else:
            # Probably don't need. Just in case a block has more than 1 line.
            line_len = 0
            for i, item in enumerate(block.text().split("\n")):
                # Find start
                if i + 1 == diff: # + for line offset. split starts 0
                    count += 2 # \n
                    line_len = len(item)
                else:
                    count += len(item)
        loc = block.position() + count
        cursor = self.textedit.edit.textCursor()

        cursor.setPosition(loc)
        cursor.movePosition(cursor.Right, cursor.KeepAnchor, line_len)
    
        charf = block.charFormat()
        charf.setBackground(QtGui.QColor(255,153,153)) # Change formatting here
        cursor.setCharFormat(charf)'''

    def highlightLineNew(self, stuff=[0, 'red', False]):
        extra_selections = []
        
        selection = self.textedit.edit.ExtraSelection()
        
        errorLineNo = stuff[0]
        color = stuff[1]
        wholeThing = stuff[2]
        if color == 'white':
            line_color = QtGui.QColor(255,255,255,0)
        elif color == 'red':
            line_color = QtGui.QColor(121,0,0)
        
        
        selection.format.setBackground(line_color)
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)

        if not wholeThing:
            selection.cursor = QtGui.QTextCursor(self.textedit.edit.document().findBlockByLineNumber(errorLineNo -1))
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        else:
            selection.cursor = QtGui.QTextCursor(self.textedit.edit.document())
            selection.cursor.clearSelection()
            extra_selections.append(selection)        

        self.textedit.edit.setExtraSelections(extra_selections)


    def runCode(self):
        code = self.textedit.edit.toPlainText()
        error = False
        
        
        
        with open('temp', 'w') as file:
            file.write(code)
        
        with tempfile.TemporaryFile() as tempf:
            with tempfile.TemporaryFile() as tempf_ex:
                #output = subprocess.Popen(['python3', 'temp'], stdout=tempf, stderr=tempf)
                output = subprocess.Popen(['python3',  '-u', 'temp',], stdout=tempf)
                #os.killpg(output.pid, signal.SIGTERM)
                try:

                    output_ex = subprocess.check_output(['python3', '-u', 'temp'], stderr=tempf_ex)
                    #output.wait()
                    tempf.seek(0)
                    
                    output = str(tempf.read())[2:-3].replace('\\n', '\n').replace("\\'", "\'").replace('\\"', '\"')
                    self.terminalArea.setTextColor(QtGui.QColor(0,0,0))
                    self.terminalArea.setPlainText(output)
                except subprocess.CalledProcessError as e:
                    print('Oops, an exception!')
                    

                    output_ex = subprocess.Popen(['python3', 'temp'], stderr=tempf_ex)
                    #output_ex.wait()
                    tempf_ex.seek(0)
                    
                    error = True
            
                
                    output_ex = str(tempf_ex.read())[2:-3].replace('\\n', '\n').replace("\\'", "\'").replace('\\"', '\"')

#print('Exception: ' + output_ex)'''
                
                if error: ### it's an error
                    self.terminalArea.setTextColor(QtGui.QColor(239,0,0))
                    self.terminalArea.setPlainText(output_ex)
                    '''with open('debug_before.txt', 'r') as db_file:
                        db = db_file.read()
                    
                    with open('debug_after.txt', 'r') as da_file:
                        da = da_file.read()
                    
                    
                    #debugTemp = tempfile.TemporaryFile()
                    #output_exDebug = subprocess.Popen(['python3', 'debug_before.txt'], stdout=debugTemp)
                    
                    #output_exDebug.wait()
                    #debugTemp.seek(0)
                    
                    #print(debugTemp.read())
                    
                    #exceptionThing = exec(db + '\n\t\t' + code + '\n' + da)
                    #print(exceptionThing)'''


                    if output_ex[:9] == 'Traceback': ## it's a traceback
                        linenumber = int(output_ex.split('\n')[1].split(',')[1].split(' ')[2])
                        print('Error on line ' + str(linenumber) + '!')
                    
                            
                    else:
                        linenumber = int(output_ex.split('\n')[0].split(',')[1].split(' ')[2])
                        print('Error on line ' + str(linenumber) + '!')
                            
                    self.textCursor = self.textedit.edit.textCursor()
                    self.textCursor.select(QtGui.QTextCursor.LineUnderCursor)
                    #self.textCursor.setCharFormat(QtGui.QTextFormat.setBackground(QtGui.QBrush(QtGui.QColor(255,0,0))))
                    self.textedit.edit.setTextCursor(self.textCursor)
                    self.highlightLineNew([linenumber, 'red', False])
                        
                        #self.highlightLine(linenumber)
                        #self.thingy = self.textedit.NumberBar
                        #self.thingy.highlightLine(self.textedit, lineno=linenumber)
                    
                        #errorLine = self.textedit.edit.document().findBlockByLineNumber(linenumber)
                        #print(errorLine.text())
#linenumber = exceptionThing
                else:
                    self.terminalArea.setTextColor(QtGui.QColor(255,255,255))
                    self.highlightLineNew([0,'white', True])
                    self.terminalArea.setPlainText(output)

    def clearTerminal(self):
        self.terminalArea.clear()
        self.terminalArea.setPlainText('')
        
        
    def beginNewSession_C(self):
        self.connectionWindow = QtWidgets.QWidget(self)
        self.connectionWindow.setWindowFlags(Qt.Sheet)
        
        
        self.connectingToInternet_L = QtWidgets.QLabel('Please enter a username.')
        self.connectingToInternet_TE = QtWidgets.QLineEdit()
        
        self.connectingToInternet_X = QtWidgets.QPushButton('Cancel')
        self.connectingToInternet_OK = QtWidgets.QPushButton('Connect')
        
        self.connectingToInternet_X.clicked.connect(self.beginNewSession_C_Close)
        self.connectingToInternet_OK.clicked.connect(self.beginNewSession_C_Step2)
        
        
        self.buttonWidgetL = QtWidgets.QHBoxLayout()
        self.buttonWidgetL.addWidget(self.connectingToInternet_X)
        self.buttonWidgetL.addWidget(self.connectingToInternet_OK)
        
        self.buttonWidgetLW = QtWidgets.QWidget()
        self.buttonWidgetLW.setLayout(self.buttonWidgetL)
        
        self.connectionWindow_L = QtWidgets.QVBoxLayout()
        self.connectionWindow_L.addWidget(self.connectingToInternet_L)
        self.connectionWindow_L.addWidget(self.connectingToInternet_TE)
        self.connectionWindow_L.addWidget(self.buttonWidgetLW)
        
        self.connectionWindow.setLayout(self.connectionWindow_L)
        self.connectionWindow.show()
        
        
    def beginNewSession_C_Close(self):
        self.connectionWindow.hide()



        
        
    def beginNewSession_C_Step2(self):
        ### TODO: This
        global isCollabing, pastebin_code, username
        initial_text = self.textedit.edit.toPlainText()
        pastebin_code = self.makeAPaste(initial_text)[24:]
        username = self.connectingToInternet_TE.text()
        self.username = username
        print('My username is ' + username)
        print(pastebin_code)
        dweepy.dweet_for('boa_editor_' + pastebin_code, {'command': 'init ' + pastebin_code, 'person': username})

        self.connectingToInternet_L.setText('Connected! Please give your partner this ID to enter:')
        self.collabStatusLabel.setText('Current Status: Waiting for Partner')

        self.completeAction.setChecked(False)
        self.completeAction.setEnabled(False)
        self.parenthesesAction.setChecked(False)
        self.parenthesesAction.setEnabled(False)

        isCollabing = True
        self.connectingToInternet_CodeLabel = QtWidgets.QLineEdit(pastebin_code)
        self.connectingToInternet_CodeLabel.setReadOnly(True)
        self.connectingToInternet_CodeLabel.setStyleSheet('''QLineEdit {font-size: 24px; height: 28;}''')
        self.connectingToInternet_CodeLabel.setMinimumHeight(30)
        self.connectingToInternet_CodeLabel.setAlignment(Qt.AlignHCenter)

        self.connectingToInternet_OK_After = QtWidgets.QPushButton('OK')
        self.connectingToInternet_OK_After.clicked.connect(self.beginNewSession_C_Close)

        self.connectionWindow_L.addWidget(self.connectingToInternet_CodeLabel, 1)
        self.connectionWindow_L.addWidget(self.connectingToInternet_OK_After, 2)

        self.connectingToInternet_TE.hide()
        self.connectingToInternet_OK.hide()
        self.connectingToInternet_X.hide()

        IRCThread.start()

        self.makeChatWindow()

    def makeChatWindow(self):
        self.chatWindow = QtWidgets.QDockWidget('Chat')

        self.chatWindow.setStyleSheet("""QDockWidget::title {background-color: #333333; text-align: center; border-top: 1px solid #555555;} QDockWidget {color: white;}
            QPushButton {background-color: #343434; color: white; border-radius: 5px; padding-top: 4px; padding-right: 6px; padding-left: 6px; padding-bottom: 4px;}
            QPushButton::pressed {background-color: #1e1e1e;}
            QTextEdit {""")
        self.chatWindow.setWindowTitle('Chat')

        self.dockWidget_TextBox = QtWidgets.QListWidget()
        self.dockWidget_TextBox.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.chatWindow.setStyleSheet('''QListWidget {font-family: 'Courier'; background-color: #343434; color: white; border-radius: 6px; border: 1px solid #5a5a5a;}
            QLineEdit {background-color: #343434; color: white; border-radius: 6px; border: 1px solid #5a5a5a;} QLabel {color: white;}''')
        #self.dockWidget_TextBox.setReadOnly(True)

        self.dockWidget_UsernameBox = QtWidgets.QLabel(self.username)
        self.dockWidget_EntryBox = QtWidgets.QLineEdit()
        self.dockWidget_EntryBox.setPlaceholderText('Write something!')
        self.dockWidget_EntryBox.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.dockWidget_EntryBox.returnPressed.connect(self.sendMessage)

        self.dockWidget_OverallLayout = QtWidgets.QVBoxLayout()
        self.dockWidget_OverallLayout.addWidget(self.dockWidget_TextBox)

        self.dockwidget_BottomLayout = QtWidgets.QHBoxLayout()
        self.dockwidget_BottomLayout.addWidget(self.dockWidget_UsernameBox)
        self.dockwidget_BottomLayout.addWidget(self.dockWidget_EntryBox)

        self.dockwidget_BottomLayoutW = QtWidgets.QWidget()
        self.dockwidget_BottomLayoutW.setLayout(self.dockwidget_BottomLayout)

        self.dockWidget_OverallLayout.addWidget(self.dockwidget_BottomLayoutW)

        self.dockWidget_OverallLayoutW = QtWidgets.QWidget()
        self.dockWidget_OverallLayoutW.setLayout(self.dockWidget_OverallLayout)
        self.chatWindow.setWidget(self.dockWidget_OverallLayoutW)


        self.addDockWidget(Qt.RightDockWidgetArea, self.chatWindow)
        #self.chatWindow.show()
        #self.dockWidget_OverallLayoutW.show()


    def sendMessage(self):
        dweepy.dweet_for('boa_editor_' + pastebin_code, {'command': 'MSG ' + self.dockWidget_EntryBox.text(), 'person': username})
        self.dockWidget_EntryBox.setText('')


    def makeAPaste(self, code):
        if code == '': code = '__NULL__'
        #argv = { 'api_paste_code' : str(code), 'api_option': 'paste', 'api_dev_key': 'edb9e6eff8e81c5f2df47a2bb6547045'}
        argv = {'code': code, 'lexer': 'text', 'expiry': '1day'}
        r = requests.post('https://bpaste.net', data=argv)
        print(r.url)
        return r.url



    def connectToSession_C(self):
        self.connectionWindow = QtWidgets.QWidget(self)
        self.connectionWindow.setWindowFlags(Qt.Sheet)
        
        
        self.connectingToInternet_L = QtWidgets.QLabel('Please enter a username.')
        self.connectingToInternet_TE = QtWidgets.QLineEdit()

        self.connectingToInternet_L2 = QtWidgets.QLabel('Please enter the host\'s ID.')
        self.connectingToInternet_TE2 = QtWidgets.QLineEdit()       
        
        self.connectingToInternet_X = QtWidgets.QPushButton('Cancel')
        self.connectingToInternet_OK = QtWidgets.QPushButton('Connect')
        
        self.connectingToInternet_X.clicked.connect(self.beginNewSession_C_Close)
        self.connectingToInternet_OK.clicked.connect(self.connectToSession_C_Step2)
        
        
        self.buttonWidgetL = QtWidgets.QHBoxLayout()
        self.buttonWidgetL.addWidget(self.connectingToInternet_X)
        self.buttonWidgetL.addWidget(self.connectingToInternet_OK)
        
        self.buttonWidgetLW = QtWidgets.QWidget()
        self.buttonWidgetLW.setLayout(self.buttonWidgetL)
        
        self.connectionWindow_L = QtWidgets.QVBoxLayout()

        self.connectionWindow_L.addWidget(self.connectingToInternet_L)
        self.connectionWindow_L.addWidget(self.connectingToInternet_TE)
        self.connectionWindow_L.addWidget(self.connectingToInternet_L2)
        self.connectionWindow_L.addWidget(self.connectingToInternet_TE2)

        self.connectionWindow_L.addWidget(self.buttonWidgetLW)
        
        self.connectionWindow.setLayout(self.connectionWindow_L)
        self.connectionWindow.show()


    def connectToSession_C_Step2(self):
        global isCollabing, username, pastebin_code
        self.connectingToInternet_X.setEnabled(False)
        self.connectingToInternet_OK.setEnabled(False)
        paste_url = 'https://bpaste.net/raw/' + self.connectingToInternet_TE2.text()

        r = requests.get(paste_url)
        
        if r.status_code == 404:
            self.connectToSession_C_InvalidCode()
        else:
            print('Success: ' + r.text)

            text = r.text
            if text == '__NULL__': text = ''
            pastebin_code = self.connectingToInternet_TE2.text()
            username = self.connectingToInternet_TE.text()
            self.username = username
            print('My username is ' + username)
            self.textedit.edit.setPlainText(text)

            dweepy.dweet_for('boa_editor_' + pastebin_code, {'command': 'PING', 'person': username})
            print('We ping\'d em!')

            self.connectionWindow.hide()
            self.collabStatusLabel.setText('Current Status: Connected\nCode is ' + pastebin_code)
            isCollabing = True
            IRCThread.start()

            self.makeChatWindow()



    def connectToSession_C_InvalidCode(self):
        self.connectingToInternet_TE2.setStyleSheet('''QLineEdit {background-color: #FFCCCC;}''')

class LineTextWidget(QtWidgets.QFrame):
 
    class NumberBar(QtWidgets.QWidget):
 
        def __init__(self, *args):
            QtWidgets.QWidget.__init__(self, *args)
            self.edit = None
            self.setStyleSheet("""QWidget {color: white;}""")
            # This is used to update the width of the control.
            # It is the highest line that is currently visibile.
            self.highest_line = 0
 
        def setTextEdit(self, edit):
            self.edit = edit
 
        def update(self, *args):
            '''
            Updates the number bar to display the current set of numbers.
            Also, adjusts the width of the number bar if necessary.
            '''
            # The + 4 is used to compensate for the current line being bold.
            width = self.fontMetrics().width(str(self.highest_line)) + 4
            if self.width() != width:
                self.setFixedWidth(width)
            QtWidgets.QWidget.update(self, *args)
 
        def paintEvent(self, event):
            contents_y = self.edit.verticalScrollBar().value()
            page_bottom = contents_y + self.edit.viewport().height()
            font_metrics = self.fontMetrics()
            current_block = self.edit.document().findBlock(self.edit.textCursor().position())
 
            painter = QtGui.QPainter(self)
 
            line_count = 0
            # Iterate over all text blocks in the document.
            block = self.edit.document().begin()
            while block.isValid():
                line_count += 1
 
                # The top left position of the block in the document
                position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()
 
                # Check if the position of the block is out side of the visible
                # area.
                if position.y() > page_bottom:
                    break
 
                # We want the line number for the selected line to be bold.
                bold = False
                if block == current_block:
                    bold = True
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
 
                # Draw the line number right justified at the y position of the
                # line. 3 is a magic padding number. drawText(x, y, text).
                painter.drawText(self.width() - font_metrics.width(str(line_count)) - 3, round(position.y()) - contents_y + font_metrics.ascent(), str(line_count))
 
                # Remove the bold style if it was set previously.
                if bold:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)
 
                block = block.next()
 
            self.highest_line = line_count
            painter.end()
 
            QtWidgets.QWidget.paintEvent(self, event)
 
        def highlightLine(self, lineno):
            
            numberOfLines = len(self.edit.toPlainText().split('\n'))
            
            for line in range(numberOfLines):
                possible_error_block = self.edit.document().findBlockByLineNumber(line)
                error_block = self.edit.document().findBlockByLineNumber(lineno)
                error_block_T = error_block.text()

                red = False
                if possible_error_block == error_block:
                        painter = QtGui.QPainter(self)
                        red = True
                        font = painter.font()
                        font.setBold(True)
                        font.setBackground(QtGui.QColor(255, 0,0))
                        painter.setFont(font)


    def __init__(self, *args):
        QtWidgets.QFrame.__init__(self, *args)
 
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Sunken)
 
        self.setStyleSheet('''QFrame {border: 0;}''')
        self.edit = TextEdit()
        self.edit.setFontFamily('Courier')
        self.edit.setStyleSheet('''QTextEdit {font-family: 'Courier'; background-color: #343434; color: white; border-radius: 6px; border: 1px solid #5a5a5a;}''')
        self.edit.setFrameStyle(QtWidgets.QFrame.NoFrame)
        #self.edit.setAcceptRichText(False)
 
 
        self.number_bar = self.NumberBar()
        self.number_bar.setTextEdit(self.edit)
 
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.setSpacing(0)
        #hbox.setMargin(0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)

        self.edit.installEventFilter(self)
        self.edit.viewport().installEventFilter(self)
    
        self.edit.setTabStopWidth(30)
 
    def eventFilter(self, object, event):
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary singals.
        if object in (self.edit, self.edit.viewport()):
            self.number_bar.update()
            return False
        return QtWidgets.QFrame.eventFilter(object, event)
 
    def getTextEdit(self):
        return self.edit


class TextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)

        self._completer = None

    def setCompleter(self, c):
        if self._completer is not None:
            self._completer.activated.disconnect()

        self._completer = c

        c.setWidget(self)
        c.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        c.setCaseSensitivity(Qt.CaseInsensitive)
        c.setModelSorting(QtWidgets.QCompleter.UnsortedModel)
        c.activated.connect(self.insertCompletion)

    def completer(self):
        return self._completer

    def insertCompletion(self, completion):
        if self._completer.widget() is not self:
            return

        tc = self.textCursor()
        extra = len(completion) - len(self._completer.completionPrefix())
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)

        return tc.selectedText()

    def focusInEvent(self, e):
        if self._completer is not None:
            self._completer.setWidget(self)

        super(TextEdit, self).focusInEvent(e)

    def keyPressEvent(self, e):
        k=e.key()
        cur=self.textCursor()
        
        cur.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, 1)
        nextChar = cur.selectedText()
        
        if nextChar == '"' or nextChar == "'":
            print('Already a quote here!')
            e.ignore()
        if cur.hasSelection():
            pass
        

        '''elif k==Qt.Key_Return:
            #if e.Qt.NoModifier
            line=cur.block().text()
            ind=len(line)-len(line.lstrip('\t'))
            if line.strip().endswith(':') and cur.positionInBlock()==len(line):
                ind+=1
            #cur.beginEditBlock()
            cur.insertText('\r')
            if ind:
                cur.insertText('\t'*ind)
                #cur.insertText('\r\t')
            #cur.endEditBlock()
            self.ensureCursorVisible()


            #cur.deletePreviousChar()
            e.ignore()'''

        ### completer begins here       
        if self._completer is not None and self._completer.popup().isVisible():
            # The following keys are forwarded by the completer to the widget.
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                e.ignore()
                # Let the completer do default behavior.
                return

        isShortcut = ((e.modifiers() & Qt.ControlModifier) != 0 and e.key() == Qt.Key_F5)
        #isShortcut = True
        if self._completer is None or not isShortcut:
            # Do not process the shortcut when we have a completer.
            super(TextEdit, self).keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if self._completer is None or (ctrlOrShift and len(e.text()) == 0):
            return

        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="
        hasModifier = (e.modifiers() != Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self.textUnderCursor()

        print(completionPrefix)
        if not isShortcut and (hasModifier or len(e.text()) == 0 or len(completionPrefix) < 3 or e.text()[-1] in eow):
            self._completer.popup().hide()
            return

        if completionPrefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completionPrefix)
            self._completer.popup().setCurrentIndex(
                    self._completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self._completer.popup().sizeHintForColumn(0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cr)


class TextEditor_CustomContext(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super(TextEditor_CustomContext, self).__init__(parent)
        print('wewe')
    def contextMenuEvent(self, e):
        QtWidgets.QTextEdit.contextMenuEvent(self, e)
        
        self.contextMenu = QtWidgets.QMenu()
        self.menu.addAction('hello', self.derp)
        self.menu.exec_(e.screenPos())

    def derp(self):
        print('derp')

class SpecialThread(QtCore.QThread):
    #### http://www.saltycrane.com/blog/2008/01/pyqt-how-to-pass-arguments-while/
    thingSignal = QtCore.pyqtSignal(str, int, int, str, str)

    def run(self):
        global username
        print('dweeps', username)
        while True:
            for dweet in dweepy.listen_for_dweets_from('boa_editor_' + pastebin_code, timeout=9999):
                dweet = dweet['content']
                print('My username is ' + username + ', and I think my partner\'s username is ' + dweet['person'])

                if dweet['command'][:3] == 'MSG':
                    message = dweet['command'][3:]

                    self.thingSignal.emit(message, 0, 0, 'MSG', dweet['person'])

                elif dweet['person'] != username:
                    #partnerUsername = dweet['person']
                    print('Just got a dweet from my partner. It says:', dweet)
                    if dweet['command'][:1] == 'A':
                        parsedDweet = dweet['command'][1:].split(' ')
                        print('Parsed: ' + str(parsedDweet))
                        cursorPos = int(parsedDweet[1])
                        print('Cursor pos: ' + str(cursorPos))

                        if dweet['command'][1] == 'S':
                            character = 'SPACE'
                        elif dweet['command'][1] == 'R':
                            character = 'RETURN'
                        else:
                            character = ' '.join(parsedDweet[2:])

                        self.thingSignal.emit(character, cursorPos, 0, 'ADD', '')

                    elif dweet['command'][:1] == 'R':
                        if dweet['command'][1] == '!':
                            parsedDweet = dweet['command'][2:].split(' ')
                            cursorPosB = int(parsedDweet[1])
                            cursorPosE = int(parsedDweet[2])

                            self.thingSignal.emit('', cursorPosB, cursorPosE, 'DEL', '')




                    elif dweet['command'][:1] == 'M':
                        parsedDweet = dweet['command'][1:].split(' ')

                        cursorPos = int(parsedDweet[1])

                        self.thingSignal.emit('', cursorPos, 0, 'MOVE', '')

                    elif dweet['command'] == 'PING': ### we're getting pinged, send a pong
                        print('we\'ve been pinged by ' + dweet['person'])
                        dweepy.dweet_for('boa_editor_' + pastebin_code, {'command': 'PONG', 'person': username})
                        self.thingSignal.emit('', 0,0,'PONG', '')
                        self.finalizeConnection()

                else:
                    print('This dweet is from me! Oops!')





    def finalizeConnection(self):
        #self.collabStatusLabel.setText('Current Status: Connected\nCode is ' + pastebin_code)
        print('we\'re all ready to go! :D')


class DraggableListWidget(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(DraggableListWidget, self).__init__(parent)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setAcceptDrops(True)


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
          event.acceptProposedAction()
        else:
          super(DraggableListWidget, self).dragEnterEvent(event)


    def dragMoveEvent(self, event):
        event.setDropAction(QtCore.Qt.MoveAction)
        super(DraggableListWidget, self).dragMoveEvent(event)

    def dropEvent(self, event):
        self.items = []
        for index in range(self.count()):
            self.items.append(self.item(index).text())


        print(self.items)

        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.path() in self.items:
                    self.addItem(url.path())
            event.acceptProposedAction()
        else:
            if event.mimeData() not in self.items:
                print('not in items!')
                super(DraggableListWidget,self).dropEvent(event)

if __name__ == '__main__':
    global app, window
    app = QtWidgets.QApplication(sys.argv)

    window = Window()
    window.show()
    sys.exit(app.exec_())

    
