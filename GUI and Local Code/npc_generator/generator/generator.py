import json, logging
from random import choice

DATA_FILE_PATH = 'npc_generator/generator/data/data.json'

class Generator(object):
    def __init__(self):
        with open(DATA_FILE_PATH, 'r') as raw:
            self.data = json.load(raw)

    def generate(self, race=None, gender=None, moral=None, ethic=None, profession=None):
        logging.info("Generating NPC [race={}, gender={}, moral={}, ethic={}, profession={}]".format(race, gender, moral, ethic, profession))
        if race == "":
            race = None
        if gender == "":
            gender = None
        if moral == "":
            moral = None
        if ethic == "":
            ethic = None
        if profession == "":
            profession = None


        if race is None:
            race = choice(self.data['races'])
        else:
            race = race.lower()

        if gender is None:
            gender = choice(self.data['genders'])
        else:
            gender = gender.lower()

        if moral is None:
            moral = choice(self.data['morals'])
        else:
            moral = moral.lower()

        if ethic is None:
            ethic = choice(self.data['ethics'])
        else:
            ethic = ethic.lower()

        if profession is None:
            profession = choice(self.data['professions'])
        else:
            profession = profession.lower()


        namegender = gender
        if gender == "other":
            namegender = choice(['male', 'female'])
        '''
        forename and other name will need option for other gender added
        race - dropdown: all races within the data.json
        gender - dropdown: male female and then other
        alignment - dropdown: good,evil, neutral
        ethics - dropdown: chaotic, neutral, lawful
        profession - textbox
        '''
        return {
            'race': race,
            'gender': gender,
            'alignment': [moral, ethic],
            'forename': choice(self.data['names'][race][namegender]),
            'othername': choice(self.data['names'][race]['othername']),
            'appearance': choice(self.data['apperances']),
            'profession': profession,
            'abilities': None,
            'talent': choice(self.data['talents']),
            'mannerism': choice(self.data['mannerisms']),
            'interaction_trait': choice(self.data['interactionTraits']),
            'ideal': [
                choice(self.data['ideals'][moral]),
                choice(self.data['ideals'][ethic])
            ],
            'bond': choice(self.data['bonds']),
            'flaw': choice(self.data['flaws']),
        }