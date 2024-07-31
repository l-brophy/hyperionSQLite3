import os
import sqlite3
from tabulate import tabulate


def call_database():
    """only called upon first run, checks for the onset book log file and
    creates and populates table, then deletes the file we write the database
    from so that upon every subsequent run the program knows not to do this 
    again
    """
    SQL.execute('''CREATE TABLE Books(ID INTEGER PRIMARY KEY,
                TITLE VARCHAR(255), Author VARCHAR(255), QTY INTEGER)''')
    db.commit()
    
    with open("onset_book_log.txt", "r") as initial_stock:
        for book in initial_stock:
            book = book.strip("\n").split("__")
            SQL.execute('''INSERT INTO Books(ROWID, Title, Author, QTY)
                        VALUES(?, ?, ?, ?)''', (int(book[0]), book[1],
                                                book[2], int(book[3])))
            db.commit()


def print_table(table):
    """uses the tabulate module to print a table of a given list of lists/
    tuples

    Args:
        table (li): given list of lists/tuples
    """    
    print(f"""
{tabulate(table, headers=["ID", "Title", "Author", "QTY"],
tablefmt="rounded_grid")}""")


def lookup(field, query):
    """uses the cursor to search the applicable field for the user's query and
    returns the result of the selection

    Args:
        field (str): the field that the user wants to search
        query (str): the specific search the user wants to make

    Returns:
        li: list of tuples returned by fetchall
    """
    match field:
        case "ID":
            SQL.execute('''SELECT * FROM Books WHERE ID = ?''',
                        (query,))
        case "Author":
            SQL.execute('''SELECT * FROM Books WHERE Author = ?''',
                        (query,))
        case "Title":
            SQL.execute('''SELECT * FROM Books WHERE Title = ?''',
                        (query,))
        case "QTY":
            SQL.execute('''SELECT * FROM Books WHERE QTY = ?''',
                        (query,))
        case "Title, Author":
            SQL.execute('''SELECT * FROM Books WHERE Title = ? AND Author = ?''',
                        (query))
    records = SQL.fetchall()
    return records


def query_field():
    """prompts the user for the field of a record/multiple records they'd like
    to interact with and returns the field name as written in the database, or
    calls itself recursively until it has a proper field value to check
    
    Returns:
        field (str): the case-sensitive heading that applies to the chosen 
    field
    """    
    search_field = input("""
    a - author
    t - title
    u - unique ID
    q - quantity
    
        : """).strip().lower()
    
    match search_field:
        case "a": 
            field = "Author"
        case "t": 
            field = "Title"
        case "u": 
            field = "ID"
        case "q":
            field = "QTY"
        case _:
            print("""\nInvalid input entered. Let's try that again. Type the \
corresponding letter and hit enter: """)
            field = query_field()
    
    return field


def update(field, update, index):
    """updates the applicable field with the user's input at the chosen UID

    Args:
        field (str): the case-sensitive heading of the database field the user
    wants to change
        update (str/int): the change that the user would like to make
        index (int): the UID that applies to the record the user would like to
    change
    """
    if field == "Title":
        SQL.execute('''UPDATE Books SET Title = ? WHERE ID = ?''', 
                    (update, index))
    elif field == "Author":
        SQL.execute('''UPDATE Books SET Author = ? WHERE ID = ?''',
                    (update, index))
    elif field == "QTY":
        SQL.execute('''UPDATE Books SET QTY = ? WHERE ID = ?''',
                    (update, index))
    elif field == "ID":
        SQL.execute('''UPDATE Books SET ID = ? WHERE ID = ?''',
                    (update, index))
    
    db.commit()


def validate_type(field):
    """called whenever the user has to input a value associated with the qty/id
    field, to make sure that their input can be cast to int, prompting them
    to re-enter it if they must

    Args:
        field (str): the name of the field that they are using

    Returns:
        int: the user's value cast to int, recursively calls itself until
    the user inputs a valid argument
    """
    if field == "ID" or field == "QTY":
        try:
            value = int(input("\t: "))
        except ValueError:
            print(f"\nInvalid input entered for {field}. Please re-enter a value.")
            return validate_type(field)
    else:
        value = input("\t: ")
    return value


def main_menu():
    """the landing page we always turn back to
    """    
    leave_menu = input("""
To interact with the database, type the letter that corresponds to what you 
would like to do and hit enter.

    a - add a new record
    s - search for a record
    u - update a record
    r - remove a record
    e - exit
    
        : """).strip().lower()
    match leave_menu:
        case "a":
            return add_record()
        case "s":
            return search_records()
        case "u":
            return update_record()
        case "r":
            return remove_record()
        case "e":
            exit()
        case _:
            print("Invalid input entered.")
            return go_to()


def go_to():
    """called at the end of every menu selection, prompts the user to enter if
    they want to go back to main menu (so that we don't obstruct their view at
    the end of every function call) and returns the main menu or exits the 
    program

    Returns:
        main menu function: takes the user back to main menu
    """
    go_to = input("\nTo go back to main menu, hit enter. ")
    if go_to == "":
        return main_menu()
    else:
        exit()


def add_record():
    """prompts the user for all the values of the new addition to the database
    and inserts it

    Returns:
        go to function: prompts the user to hit enter to go back to main menu
    """
    title = input("\nEnter the title of the book.\n\t: ")
    author = input("\nEnter the author of the book.\n\t: ")
    print("\nEnter the amount of the book in stock.")
    qty = validate_type("QTY")
    
    existing_book = lookup("Title, Author", (title, author))
    
    if existing_book:
        print("\nBook has already been recorded onto database.")
    else:
        SQL.execute('''INSERT INTO Books(Title, Author, QTY) 
                    VALUES(?, ?, ?)''', (title, author, qty))
        db.commit()
        print("\nBook successfully added to database and assigned a unique ID!")
    
    return go_to()


def search_records():
    """allows the user to choose a field to search and a value to search,
    performs a lookup on the database and displays the search results if
    found

    Returns:
        go to function: prompts the user to hit enter to go back to main menu
    """
    print("\nEnter the letter that corresponds to the field you want to search.")
    search_field = query_field()
    print("\nEnter the value you would like to search.")
    search_value = validate_type(search_field)
    
    search_result = lookup(search_field, search_value)
    
    if not search_result:
        print("\nNo matching results found.")
    else:
        print(f"\nAll results found for search '{search_value}'")
        print_table(search_result)
    
    return go_to()


def update_record():
    """prompts the user for the field to change and the value to change from.
    performs a lookup on the database and, if found, displays every applicable
    record for the user and prompts for confirmation to update. if given 
    confirmation, user is prompted for the replacement and the update(s) is/
    are made
    
    Returns:
        go to function: prompts the user to hit enter to go back to main menu
    """
    print("""\nEnter the letter that corresponds to the field you would like \
to change.""")
    update_field = query_field()
    print("\nEnter the value that you would like to change.")
    outdated_value = validate_type(update_field)
    
    search_result = lookup(update_field, outdated_value)
    
    if not search_result:
        print("\nCould not locate record with that value.")
    else:
        print_table(search_result)
        confirmation = input(f"""\nYou will be updating the {update_field} for \
all of the above records. Are you sure you want to proceed - (y/N)?\n\t: """).strip()
        if confirmation == "y":
            new_value = input("\nEnter the new value.\n\t: ")
            for i in range(len(search_result)):
                update(update_field, new_value, search_result[i][0])
            print("\nRecord(s) successfully updated!")
    
    return go_to()


def remove_record():
    """prompts the user for the field and value they'll use to perform the
    lookup. if found, displays every applicable result and prompts the user for
    confirmation to remove every displayed result. if given confirmation, 
    removes every single one. 
    
    Returns:
        go to function: prompts the user to hit enter to go back to main menu
    """
    print("""\nEnter the letter that corresponds with the field you'll be using \
to identify the defunct record(s).""")
    search_field = query_field()
    print("\nEnter the value you will be searching with.")
    defunct_record = validate_type(search_field)
    
    search_result = lookup(search_field, defunct_record)
    
    if not search_result:
        print("\nCould not locate record.")
    else:
        print_table(search_result)
        confirmation = input("""\nYou will be removing all of the above records.
Are you sure you want to proceed - (y/N)?\n\t: """).strip()
        if confirmation == "y":
            for i in range(len(search_result)):
                SQL.execute('''DELETE FROM Books WHERE ID = ?''',
                            (search_result[i][0],))
                db.commit()
    
    return go_to()


def main():
    main_menu()


if __name__ == "__main__":
    db = sqlite3.connect("e_bookstore.db")
    SQL = db.cursor()
    
    if os.path.isfile("./onset_book_log.txt") is True:
        database_initialised = False
        while database_initialised is False:
            preload_database = input('''\nFile with book data located. Would \
you like to make use of this file (y/N?)\n\t: ''').strip()
            match preload_database:
                case "y":
                    call_database()
                    print("\nPresets added successfully!")
                    database_initialised = True
                case "N":
                    confirmation = input('''\nPresets will be deleted. This is \
an irreversible action. Are you sure (y/N)? ''')
                    match confirmation:
                        case "y":
                            database_initialised = True
                            print("\nStarting fresh!")
        os.remove("./onset_book_log.txt")
    
    print('''Hello, and welcome to e-Bookstore HQ! 
        
    This menu down here is the brain of the operation. Through a series of 
    menus, your terminal will guide you through various functions by prompting 
    you to type a key - and only ever a single key - to get to where you need 
    to go. 
    
    Being a rather simplistic system, this manager is not nearly as smart as 
    you are, so please make sure that you know exactly what it is you'd like 
    to do before you go through with it, and make sure that your instructions 
    are within bounds! 
    
    Without further ado:
    ''')
    
    main()
    
    db.close()
