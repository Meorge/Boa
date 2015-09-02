"""
Usage:
    cd to it's directory
    python mac_setup.py py2app
"""
# How to get the app bundle to work:
# Once you run this file (as seen above), go to the dist folder -> Reggie Next.app and show the package contents. Inside the Contents folder, paste the PlugIns and Frameworks folders included in the APP-Package-Stuff folder. Next, open the Info.plist in the Contents folder with Xcode and open the PyMainFileNames array, and change the Item 0 String from '__boot__' to 'reggie'. The app bundle should now work. Enjoy!

from setuptools import setup
import os, sys, shutil


NAME = 'Reggie Next ARGV'
VERSION = '1.0'

plist = dict(
    CFBundleIconFile=NAME,
    CFBundleName=NAME,
    CFBundleShortVersionString=VERSION,
    CFBundleGetInfoString=' '.join([NAME, VERSION]),
    CFBundleExecutable=NAME,
    CFBundleIdentifier='RoadrunnerWMCReggie',
)



APP = ['reggie.py']
DATA_FILES = ['reggiedata', 'archive.py', 'common.py', 'license.txt', 'lz77.py', 'readme.md', 'LHTool.py', 'spritelib.py', 'sprites.py', 'prepare_source_dist.py']
OPTIONS = {
 'argv_emulation': True,
'graph': True,
 'iconfile': 'reggiedata/reggie.icns',
 'plist': plist,
 'xref': True,
 'includes': ['sip', 'encodings', 'encodings.hex_codec', 'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQtRibbon', 'TPLLib', 'archives', 'LHTool', 'lz77', 'SARC', 'spritelib', 'sprites', 'base64', 'importlib', 'math', 'os.path', 'pickle', 'struct', 'subprocess', 'threading', 'time', 'urllib.request', 'xml.etree', 'zipfile', 'bdp', 'pdb', 'importlib.machinery', 'operator', 'reprlib', '_weakrefset', 'multiprocessing.connection', 'copy', 'os', 'collections', 'java.lang', 'org.python.core', 'org.python', 'webbrowser', 'platform', 'pkg_resources', 'sys', 'PyQtRibbon.FileMenu', 'PyQtRibbon.RecentFilesManager', 'PyQtRibbon.Ribbon', 'shutil', 'tokenize', 'ctypes.macholib.dyld', 'multiprocessing.reduction', 'functools'],
 'excludes': ['PyQt5.QtWebKit', 'PyQt5.QtDesigner', 'PyQt5.QtNetwork', 'PyQt5.QtOpenGL',
            'PyQt5.QtScript', 'PyQt5.QtSql', 'PyQt5.QtTest', 'PyQt5.QtXml', 'PyQt5.phonon'],
 'compressed': 0,
 'optimize': 0
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
# (1) remove build files

# (2)  issue setup command

# (3) copy plugin
#plugin
print("copy plugins")
os.system("cp -r plugins dist/test.app/Contents/PlugIns")
os.system("cp qt.conf dist/test.app/Contents/Resources/qt.conf")

# (4) correct dylib references

appPath = "/Users/Malcolm/Documents/Reggie Next for Mac/Reggie-Next-master/dist/ReggieNext!.app"
qtPath = "/Applications/Qt/5.4/clang_64/lib"
pythonPath = "/Library/Frameworks/Python.framework/Versions/3.4/Resources/Python.app"

def iid(dylib):
    command = "install_name_tool -id @executable_path/../PlugIns/{dylib} {appPath}/Contents/PlugIns/{dylib}".format(dylib=dylib, appPath=appPath)
    os.system(command)

def icPython(dylib):
    command = "install_name_tool -change {pythonPath}/Python.framework/Versions/3.3/Python @executable_path/../Frameworks/Python.framework/Versions/3.3/Python {appPath}/Contents/PlugIns/{dylib}".format(dylib=dylib, appPath=appPath, pythonPath=pythonPath)
    os.system(command)

def icCore(dylib):
    command = "install_name_tool -change {qtPath}/lib/QtCore.framework/Versions/5/QtCore @executable_path/../Frameworks/QtCore.framework/Versions/5/QtCore {appPath}/Contents/PlugIns/{dylib}".format(dylib=dylib, appPath=appPath, qtPath=qtPath)
    os.system(command)

def update(dylib):
    iid(dylib)
    icPython(dylib)
    icCore(dylib)

#accessible
print("# update accessible")
update("accessible/libqtaccessiblequick.dylib")
update("accessible/libqtaccessiblewidgets.dylib")

#bearer
print("# update bearer")
update("bearer/libqcorewlanbearer.dylib")

#platform
print("# update platforms")
update("platforms/libqcocoa.dylib")   ## <-- you need it
update("platforms/libqminimal.dylib")



