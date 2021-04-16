from PyQt5.QtWidgets import QWidget, QGroupBox, QPushButton, QSizePolicy, QVBoxLayout
import sys, logging

class ButtonBar(QWidget):
    def __init__(self, mainWindow, names, values, *args, **kwargs):
        super(ButtonBar, self).__init__(*args, **kwargs)

        self.groupBox = QGroupBox(self)
        layout = QVBoxLayout()

        self.buttons = list()
        for name, value in zip(names, values):
            button = SelfDisablingButton(self, name, value, mainWindow, self.groupBox)
            self.buttons.append(button)
            layout.addWidget(button._button)

        self.groupBox.setLayout(layout)

        self.groupBox.show()

    def disableAll(self):
        for button in self.buttons:
            button.disable()

        self.setEnabled(False)
        self.groupBox.setEnabled(False)


class SelfDisablingButton(QWidget):
    def __init__(self, bar, name, value, mainWindow, *args, **kwargs):
        super(SelfDisablingButton, self).__init__(*args, **kwargs)
        self.name = name
        self.value = value
        self.bar = bar
        self.mainWindow = mainWindow
        self._button = QPushButton(name, self)
        self._button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self._button.clicked.connect(self.pushed)

    def pushed(self):
        logging.info(self.value)
        self.mainWindow.input.setText(self.value)
        self.mainWindow.send_message()

        self.bar.disableAll()

    def disable(self):
        self.setEnabled(False)
        self._button.setEnabled(True)