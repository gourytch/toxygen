from PySide import QtCore, QtGui
import widgets
import profile
import util


class IncomingCallWidget(widgets.CenteredWidget):

    def __init__(self, friend_number, text, name):
        super(IncomingCallWidget, self).__init__()
        self.resize(QtCore.QSize(500, 270))
        self.avatar_label = QtGui.QLabel(self)
        self.avatar_label.setGeometry(QtCore.QRect(10, 20, 64, 64))
        self.avatar_label.setScaledContents(False)
        self.name = widgets.DataLabel(self)
        self.name.setGeometry(QtCore.QRect(90, 20, 300, 25))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        font.setBold(True)
        self.name.setFont(font)
        self.call_type = widgets.DataLabel(self)
        self.call_type.setGeometry(QtCore.QRect(90, 55, 300, 25))
        self.call_type.setFont(font)
        self.accept_audio = QtGui.QPushButton(self)
        self.accept_audio.setGeometry(QtCore.QRect(20, 100, 150, 150))
        self.accept_video = QtGui.QPushButton(self)
        self.accept_video.setGeometry(QtCore.QRect(170, 100, 150, 150))
        self.decline = QtGui.QPushButton(self)
        self.decline.setGeometry(QtCore.QRect(320, 100, 150, 150))
        pixmap = QtGui.QPixmap(util.curr_directory() + '/images/accept_audio.png')
        icon = QtGui.QIcon(pixmap)
        self.accept_audio.setIcon(icon)
        pixmap = QtGui.QPixmap(util.curr_directory() + '/images/accept_video.png')
        icon = QtGui.QIcon(pixmap)
        self.accept_video.setIcon(icon)
        pixmap = QtGui.QPixmap(util.curr_directory() + '/images/decline_call.png')
        icon = QtGui.QIcon(pixmap)
        self.decline.setIcon(icon)
        self.accept_audio.setIconSize(QtCore.QSize(150, 150))
        self.accept_video.setIconSize(QtCore.QSize(140, 140))
        self.decline.setIconSize(QtCore.QSize(140, 140))
        self.accept_audio.setStyleSheet("QPushButton { border: none }")
        self.accept_video.setStyleSheet("QPushButton { border: none }")
        self.decline.setStyleSheet("QPushButton { border: none }")
        self.setWindowTitle("Toxygen")
        self.name.setText(name)
        self.call_type.setText(text)
        pr = profile.Profile.get_instance()
        self.accept_audio.clicked.connect(lambda: pr.start_call(friend_number, True, False) or self.close())
        # self.accept_video.clicked.connect(lambda: pr.start_call(friend_number, True, True))
        self.decline.clicked.connect(lambda: pr.stop_call(friend_number, False) or self.close())

    def set_pixmap(self, path):
        pixmap = QtGui.QPixmap(QtCore.QSize(64, 64))
        pixmap.load(path)
        self.avatar_label.setPixmap(pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio))

if __name__ == '__main__':
    import sys
    from util import curr_directory
    app = QtGui.QApplication(sys.argv)

    with open(curr_directory() + '/styles/style.qss') as fl:
        dark_style = fl.read()
    app.setStyleSheet(dark_style)
    window = IncomingCallWidget(0, 'Incoming audio call', 'Echobot')
    window.pixmap = QtGui.QPixmap(QtCore.QSize(64, 64))
    window.pixmap.load(curr_directory() + '/images/avatar')
    window.avatar_label.setPixmap(window.pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio))
    window.show()
    app.exec_()
