import json as JSON
import logging
from cs50 import SQL
import datetime

# Function to take a json file and INSERT any spells in it into spells db
def spells_import(file, user, db):
    # Open the file provided and convert the JSON to python object, in this case a list of dicts
    # TODO: This is a file, when implementing importing function may need to consider are they uploading a file, copying and pasting the contents of a json, or editing an HTML form
    #       and need to commit to whichever design decision is made and adjust this function appropriately.
    with open(file) as file:
        data = JSON.load(file)


    # Create a dict to store spells with the format intended for feeding to the jinja templates
    spells = {}
    janky = []
    # Iterate through data and build a new dict with just the info needed for our db
    for spell in data:
        if spell["type"] == "spell":
            print(spell["data"]["source"])
            if spell["data"]["source"] == "":
                janky.append(spell["name"])
            if spell["data"]["source"] in spells:
                spells[spell["data"]["source"]] +=1
            else:
                spells[spell["data"]["source"]] = 1

    print(janky)


    # return(spells)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///npc.db")

# Caller should provide the file name, from a HTML input form on spells.html
data = 'item-1-global-spells.db'

print(spells_import(data, 1, db))


