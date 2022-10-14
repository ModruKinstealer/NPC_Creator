import json as JSON

from cs50 import SQL


# Function to take a json file and INSERT any spells in it into spells db
def spells_import(file, user, db):
    # Open the file provided and convert the JSON to python object, in this case a list of dicts
    # TODO: This is a file, when implementing importing function may need to consider are they uploading a file, copying and pasting the contents of a json, or editing an HTML form
    #       and need to commit to whichever design decision is made and adjust this function appropriately.
    with open(file) as file:
        data = JSON.load(file)
    spells = []
    # Iterate through data and build a new dict with just the info needed for our db
    for spell in data:
        if spell["type"] == "spell":
            # Empty dict to populate for each iteration
            print(spell["name"])
            print(spell["img"])
            print(spell["data"]["description"]["value"])
            print(spell["data"]["source"])
            print(spell["data"]["level"])
            print(spell["data"]["school"])
            print(spell["data"]["components"]["vocal"])
            print(spell["data"]["components"]["somatic"])
            print(spell["data"]["components"]["material"])
            print(spell["data"]["components"]["ritual"])
            print(spell["data"]["components"]["concentration"])

            # TODO: logging? try except where if it doesn't work add name and type to a list to print out at end.
            # TODO: if spell["type"] == feat, don't process, or probably better only process if type is spell
            # TODO: Field split into dict with multiple keys, verify from Export of individual item before finalizing
            '''
            print(spell["data"]["materials"]["value"])
            print(spell["data"]["activation"]["type"])
            print(spell["data"]["duration"]["value"])
            print(spell["data"]["target"]["value"])
            '''


    # return(spells)

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

