from cs50 import SQL

# Function to get the column names of a SQL table
def columns(table):
    # Set CS50 to use npc.db
    db = SQL("sqlite:///npc.db")
    col = db.execute("SELECT * FROM ? LIMIT 1", table)
    col = col[0].keys()
    names = []
    for i in col:
        names.append(i)
    return(names)

table = columns('spells')
print(table)