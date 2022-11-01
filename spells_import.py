import json as JSON

from cs50 import SQL
 # If use logging

# Function to take a json file and INSERT any spells in it into spells db
def spells_import(file, user, db):
    # Open the file provided and convert the JSON to python object, in this case a list of dicts
    # TODO: This is a file, when implementing importing function may need to consider are they uploading a file, copying and pasting the contents of a json, or editing an HTML form
    #       and need to commit to whichever design decision is made and adjust this function appropriately.
    with open(file) as file:
        data = JSON.load(file)

    '''
    TODO: Implment logging? Is logging really needed?
    # If decide to use logging Add these two to imports
    import datetime
    import logging

    # Configure some logging
    date = datetime.datetime.now()
    date = date.strftime("%d-%m-%Y %H:%M:%S")
    Dynamically create log name with user and date timestamp

    # Create a list for errors, each error will be a list with the name of the spell and which part of the import process didn't work I.E. ['magic missile', description]
    errors = []

    log_name =
    logging.basicConfig(filename='example.log', encoding='utf-8')

    # Try / except where if it doesn't work add name and type to a list to print out at end?
    '''

    # Create a list to store spells with the format intended for feeding to the jinja templates
    spells = []

    # Iterate through data and build a new dict with just the info needed for our db
    for spell in data:
        if spell["type"] == "spell":
            # Empty dict to populate for each iteration
            this_spell = {}

            # Some keys/values will be straight adds
            this_spell["name"] = spell["name"]
            this_spell["lvl"] = spell["data"]["level"]
            this_spell["img"] = spell["img"]
            this_spell["description"] = spell["data"]["description"]["value"]
            this_spell["school"] = spell["data"]["school"]
            this_spell["verbal"] = spell["data"]["components"]["vocal"]
            this_spell["somatic"] = spell["data"]["components"]["somatic"]
            this_spell["material"] = spell["data"]["components"]["material"]
            this_spell["ritual"] = spell["data"]["components"]["ritual"]
            this_spell["concentration"] = spell["data"]["components"]["concentration"]

            # Check sources table, add if needed, get id for the source, add that as value
            print(spell["data"]["source"])

            # These keys were split into multiple values so have to be combined into format we want to use
            '''
            classes
            print(spell["data"]["materials"]["value"]) # value is text of what material component is?
            print(spell["data"]["activation"]["type"]) # casting time?
            print(spell["data"]["duration"]["value"])
            print(spell["data"]["target"]["value"])
            save
            dmg
            
            '''

    #return(spells)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///npc.db")

# Caller should provide the file name, from a HTML input form on spells.html
data = 'item-1-global-spells.db'

print(spells_import(data, 1, db))

'''
    TODO: FoundryVTT's .db files from pack folder, based on my research while trying to implement this function, are a "newline separated"
        file of jsons. So to get it to work I had to manually edit the file to wrap the existing lines into a json
        wrapped existing lines inside of [] and added a comma at the end of each line.  At this moment I just want to get some spells imported
        so i can work on the spells.html and spells route in app.py.  Need to find a way to either iterate through the file as is, or programmatically
        modify the files. Or as a less desirable solution force the users to edit them, provide a sample file for importing and put the work of getting
        their data into that format on them rather than a function to do it automatically.
'''

