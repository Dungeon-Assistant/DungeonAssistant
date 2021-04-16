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
    url = 'https://open5e.com/magicitems/'
    testurl = 'https://api.open5e.com/magicitems/?'
    
    #API searches are spaced, URLs are dashed
    itemSpaced = dict.get("name").replace("\"", "").lower()
    itemDashed = itemSpaced.replace(" ", "-")
    
    url = url + itemDashed
    testurl = testurl + 'search=' + itemSpaced

    #if filters return only one result, set match flag and create a node response for 1 returned
    matchFlag = False
    
    print(url)
    print(testurl)
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
            itemSpaced = x['name']
    if numOfResults>1:
        print(numOfResults)
        num=1
        for x in responseJson['results']:
            print(x['name'])
            if(x['name'].lower() == itemSpaced):
                matchFlag = True
                itemSpaced=x['name']
            parseStmt+=str(num)+". "+x['name']+"\n"
            num+=1
    
    url = "<a  target=\"_blank\" href=\" " + url + "\">" + itemSpaced + "</a>.<br/><br/>"

    return {
            'url' : url,
            'count':numOfResults,
            'pre' : parseStmt,
            'match' : matchFlag
    }
