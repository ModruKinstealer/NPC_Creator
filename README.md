# NPC_Creator
#### Video Demo:  <URL HERE>
#### Description:
A utility to create and modify NPCs for D&amp;D 5e games. Created for submission as the Final Project for [CS50](https://cs50.harvard.edu/x/2022/ "CS50 2022 welcome page")
  
# Purpose
As a new DM I found that often pre-made monsters or NPCs in my D&amp;D 5e game were not quite what I wanted and so I would modify stats or add abilities to them. This was in part because all of the players in my game have been playing since 1st edition and so they basically know everything about pretty much every significant monster and I wanted to surprise them a bit. It sounds easy, just give them a new spell like ability and it'll be fun, however it's not very intuitive as to how much of a difference say adding +1 to an Orc's attack will effect a combat. The Challenge Rating system in D&D is more or less a rough guideline rather than a set rule. If you have 4 players and a balance set of classes, chances are X CR will be an "easy" fight. However experienced players often hit above their weight class because they know the tricks, or sometimes an encounter will be won easily because the wizard happened to know the perfect spell to counter your bad guy. The Dungeon Master's Guide has information on modifying monsters to change their CR but they can be pretty confusing.  As a result to this I found myself looking online for a utility that helped figure out the CR of a creature based on changes I wanted to make. Well I was able to find a couple, Kobold Fightclub has one and D&DBeyond.com has another, however there are in my opinion some fundamental issues with both. With Kobold Fightclub for instance you have to enter in the stats of a creature and then manually figure out how much damage they do, what their defensive CR is, and select special abilities. Unfortunately they don't have all of the special abilities listed in the DMG, much less an ability to create custom ones. And then getting the site to update the CR is a click. So I decided I wanted to create a mod for Foundry VTT, my prefered VTT at the moment, then while considering initial design ideas I realized that some of my friends still run on Roll20 because that's what they're used to and would rather put up with that pain than take the time to learn something new so I thought I'd make both a web app and a mod for Foundry VTT. 

# Must haves
- A page with all of the stats that you would find on a character sheet. It should have both NPC related stats, like legendary actions, as well as more PC related stats, like inventory and long/short rests. 
- Updating stats should dynamically update the CR of the creature upon entry.
- Calculation of both offensive and defensive CRs should happen automatically whenever any stat effecting them is changed.
- Ability to save the creature into an easily used file format like json.
- At the minimum, each of the CR effecting abilities listed within the DMG.

# The Dream
- All features implemented in an web app as well as a FoundryVTT module. 
- CR should be calculated dynamically based on changes. 
- User login so that the user can save the work they've done and come back to it later.
- Ability to export into an easily manipulated file like json, if possible have the ability to export in file formats specific to various VTTs. For instance .rptok for Maptools.
- Each user would be able to decide if the creature they create is available for other users to access. Foundry would control through whatever they have in their compendium. 
- The ability to create custom abilities, including what the creator believes the effect on CR should be. This would allow them not only to create completely new abilities but modify existing creatures and save them as "home brew" for instance if a DM thinks flying should be +2 CR instead of +1 or whatever, they can create a version of an ability that does that. 
- If possible, the ability to drag and drop a token file to directly input creature stats.  For Foundry this will be possibly to drag from compendiums. Importing from json files is also available, converting from files exported from other VTTs therefor should just be reliant upon being able to get them into a json format. 
- The ability for each user to set what they want for default stats, or stat generation, for new creatures. 
- The ability for a DM to determine which abilities the creature uses for calculation of CR, for those instances when they know that they want to use a different set of abilities than what is defaulted to for an encounter so they can tailor the CR more effectively to a particular encounter should they choose. 

# Files and their purposes
-app.py, requirements.txt, helpers.py
    - The site I want to create has some similarities to pset9: Finance so I'm going to use that as a kind of template for the final project as such I'm going to use app.py for the main program and put all my helper functions in helpers.py. Ideally things should be setup as modular as possible.
-npc.db
    - Main database for the site. Will have tables for users, spells, features, monsters, races, equipment, backgrounds, skills, and languages at a minimum.
    - I may create additional tables that are for home brewed content for each of those as well, it'll depend on what I think would be easier to maintain and use going forward
    - I considered using Json files rather than a DB but I'd guess there's at least a thousand spells, and a couple thousand monsters, plus everything else I thought that a SQL db would be the better long term choice since there's no telling how many users will use it and therefor how many thousands of new entries will get created going forward





