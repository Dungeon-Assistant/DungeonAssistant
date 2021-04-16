import sys, json, shutil, logging
from datetime import datetime
from ibm_cloud_sdk_core.api_exception import ApiException
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QMainWindow, QPushButton, QLineEdit, 
    QScrollArea, QVBoxLayout, QApplication, QSizePolicy, QComboBox, QSpinBox, QCheckBox, QTextEdit,QTextBrowser)
from PyQt5.QtGui import QPixmap, QMovie, QPixmapCache
from npc_generator.generator.generator import Generator
from watsonAssistant import Assistant
from buttonBar import ButtonBar
from feedback_popup import FeedbackPopup
from saved_npc_widget import SavedNPCWidget
from saved_dungeon_widget import SavedDungeonWidget
from dungeon_generator.callGenerator import makeDungeon,makeEncounters
from dungeon_generator.generateDungeonMap import to_image
from PIL import Image


class MainWindow(QMainWindow):
    def __init__(self, app, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.mainApp = app

        self.assistant = Assistant()
        self.npcGen = Generator()
        self.chatHistory = list()
        
        self.npc_list = list()
        try:
            with open('data/saved_npcs.txt') as npcs_infile:
                self.npc_list = json.load(npcs_infile)
        except OSError:
            logging.warning("Could not open/read file: data/saved_npcs.txt")

        self.dungeon_list = list()
        try:
            with open('data/saved_dungeon.txt') as dungeons_infile:
                self.dungeon_list = json.load(dungeons_infile)
        except OSError:
            logging.warning("Could not open/read file: data/saved_dungeon.txt")
        

        self.current_npc_widget = None

        self.load_main_ui()
        self.send_message() # get welcome message by sending empty message
      
    # --- UI Loading & Unloading ---

    def unload_all(self):
        for child in self.findChildren(QWidget):
            child.setParent(None)


    def connect_nav_buttons(self):
        self.mainMenuButton = self.findChild(QPushButton, 'pushButton')
        self.mainMenuButton.clicked.connect(self.load_main_ui)
        self.npcGenButton = self.findChild(QPushButton, 'pushButton_2')
        self.npcGenButton.clicked.connect(self.load_npcgen_ui)
        self.dungeonGenButton = self.findChild(QPushButton, 'pushButton_3')
        self.dungeonGenButton.clicked.connect(self.load_dungeongen_ui)
        self.feedbackButton = self.findChild(QPushButton, 'pushButton_4')
        self.feedbackButton.clicked.connect(self.load_feedback_menu)
    

    def load_main_ui(self):
        logging.info("Loading main ui")

        self.unload_all()
        uic.loadUi('ui/main.ui', self)
        self.connect_nav_buttons()

        # connect main ui specifics:
        self.enterButton = self.findChild(QPushButton, 'button')
        self.enterButton.clicked.connect(self.send_message)
        self.input = self.findChild(QLineEdit, "input")
        self.input.returnPressed.connect(self.send_message)
        
        self.outputScroll = self.findChild(QScrollArea, "scrollArea")
        self.outputWidget = self.findChild(QWidget, "scrollAreaWidgetContents")
        self.outputLayout = self.findChild(QVBoxLayout, "layoutArea")

        self.outputWidget.setLayout(self.outputLayout)
        self.outputScroll.setWidget(self.outputWidget)

        for widget in self.chatHistory:
            self.add_widget_to_scrollbox(widget, self.outputLayout, self.outputScroll)


    def load_feedback_menu(self):
        logging.info("Loading feedback menu")
        fp = FeedbackPopup(self)
        fp.show()



    # this runs when the window is closed
    def closeEvent(self, event):
        logging.info("Closing Dungeon Assistant")

        with open('data/saved_npcs.txt', 'w') as npc_outfile:
            json.dump(self.npc_list, npc_outfile)
        with open('data/saved_dungeon.txt', 'w') as dungeon_outfile:
            json.dump(self.dungeon_list, dungeon_outfile)


    # --- Dungeon UI Functions ---

    def load_dungeongen_ui(self):
        logging.info("Loading dungeongen ui")

        self.unload_all()
        uic.loadUi('ui/dungeongen.ui', self)
        self.connect_nav_buttons()
        # connect dungeon ui specifics:

        # comboboxes in settings
        self.roomDensityOption = self.findChild(QComboBox, "roomDensityComboBox")
        self.roomSizeOption = self.findChild(QComboBox, "roomSizeComboBox")
        self.floorOption = self.findChild(QSpinBox, "numberOfFloorsSpinBox")
        self.dungeonSizeOption = self.findChild(QComboBox, "dungeonSizeComboBox")
        #encounter generation stuff
        self.encounterTextBox = self.findChild(QTextBrowser,"encounterTextBrowser")
        self.partySizeOption = self.findChild(QSpinBox,"partySizeSpinBox")
        self.partyLevelOption = self.findChild(QSpinBox,"partyLevelSpinBox")
        self.dungeonDifficultyOption = self.findChild(QComboBox,"dungeonDifficultyComboBox")
        self.encounterGenCheckBox = self.findChild(QCheckBox,"encounterGenCheckBox")
        self.encounterGenCheckBox.stateChanged.connect(self.disable_encounter)
        self.encounterGenCheckBox.toggle()
        # generatebutton
        self.generateButton = self.findChild(QPushButton, 'generateButton')
        self.generateButton.clicked.connect(self.generate_dungeon)
        # open image button
        self.openButton = self.findChild(QPushButton, 'OpenImage')
        self.openButton.clicked.connect(self.open_dungeon)
        # save buttons
        self.saveDungeonButton = self.findChild(QPushButton,"saveDungeonPushButton")
        self.saveDungeonButton.clicked.connect(self.save_dungeon)
        #I want to populate this with our default name and the user then can save need to give these 2 names
        self.dungeonName = self.findChild(QLineEdit,"DungeonNameLineEdit")
        # other widgets
        self.prevDungeonScroll = self.findChild(QScrollArea, "prevFloorScrollBox")
        self.prevDungeonWidget = self.findChild(QWidget, "scrollAreaWidgetContents")
        self.prevDungeonLayout = self.findChild(QVBoxLayout, "layoutArea")
        self.prevDungeonScroll.setWidget(self.prevDungeonWidget)
        self.dungeonImageLabel = self.findChild(QLabel, "dungeonImageLabel")
        #current_dungeon keeps track of which dungeon is currently loaded
        self.current_dungeon = {}
        self.temp_dungeon = {}
        self.temp_buttons = []
        for dungeon in self.dungeon_list:
            dungeon_widget = SavedDungeonWidget(self, dungeon, self.prevDungeonWidget)
            self.add_widget_to_scrollbox(dungeon_widget, self.prevDungeonLayout, self.prevDungeonScroll, addToTop=True)
        

    def disable_encounter(self):
        if self.encounterGenCheckBox.isChecked()==True:
            self.partySizeOption.setEnabled(True)
            self.partyLevelOption.setEnabled(True)
            self.dungeonDifficultyOption.setEnabled(True)
        else:
            self.partySizeOption.setEnabled(False)
            self.partyLevelOption.setEnabled(False)
            self.dungeonDifficultyOption.setEnabled(False) 

    # --- NPC UI Functions ---

    def load_npcgen_ui(self):
        logging.info("Loading npcgen ui")

        self.unload_all()
        uic.loadUi('ui/npcgen.ui', self)
        self.connect_nav_buttons()

        # connect npc ui specifics:

        # inputs
        self.raceOption = self.findChild(QComboBox, "raceComboBox")
        self.genderOption = self.findChild(QComboBox, "genderComboBox")
        self.alignmentOption = self.findChild(QComboBox, "alignComboBox")
        self.ethicsOption = self.findChild(QComboBox, "ethicsComboBox")
        self.professionEntry = self.findChild(QLineEdit, "professionLineEdit")
        
        self.generateButton = self.findChild(QPushButton, 'generateButton')
        self.generateButton.clicked.connect(self.generate_npc)

        self.saveButton = self.findChild(QPushButton, 'saveButton')
        self.saveButton.clicked.connect(self.save_npc)

        # scroll area
        self.prevNPCScroll = self.findChild(QScrollArea, "scrollArea")
        self.prevNPCWidget = self.findChild(QWidget, "scrollAreaWidgetContents")
        self.prevNPCLayout = self.findChild(QVBoxLayout, "layoutArea")
        self.prevNPCScroll.setWidget(self.prevNPCWidget)

        # outputs
        self.nameOutput = self.findChild(QLineEdit, "nameOutput")
        self.raceOutput = self.findChild(QLineEdit, "raceOutput")
        self.genderOutput = self.findChild(QLineEdit, "genderOutput")
        self.alignmentOutput = self.findChild(QLineEdit, "alignmentOutput")
        self.appearanceOutput = self.findChild(QLineEdit, "appearanceOutput")
        self.professionOutput = self.findChild(QLineEdit, "professionOutput")

        self.talentOutput = self.findChild(QLineEdit, "talentOutput")
        self.mannerismOutput = self.findChild(QLineEdit, "mannerismOutput")
        self.interactionTraitOutput = self.findChild(QLineEdit, "interactionTraitOutput")
        self.idealOutput = self.findChild(QLineEdit, "idealOutput")
        self.bondOutput = self.findChild(QLineEdit, "bondOutput")
        self.flawOutput = self.findChild(QLineEdit, "flawOutput")

        self.notesOutput = self.findChild(QTextEdit, "notesTextEdit")

        for npc in self.npc_list:
            npc_widget = SavedNPCWidget(self, npc, self.prevNPCWidget)
            self.add_widget_to_scrollbox(npc_widget, self.prevNPCLayout, self.prevNPCScroll, addToTop=True)
        
    # --- Dungeon Gen Functions ---

    def remove_temp_dungeons(self):
        for temp in self.temp_buttons:
            temp.delete()
    

    def remove_encounters(self):
        self.encounterTextBox.clear()
    

    def print_encounters(self, encounters):
        try:
            for encounter in encounters:
                logging.info("Printing encounter: [{}, {}]".format(encounter[0], encounter[1]))
                self.encounterTextBox.append("Room "+str(encounter[0])+": "+encounter[1])
        except TypeError:
            print('No encounters')


    def open_dungeon(self):
        if 'name' in self.current_dungeon:
            try:
                image = Image.open("generated_dungeons\\"+self.current_dungeon['name']+".png")
                image.show()
            except:
                print("Cannot display image")
        else:
            try:
                image = Image.open("generated_dungeons\\"+'tempF1'+".png")
                image.show()
            except:
                print(self.current_dungeon)



    def generate_dungeon(self):
        self.generateButton.setEnabled(False)
        #remove temporary dungeon images
        self.remove_temp_dungeons()
        self.remove_encounters()
        #check this to see what is to much etc
        room_Density_dict = {"Sparse":100,"Moderate":1000,"Dense":5000}
        roomDensity = str(self.roomDensityOption.currentText())
        roomSize = str(self.roomSizeOption.currentText())
        floors = self.floorOption.value()
        dungeonSize = str(self.dungeonSizeOption.currentText())
        room_dens = room_Density_dict.get(roomDensity)
        if "Dangerous" in dungeonSize:
            dungeonSize = "Dangerous" 
        dungeonImages = makeDungeon(dungeonSize,roomSize,room_dens,floors)
        count = 1
        for dungeonImage in dungeonImages:
            to_image(dungeonImage)
            shutil.copy("dungeonmap.png","generated_dungeons/tempF"+str(count)+'.png')
            count+=1
        self.temp_dungeon = {}
        count = 1
        if self.encounterGenCheckBox.isChecked():
            partySize = self.partySizeOption.value()
            partyLevel = self.partyLevelOption.value()
            dungeonDifficulty = str(self.dungeonDifficultyOption.currentText())
            encounterString = makeEncounters(dungeonImages,partySize,partyLevel,dungeonDifficulty)
            for encounter in encounterString:
                imgName = "tempF"+str(count)
                self.temp_dungeon[imgName] = encounter
                count+=1
        #display first encounter ie temp_dungeons['temp1']
            self.print_encounters(self.temp_dungeon['tempF1'])
        else:
            for dungeon in dungeonImages:
                imgName = "tempF"+str(count)
                self.temp_dungeon[imgName] = None
                count+=1
        logging.info("Created the dungeon")        
        QPixmapCache.clear()
        pix= QPixmap('generated_dungeons/tempF1.png').scaled(400,400, Qt.KeepAspectRatio)
        self.dungeonImageLabel.setPixmap(pix)
        #need to display buttons to load the other images and ecnoutners
        self.current_dungeon = self.temp_dungeon 
        self.temp_buttons.clear()
        for dungeon in self.temp_dungeon:
            new_dungeon= {}
            new_dungeon['name']=dungeon
            new_dungeon['encounters']=self.temp_dungeon[dungeon]
            dungeon_widget = SavedDungeonWidget(self, new_dungeon, self.prevDungeonWidget)
            self.add_widget_to_scrollbox(dungeon_widget, self.prevDungeonLayout, self.prevDungeonScroll, addToTop=True)
            self.temp_buttons.append(dungeon_widget)
        self.generateButton.setEnabled(True)
      
    
    def save_dungeon(self):
        logging.info("Saving Dungeon")
        #for dungeon in dungeons
        floorNumber = 1
        dungeon_name =''.join(filter(str.isalnum,self.dungeonName.text()))
        if 'name' in self.current_dungeon:
            new_dungeon = {}
            name = dungeon_name+"F"+str(floorNumber)
            shutil.copy("generated_dungeons\\"+self.current_dungeon['name']+".png","generated_dungeons\\"+name+".png")
            new_dungeon['name']=name
            new_dungeon['encounters']=self.current_dungeon['encounters']
            dungeon_widget = SavedDungeonWidget(self, new_dungeon, self.prevDungeonWidget)
            self.add_widget_to_scrollbox(dungeon_widget, self.prevDungeonLayout, self.prevDungeonScroll, addToTop=True)
            self.dungeon_list.append(new_dungeon)
            floorNumber+=1

            logging.info("Saved Dungeon named {}".format(name))
        else:
            for dungeon in self.current_dungeon:
                new_dungeon = {}
                name = dungeon_name+"F"+str(floorNumber)
                shutil.copy("generated_dungeons\\"+dungeon+".png","generated_dungeons\\"+name+".png")
                new_dungeon['name']=name
                new_dungeon['encounters']=self.current_dungeon[dungeon]
                dungeon_widget = SavedDungeonWidget(self, new_dungeon, self.prevDungeonWidget)
                self.add_widget_to_scrollbox(dungeon_widget, self.prevDungeonLayout, self.prevDungeonScroll, addToTop=True)
                self.dungeon_list.append(new_dungeon)
                floorNumber+=1

                logging.info("Saved Dungeon named {}".format(name))
               
        
    def load_dungeon(self, dungeon, widget=None):
        logging.info("Loading Dungeon")
        self.remove_encounters()
        #load name as in the save field
        self.dungeonName.setText(dungeon['name'])
        self.current_dungeon = dungeon
        #load up the image
        QPixmapCache.clear()
        pix= QPixmap("generated_dungeons\\"+dungeon['name']+".png").scaled(400,400, Qt.KeepAspectRatio)
        self.dungeonImageLabel.setPixmap(pix)
        #load encounters if they exist      
        self.print_encounters(dungeon['encounters'])
        
    # --- NPC Gen Functions ---

    def generate_npc(self):
        race = str(self.raceOption.currentText())
        gender = str(self.genderOption.currentText())
        alignment = str(self.alignmentOption.currentText())
        ethics = str(self.ethicsOption.currentText())
        profession = self.professionEntry.text()

        npc = self.npcGen.generate(race, gender, alignment, ethics, profession)

        logging.info("Generated: {}\n".format(str(npc)))

        self.nameOutput.setText('{} {}'.format(npc.get('forename', 'error'), npc.get('othername', 'error'))) 
        self.raceOutput.setText(npc.get('race', 'error'))
        self.genderOutput.setText(npc.get('gender', 'error'))
        align, ethics = npc.get('alignment', ['error', 'error'])
        self.alignmentOutput.setText('{} {}'.format(align, ethics))
        self.appearanceOutput.setText(npc.get('appearance', 'error'))
        self.professionOutput.setText(npc.get('profession', 'error'))

        self.talentOutput.setText(npc.get('talent', 'error'))
        self.mannerismOutput.setText(npc.get('mannerism', 'error'))
        self.interactionTraitOutput.setText(npc.get('interaction_trait', 'error'))
        ideals = npc.get('ideal', ['error', 'error'])
        self.idealOutput.setText('{}, and {}'.format(ideals[0], ideals[1]))
        self.bondOutput.setText(npc.get('bond', 'error'))
        self.flawOutput.setText(npc.get('flaw', 'error'))

        self.notesOutput.setText('Write notes here.')

        self.saveButton.setEnabled(True)
        self.current_npc_widget = None


    def save_npc(self):
        logging.info("Saving NPC")
        current_npc = {}

        current_npc['name'] = self.nameOutput.text()
        current_npc['race'] = self.raceOutput.text()
        current_npc['gender'] = self.genderOutput.text()
        current_npc['alignment'] = self.alignmentOutput.text()
        current_npc['appearance'] = self.appearanceOutput.text()
        current_npc['profession'] = self.professionOutput.text()

        current_npc['talent'] = self.talentOutput.text()
        current_npc['mannerism'] = self.mannerismOutput.text()
        current_npc['interaction_trait'] = self.interactionTraitOutput.text()
        current_npc['ideals'] = self.idealOutput.text()
        current_npc['bond'] = self.bondOutput.text()
        current_npc['flaw'] = self.flawOutput.text()

        current_npc['notes'] = self.notesOutput.toPlainText()

        logging.info("Saving: {}\n".format(str(current_npc)))
        self.npc_list.append(current_npc)

        if self.current_npc_widget is None:
            npc_widget = SavedNPCWidget(self, current_npc, self.prevNPCWidget)
            self.add_widget_to_scrollbox(npc_widget, self.prevNPCLayout, self.prevNPCScroll, addToTop=True)
            self.current_npc_widget = npc_widget
        else:
            self.current_npc_widget.change_npc_data(current_npc)


    def load_npc(self, npc, widget=None):
        logging.info("Loading NPC")
        self.saveButton.setEnabled(True)
        self.current_npc_widget = widget
        
        self.nameOutput.setText(npc.get('name', 'error'))
        self.raceOutput.setText(npc.get('race', 'error'))
        self.genderOutput.setText(npc.get('gender', 'error'))
        self.alignmentOutput.setText(npc.get('alignment', 'error'))
        self.appearanceOutput.setText(npc.get('appearance', 'error'))
        self.professionOutput.setText(npc.get('profession', 'error'))

        self.talentOutput.setText(npc.get('talent', 'error'))
        self.mannerismOutput.setText(npc.get('mannerism', 'error'))
        self.interactionTraitOutput.setText(npc.get('interaction_trait', 'error'))
        self.idealOutput.setText(npc.get('ideals', 'error'))
        self.bondOutput.setText(npc.get('bond', 'error'))
        self.flawOutput.setText(npc.get('flaw', 'error'))

        self.notesOutput.setText(npc.get('notes', 'error'))

        logging.info("Loading: {}\n".format(str(npc)))   

    # --- Watson Dialog ---

    def send_message(self):
        self.enterButton.setEnabled(False)

        new_input = self.input.text()
        self.print_text(new_input, alignRight=True)
        self.input.clear()
        
        logging.info("Sent to Watson '{}'".format(new_input))

        try:
            response = self.assistant.getResponse(new_input)
        except (ConnectionError, ApiException):
            logging.info("Assistant Timeout. Creating new Session.")
            self.assistant.createNewSession()
            response = self.assistant.getResponse(new_input)
        
        logging.info("Recieved response '{}'".format(str(response)))        
        self.print_response(response)

        self.enterButton.setEnabled(True)
     

    def print_response(self,response):
        for label in response:
            # just print text
            if label['response_type']=='text':
                self.print_text(label['text'])
            # description -> source
            elif label['response_type']=='image':
                self.print_image(label['source'])
                self.print_text(label['description'])                         
            # title -> description -> buttons ie options
            elif label['response_type']=='option':
                if 'title' in label:
                    self.print_text(label['title'])
                if 'description' in label:
                    self.print_text(label['description'])
                self.print_option(label)

    # --- General Output ---

    def add_widget_to_scrollbox(self, widget, scrollBoxLayout, scrollBox, addToTop=False):
        if addToTop:
            scrollBoxLayout.insertWidget(0, widget)
        else:
            scrollBoxLayout.addWidget(widget)
        
        widget.show()

        self.mainApp.processEvents()
        scrollBox.ensureWidgetVisible(widget)


    def print_buttons(self, labels, values):
        buttonBar = ButtonBar(self, labels, values, self.outputWidget)
        
        self.add_widget_to_scrollbox(buttonBar.groupBox, self.outputLayout, self.outputScroll)
        
        # self.chatHistory.append(buttonBar.groupBox) 
        # just causes an empty box on subsequent loads? looks better to not try currently


    def print_text(self, message, alignRight=False):
        newLabel = QLabel(self.outputWidget)
        newLabel.setText(message)
        newLabel.setWordWrap(True)
        newLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        newLabel.setOpenExternalLinks(True)
        if(alignRight):
            newLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.add_widget_to_scrollbox(newLabel, self.outputLayout, self.outputScroll)
        self.chatHistory.append(newLabel)


    # QMovie is what will play gifs we will likely need a way to auto pause these as they will probably continue playing
    # Need to rescale 
    def print_image(self,source):
        # 0 is a nat 1 and anything else is a nat 20
        if source == '0':
            image_label = QLabel()
            # this is how to set a pixmap and scale the pixmap
            pix= QPixmap("img/ohno.png").scaled(350,200,Qt.KeepAspectRatio)
            image_label.setPixmap(pix)
            
            self.add_widget_to_scrollbox(image_label, self.outputLayout, self.outputScroll)
            self.chatHistory.append(image_label)
        else:
            gif = QMovie("img/nat20.gif")
            # gif.setScaledSize(200,200) still is not working not sure how to scale this still
            gif_label = QLabel()
            gif_label.setMovie(gif)
            gif.start()
            
            self.add_widget_to_scrollbox(gif_label, self.outputLayout, self.outputScroll)
            self.chatHistory.append(gif_label)
            
            
    def print_option(self,label):
        text=[]
        values=[]
        for option in label['options']:
            text.append(option['label'])
            values.append(option['value']['input']['text'])
        logging.info(text)
        logging.info(values)
        self.print_buttons(text,values)
        
# --- Main ---

def main():
    app = QApplication(sys.argv)
    main = MainWindow(app)
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    logging.root.handlers = []

    now = datetime.now()
    filename = now.strftime('%y-%m-%d-%H-%M-%S')

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/{}.log".format(filename)),
            logging.StreamHandler()
        ]
    )

    try:
        main()
    except Exception as e:
        logging.exception(e)