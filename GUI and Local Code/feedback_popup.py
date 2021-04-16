from PyQt5.QtWidgets import QPushButton, QMainWindow
from PyQt5 import uic
from PyQt5.Qt import QUrl, QDesktopServices
import sys,os, logging

class FeedbackPopup(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(FeedbackPopup, self).__init__(*args, **kwargs)
        uic.loadUi('ui/feedback_nav.ui', self)

        self.bug_button = self.findChild(QPushButton, 'bugButton')
        self.bug_button.clicked.connect(self.bug_report)

        self.general_button = self.findChild(QPushButton, 'feedbackButton')
        self.general_button.clicked.connect(self.general_feedback)


    def bug_report(self):
        logging.info("Loading bug report form")
        self.open_link("https://forms.gle/aPe65vx6qeA1gX7a7")
        self.setParent(None)

    def general_feedback(self):
        logging.info("Loading general feedback form")
        self.open_link("https://forms.gle/uo9tLXDiQzohG7s38")
        self.setParent(None)

    def open_link(self, url):
        logging.info("Directing to <{}>".format(url))

        url = QUrl(url)
        QDesktopServices.openUrl(url)