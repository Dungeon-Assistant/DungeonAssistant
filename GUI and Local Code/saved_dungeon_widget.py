from PyQt5.QtWidgets import QWidget, QPushButton, QLabel
from PyQt5 import uic
import sys,os, logging

class SavedDungeonWidget(QWidget):
    def __init__(self, parent, dungeon_data, *args, **kwargs):
        super(SavedDungeonWidget, self).__init__(*args, **kwargs)
        uic.loadUi('ui/loadingWidget.ui', self)

        self.parent = parent
        self.dungeon_data = dungeon_data

        self.name_label = self.findChild(QLabel, "nameLabel")
        self.nameLabel.setText(self.dungeon_data.get('name', 'error'))

        self.load_button = self.findChild(QPushButton, "loadButton")
        self.load_button.clicked.connect(self.load)

        self.delete_button = self.findChild(QPushButton, "deleteButton")
        self.delete_button.clicked.connect(self.delete)

    # need to add 'are you sure?' popup
    def delete(self):
        logging.info("Deleting Dungeon named {}".format(self.dungeon_data['name']))
        self.delete_dungeon_data()
        self.setParent(None)


    def load(self):
        self.parent.load_dungeon(self.dungeon_data, self)


    def delete_dungeon_data(self):
        try:
            dungeon = self.dungeon_data['name']
            self.parent.dungeon_list.remove(self.dungeon_data)
            os.remove("generated_dungeons\\"+dungeon+".png")
            
        except ValueError:
            logging.warning("Dungeon named {} was already deleted.".format(self.dungeon_data.get('name', 'error')))
        except FileNotFoundError:
            logging.warning("Dungeon named {} was already deleted.".format(self.dungeon_data.get('name', 'error')))


    def change_dungeon_data(self, dungeon):
        self.delete_dungeon_data()
        self.dungeon_data = dungeon
        self.nameLabel.setText(self.dungeon_data.get('name', 'error'))