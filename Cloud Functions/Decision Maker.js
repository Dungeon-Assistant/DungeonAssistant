/**
  *
  * main() will be run when you invoke this action
  *
  * @param Cloud Functions actions accept a single parameter, which must be a JSON object.
  *
  * @return The output of this action, which must be a JSON object.
  *
  */
  //Code based on IBM function calls from cloud functions guide. The goal of this function is to split Watson Assistant's one webhook call capability into many, by creating a switcher for the calls.
const openwhisk = require('openwhisk');
const ow = openwhisk();
  
function main(params) {
    
    //Return values are all dictionaries
    var result;
    
    //Calls to Dungeon Assistant Action Dice Roll.
    if(params.call == "Dice-Roll")
    {
        result = ow.actions.invoke({ 
            name: 'Dungeon-Assistant-Actions/Dice-Roll',
            blocking: true,
            result: true,
            params: params
        });
    }
    
    //Calls to Dungeon Assistant Action Monster Search
    else if(params.call == "Monster-Search")
    {
        result = ow.actions.invoke({ 
            name: 'Dungeon-Assistant-Actions/Monster-Search',
            blocking: true,
            result: true,
            params: params
            });
    }    
    
    //Calls to Dungeon Assistant Action Spell Search
    else if(params.call == "Spell-Search")
    {
        result = ow.actions.invoke({ 
            name: 'Dungeon-Assistant-Actions/Spell Search',
            blocking: true,
            result: true,
            params: params
            });
    }
    
    //Calls to Dungeon Assistant Item Search
    else if(params.call == "Item-Search")
    {
        result = ow.actions.invoke({ 
            name: 'Dungeon-Assistant-Actions/Magic-Item-Search',
            blocking: true,
            result: true,
            params: params
            });
    }
    
    //Calls to Dungeon Assistant Weapon Search
    else if(params.call == "Weapon-Search")
    {
        result = ow.actions.invoke({ 
            name: 'Dungeon-Assistant-Actions/Weapon-Search',
            blocking: true,
            result: true,
            params: params
            });
    }
    
    //Calls to Dungeon Assistant Encounter Generation
    else if(params.call == "Encounter-Generation")
    {
        result = ow.actions.invoke({ 
            name: 'Dungeon-Assistant-Actions/Encounter Generation',
            blocking: true,
            result: true,
            params: params
            });
    }
    
    //Calls to Dungeon Assistant Exp Calculator
    else if(params.call == "calculator")
    {
        result = ow.actions.invoke({ 
            name: 'Dungeon-Assistant-Actions/exp-Calculator',
            blocking: true,
            result: true,
            params: params
            });    
    }
    
    //Return the result obtained from the call above.
	return result;
}
