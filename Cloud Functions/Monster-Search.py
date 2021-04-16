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
    url = 'https://open5e.com/monsters/'
    testurl = 'https://api.open5e.com/monsters/?'
    
    # name, level_int, dnd_class (caps), school (also caps), range (also caps)
    #API searches are spaced, URLs are dashed
    monsterSpaced = ""
    monsterDashed = ""
    if(dict.get("monster") is not None):
        monsterSpaced = dict.get("monster").replace("\"", "").lower()
        monsterDashed = monsterSpaced.replace(" ", "-")
        
        url = url + monsterDashed
        testurl = testurl + 'search=' + monsterSpaced
    
    if(dict.get("cr") is not None):
        challenge = dict.get("cr")
        if(dict.get("monster") is not None):
            testurl = testurl + "&"
        
        testurl = testurl + "challenge_rating=" + str(challenge)

    
    if(dict.get("type") is not None):
        monsterType = dict.get("type").replace("\"", "").lower()
        if(dict.get("monster") is not None or dict.get("cr") is not None):
            testurl = testurl + "&"
        
        testurl = testurl + "type=" + monsterType
    
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
            monsterSpaced = x['name']
    if numOfResults>1:
        print(numOfResults)
        num=1
        for x in responseJson['results']:
            print(x['name'])
            if(x['name'].lower() == monsterSpaced):
                matchFlag = True
                monsterSpaced=x['name']
            parseStmt+=str(num)+". "+x['name']+"\n"
            num+=1
    
    url = "<a  target=\"_blank\" href=\" " + url + "\">" + monsterSpaced + "</a>.<br/><br/>"

    return {
            'url' : url,
            'count':numOfResults,
            'pre' : parseStmt,
            'match' : matchFlag
    }
