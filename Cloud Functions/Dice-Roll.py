# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#

import sys
import random

def main(dict):
    #find index of d and dice value
    type_str = dict.get("type","d6")
    d_dex = type_str.index("d")
    type = int(type_str[d_dex+1:])
    total = 0
    
    #find number of dice, 2d20 vs 2 d20
    if(d_dex):
        num_dice = int(type_str[:d_dex])
        if(dict.get("operation") is not None):
            total = abs(int(dict.get("number",0)))
    else:
        if(dict.get("number") is not None):
            if(dict.get("operation") is not None and dict.get("bonus") is None):
                total = abs(int(dict.get("number",0)))
                if(op != "+"):
                    total *= -1
                num_dice = 1
            else:
                num_dice = int(dict.get("number",1))
        else:
            num_dice = 1   
    
    #find bonus
    if(dict.get("operation") is not None and dict.get("bonus") is not None):
        op = str(dict.get("operation","+"))
        
        #number is the first recognized number
        #if formatted as d20 + 15 / 15d20, 1 is the first number but is actually the bonus 
        total = abs(int(dict.get("bonus",0)))
        
        if(op != "+"):
            total *= -1
    
    #Parse Dice Rolls
    i = 0
    temp_bonus = total
    print(num_dice) #Print for Debug
    while(i < num_dice):
        total += random.randint(1,type)
        i += 1
    
    crit = False
    fail = False
    #Parse for crit or fail, return a random number for image choosing.
    if(num_dice == 1 and type == 20):
        if(total - temp_bonus == 20):
            crit = True
        elif(total - temp_bonus == 1):
            fail = True
    rand = random.randint(1,5)
    return { 'total': total,
             'crit': crit,
             'fail': fail,
             'rand': rand
    }
