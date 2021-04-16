#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#

#An exp calculator based on the rules stated on https://www.dndbeyond.com/sources/basic-rules/building-combat-encounters

import sys

#Difficulty thresholds for encounters
thresholds = [
	[25, 50, 75, 100],
	[50, 100, 150, 200],
	[75, 150, 225, 400],
	[125, 250, 375, 500],
	[250, 500, 750, 1100],
	[300, 600, 900, 1400],
	[350, 750, 1100, 1700],
	[450, 900, 1400, 2100],
	[550, 1100, 1600, 2400],
	[600, 1200, 1900, 2800],
	[800, 1600, 2400, 3600],
	[1000, 2000, 3000, 4500],
	[1100, 2200, 3400, 5100],
	[1250, 2500, 3800, 5700],
	[1400, 2800, 4300, 6400],
	[1600, 3200, 4800, 7200],
	[2000, 3900, 5900, 8800],
	[2100, 4200, 6300, 9500],
	[2400, 4900, 7300, 10900],
	[2800, 5700, 8500, 12700]]
	
#CR to EXP table
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

#Size adjustment table, feeds into second table
adjustments = { 1 : 1,
                2 : 2,
                3 : 3,
                4 : 3,
                5 : 3,
                6 : 3,
                7 : 4,
                8 : 4,
                9 : 4,
                10 : 4,
                11 : 5,
                12 : 5,
                13 : 5,
                14 : 5
    
}

#Second size adjustment table
adjustTable = [.5, 1, 1.5, 2, 2.5, 3, 4, 5]
def main(dict):
    
    #Get all data we need, and set variables.
    PList = dict.get('party_list',-1)
    CRList = dict.get('CR_list',-1)
    totalEXP = 0
    totalAdjustedEXP = 0
    avgLvl = 0
    rating = ""
    adjustment = 1
    returnDict = {}
    
    #Make sure our lists aren't empty.
    if not (PList == -1 or CRList == -1):
        CRList = CRList.strip()
        CRList = CRList.split(',')
        PList = PList.strip()
        PList = PList.split(',')
        
        #get total EXP, check to make sure the list was formatted properly.
        for CR in CRList:
            try:
                totalEXP += crToExp.get(CR)
            except:
                return {
                    'fail' : True,
                    'errormessage' : 'CR List formatted improperly.'
                }
        #get average level of party, check to make sure the list was formatted properly.
        for P in PList:
            try:
                level = int(P)
                avgLvl += level
            except:
                return {
                    'fail' : True,
                    'errormessage' : 'Player Level list formatted improperly.'
                }
        #Make sure the CRlist wasn't empty again.       
        if len(CRList) > 0:
            #Get the adjustment index from the first adjustment table
            adjustment = adjustments.get(len(CRList), 6)

            #adjust the index based on the rules stated in the link at the top of the file
            if(len(PList) < 3):
                adjustment = adjustTable[adjustment + 1]
                
            elif(len(PList) >= 6):
                adjustment = adjustTable[adjustment - 1]
                
            else:
                adjustment = adjustTable[adjustment]
            #Adjust exp
            totalAdjustedEXP = totalEXP * adjustment
        else:
            totalAdjustedEXP = totalEXP
        
        #calculate average level    
        avgLvl = int(avgLvl/len(PList))
        
        difficultyList = thresholds[avgLvl - 1]
        
        #Calculate the difficulty based off of the difficulty list from the thresholds matrix.
        if totalAdjustedEXP < difficultyList[0]*len(PList):
            rating = "Trivial"
        elif totalAdjustedEXP >= difficultyList[0]*len(PList) and totalAdjustedEXP < difficultyList[1]*len(PList):
            rating = "Easy"
        elif totalAdjustedEXP >= difficultyList[1]*len(PList) and totalAdjustedEXP < difficultyList[2]*len(PList):
            rating = "Medium"
        elif totalAdjustedEXP >= difficultyList[2]*len(PList) and totalAdjustedEXP < difficultyList[3]*len(PList):
            rating = "Hard"
        elif totalAdjustedEXP >= difficultyList[3]*len(PList):
            rating = "Deadly"
          
        #Set up the return dictionary. 
        returnDict = {
            'chars' : len(PList),
            'mons' : len(CRList),
            'awardGroup' : totalEXP,
            'awardEach' : totalEXP/len(PList),
            'adjustment' : adjustment,
            'ADR' : totalAdjustedEXP,
            'rating' : rating,
            'fail' : False
        }
        
    else:
        returnDict = {        
        'fail' : True,
        'errormessage' : 'Required inputs are missing from the call.'
        }
    return returnDict
