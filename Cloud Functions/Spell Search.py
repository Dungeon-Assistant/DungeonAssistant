#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#
import sys
import requests

def main(dict):
    parseStmt=""
    url = 'https://open5e.com/spells/'
    testurl = 'https://api.open5e.com/spells/?'
    
    # SPELL SEARCH OPTIONS
    # name
    # range (touch, self, 30 feet, 60 feet, 90 feet, 120 feet) 
    # components (V,S,M) 
    # ritual (yes,no) : concentration (yes,no)
    # casting_time (1 action, 1 bonus action, 1 minute, 1 hour, 8 hours, 24 hours)
    # level_int (0-9) : class (Cleric, Wizard, Druid, Sorcerer, Warlock): 
    
    multi_filter_flag = False
    spellSpaced = ""
    spellDashed = ""
    #API searches are spaced, URLs are dashed
    if(dict.get("name") is not None):
        spellSpaced = dict.get("name").replace("\"", "").lower()
        spellDashed = spellSpaced.replace(" ", "-")
        
        testurl = testurl + 'search=' + spellSpaced
        multi_filter_flag = True

    
    if(dict.get("level") is not None):
        level = dict.get("level")
        if(multi_filter_flag):
            testurl = testurl + "&"
        
        testurl = testurl + "level_int=" + str(level)
        multi_filter_flag = True

    if(dict.get("school") is not None):
        spellSchool = dict.get("school").replace("\"", "").lower()
        if(multi_filter_flag):
            testurl = testurl + "&"
        
        testurl = testurl + "school=" + spellSchool
        multi_filter_flag = True
    
    if(dict.get("class") is not None):
        spellClass = dict.get("class").replace("\"", "").lower()
        if(multi_filter_flag):
            testurl = testurl + "&"
        
        testurl = testurl + "class=" + spellClass
        multi_filter_flag = True
    

    
    #if filters return only one result, set match flag and create a node response for 1 returned
    matchFlag = False
    
    print(url)
    response = requests.get(testurl)
    responseJson = response.json()
    
    #Add search functionality when count returned from testurl != 1
    numOfResults = responseJson['count']
    if numOfResults==1:
        num=1
        for x in responseJson['results']:
            print(x['name'])
            matchFlag = True
            parseStmt+=str(num)+". "+x['name']+"\n"
            spellSpaced = x['name']
            url = url + x['slug']
    if numOfResults>1:
        print(numOfResults)
        num=1
        for x in responseJson['results']:
            print(x['name'])
            if(x['name'].lower() == spellSpaced):
                matchFlag = True
                spellSpaced=x['name']
                url = url + x['slug']
            parseStmt+=str(num)+". "+x['name']+"\n"
            num+=1
    if(spellSpaced != ""):
        url = "<a  target=\"_blank\" href=\"" + url + "\">" + spellSpaced + "</a>.<br/><br/>"

    return {
            'url' : url,
            'count':numOfResults,
            'pre' : parseStmt,
            'match' : matchFlag
    }
