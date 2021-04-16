
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.

import sys, logging

import random, requests, json

difficulty_strings = ['Easy','Medium','Hard', 'TPK']

#list copied from DMG pg 82 for xp thresholds by char level
#This is a D&D 5e psuedo-random combat encounter generator.
thresholds = [
	[25, 50, 75, 100, 500],
	[50, 100, 150, 200, 1100],
	[75, 150, 225, 400, 1700],
	[125, 250, 375, 500, 2100],
	[250, 500, 750, 1100, 2400],
	[300, 600, 900, 1400, 2800],
	[350, 750, 1100, 1700, 3600],
	[450, 900, 1400, 2100, 4500],
	[550, 1100, 1600, 2400, 5100],
	[600, 1200, 1900, 2800, 10000],
	[800, 1600, 2400, 3600, 25000],
	[1000, 2000, 3000, 4500, 35000],
	[1100, 2200, 3400, 5100, 70000],
	[1250, 2500, 3800, 5700, 82000],
	[1400, 2800, 4300, 6400, 92000],
	[1600, 3200, 4800, 7200, 100000],
	[2000, 3900, 5900, 8800, 120000],
	[2100, 4200, 6300, 9500, 150000],
	[2400, 4900, 7300, 10900, 175000],
	[2800, 5700, 8500, 12700, 320000]
]
crToExp = { '0' : 10,
            '1/8' : 25,
            '1/4' : 50,
            '1/2' : 100,
            '1' : 200,
            '2' : 450,
            '3' : 700,
            '4' : 1100,
            '5' : 1800,
            '6' : 2300,
            '7' : 2900,
            '8' : 3900,
            '9' : 5000,
            '10' : 5900,
            '11' : 7200,
            '12' : 8400,
            '13' : 10000,
            '14' : 11500,
            '15' : 13000,
            '16' : 15000,
            '17' : 18000,
            '18' : 20000,
            '19' : 22000,
            '20' : 25000,
            '21' : 33000,
            '22' : 41000,
            '23' : 50000,
            '24' : 62000,
            '25' : 75000,
            '26' : 90000,
            '27' : 105000,
            '28' : 120000,
            '29' : 135000,
            '30' : 155000
}
diffToMult = { 'Easy' : 1,
                'Medium' : 2,
                'Hard' : 3,
                'Deadly' : 4,
                'TPK' : 5 }

ranOut = False
#our function with three inputs - number of PCs, their average level, and difficulty

def party_threshold(numPcs, avgLev, difficulty):
    xp = thresholds[(avgLev - 1)][(difficulty - 1)]
    xp = (xp * numPcs)
    logging.info('Our combined party XP threshold is: ' + str(xp))
    return xp

def load_monsters(type):
    #Load a list of monsters that contains Tuples of: Name, Type, exp
    monsterData = []
    dataurl = ''
    
    if(type == ""):
        dataurl = 'https://api.open5e.com/monsters/?limit=500'
    else:
        dataurl = 'https://api.open5e.com/monsters/?type=' + type
    while dataurl != None:
        response = requests.get(dataurl)
        responseJson = response.json()
        dataurl = responseJson['next']
        for mon in responseJson['results']:
            exp = crToExp.get(mon['challenge_rating'])
            monster = tuple((mon['name'], mon['type'], exp, mon['slug']))
            monsterData.append(monster)

    random.shuffle(monsterData)
    return(monsterData)

# generate our combat encounter

def encounter_gen(monsterList, xpThreshold):
    encounteredMonsters = []		# list for the encountered monsters
    monsterCounter = 0
    xpMonsters = 0
    xpLowerLimit = int(xpThreshold / 25)
    while xpMonsters < (xpThreshold - (3 * xpLowerLimit)):		# keep adding monsters until we get close enought to xpThreshold
        possibleMonsters = []
        for m in monsterList:		# remove monsters with too high or too low xp values
            if xpLowerLimit < int(m[2]) < (xpThreshold - xpMonsters):
                possibleMonsters.append(m)
        if not possibleMonsters:
            global ranOut
            ranOut = True# this is just a warning that there might have been xp left over
            return encounteredMonsters
        r = random.randint(0, (len(possibleMonsters) - 1))
        encounteredMonsters.append(possibleMonsters[r])
        monsterCounter = len(encounteredMonsters)
        xpMonsters = 0
        for xp in encounteredMonsters:
            xpMonsters += int(xp[2])
        if monsterCounter == 2:			# these if statements take into account difficulty scaling with # of monsters
            xpMonsters = int(xpMonsters * 1.5)
        if 3 <= monsterCounter <= 6:
            xpMonsters = xpMonsters * 2
        if 7 <= monsterCounter <= 10:
            xpMonsters = int(xpMonsters * 2.5)
    return encounteredMonsters

#print out the monsters in a nicely formated way
def print_encounter(encounteredMonsters):
    returnString = 'Our encounter consists of: <br/><br/>'
    
    if ranOut:
        returnString = 'The generator ran out of monster\'s while building the encounter. Try changing your search. ' + returnString

    count = {}
    for m in encounteredMonsters:
        if(m[3] in count.keys()):
            count[m[3]][1] += 1
        else:
            count[m[3]] = (m[0],1)

    for m in count:
        url = 'https://open5e.com/monsters/'
        url = str(count[m][1]) + " - " + "<a  target=\"_blank\" href=\"" + url + str(m) + "\">" + str(count[m][0]) + "</a>.<br/><br/>"
        returnString +=  url
    return returnString

def call_encounter(difficulty, num_encounters, numPcs, avgLev):
    logging.info("Generating encounter [difficulty={}, num_encounters={}, numPcs={}, avgLev={}]".format(difficulty, num_encounters, numPcs, avgLev))
    difficulty = diffToMult.get(difficulty)
    
    xp = party_threshold(numPcs,avgLev,difficulty)
    monster_data = load_monsters("") #select all monster types
    
    encounters = []
    for i in range(num_encounters):
        encounteredMonsters = encounter_gen(monster_data, xp)
        encounters.append(print_encounter(encounteredMonsters))
    
    return encounters

if __name__ == '__main__':
    params = {"size" : 4,"level" : 10}
    call_encounter(params)