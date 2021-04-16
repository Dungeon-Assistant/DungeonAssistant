from PyQt5.QtWidgets import QWidget, QPushButton, QLabel
from PyQt5 import uic
import sys, logging

class SavedNPCWidget(QWidget):
    def __init__(self, parent, npc_data, *args, **kwargs):
        super(SavedNPCWidget, self).__init__(*args, **kwargs)
        uic.loadUi('ui/loadingWidget.ui', self)

        self.parent = parent
        self.npc_data = npc_data

        self.name_label = self.findChild(QLabel, "nameLabel")
        self.nameLabel.setText(self.npc_data.get('name', 'error'))

        self.load_button = self.findChild(QPushButton, "loadButton")
        self.load_button.clicked.connect(self.load)

        self.delete_button = self.findChild(QPushButton, "deleteButton")
        self.delete_button.clicked.connect(self.delete)

    # need to add 'are you sure?' popup
    def delete(self):
        logging.info("Deleting NPC {}\n".format(self.npc_data))
        self.delete_npc_data()
        self.setParent(None)


    def load(self):
        self.parent.load_npc(self.npc_data, self)


    def delete_npc_data(self):
        try:
            self.parent.npc_list.remove(self.npc_data)
        except ValueError:
            logging.warning("NPC named {} was already deleted.".format(self.npc_data.get('name', 'error')))


    def change_npc_data(self, npc):
        self.delete_npc_data()
        self.npc_data = npc
        self.nameLabel.setText(self.npc_data.get('name', 'error'))