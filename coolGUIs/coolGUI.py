from PyQt5 import QtCore, QtMacExtras, QtGui, QtWidgets, QtHelp
Qt = QtCore.Qt


class SearchBox(QtWidgets.QLineEdit):
	"""docstring for SearchBox"""
	def __init__(self):
		super(SearchBox, self).__init__()
		self.setStyleSheet('QLineEdit {padding-left: 17px; padding-right: 24px; background-image: url(\'glass.png\'); background-position: left; background-repeat: no-repeat; height: 24px; border: 0px solid white; border-radius: 5px;}')
		
