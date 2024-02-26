import json
import os
import random as rng
import requests
from PIL import Image

"""
pre: files 'data/cache.json' and 'data/oracle.json' must exist.
param: cardName, name of card matching format of 'name' field of Oracle data.
return: JSON card object with name param:cardName from cache, from Oracle if not in cache, or None if not in Oracle.
post: card is cached if not in cache already.
"""
def lookupCard(cardName:str) -> dict:
    # Check in cache first to potentially save time
    with open('data/cache.json', encoding='utf8') as f:
        db = json.load(f)
        for card in db:
            # Compare target card to each card in cache (non-case-sensitive, ignores commas)
            if card['name'].lower().replace(",","") == cardName.lower().replace(",",""):
                return card
    # If not in cache, have to pull from full Oracle database
    with open('data/oracle.json', encoding='utf8') as f:
        db = json.load(f)
        for card in db:
            # Compare target card to each card in Oracle (non-case-sensitive, ignores commas)
            if card['name'].lower().replace(",","") == cardName.lower().replace(",",""):
                # Cache card for ease of future use
                cacheData(card)
                return card
        # Return error if card is not found in Oracle (DNE)
        return None
# END LOOKUPCARD

"""
pre: file 'data/cache.json' must exist.
return: random JSON card object from cache.
"""    
def lookupRandom() -> dict:
    # Only draw from cache for random card pool, as full Oracle pool would be costly and full of unwanted cards
    with open('data/cache.json', encoding='utf8') as f:
        db = json.load(f)
        numCards = len(db)
        randIndex = rng.randint(0,numCards-1)
        # Return card at random index in cache
        return db[randIndex]
# END LOOKUPRANDOM
    
"""
pre: file 'data/cache.json' must exist and have some data in it. If creating a new cache, this data can just be '[]'.
param: card, JSON card object to be cached.
post: card is written to cache.
"""           
def cacheData(card:dict):
    # Initialize new cache in case cache fails to open due to DNE
    cache = '[]'
    with open('data/cache.json', 'r') as f:
        # Read cache
        cache = f.read()
    with open('data/cache.json', 'w') as f:
        # Write back all but closing ']'
        f.write(cache[0:len(cache)-1])
    with open('data/cache.json', 'a') as f:
        # Add line break unless cache var is empty (would consist only of '[]')
        if len(cache) > 2:
            f.write(',\n')
        # Write in new card    
        json.dump(card, f)
        # Close cache
        f.write(']')
# END CACHEDATA
        
"""
pre: files 'data/cache.json' and 'data/oracle.json' must exist.
param: cardName, name of card matching format of 'name' field of Oracle data.
return: Relevant data from the card with name param:cardName is displayed.
"""
def printCard(cardName:str):
    # Check in cache first to potentially save time
    with open('data/cache.json', encoding='utf8') as f:
        db = json.load(f)
        for card in db:
            # Compare target card to each card in cache (non-case-sensitive, ignores commas)
            if card['name'].lower().replace(",","") == cardName.lower().replace(",",""):
                # Extract url for PNG image from card object
                imgSrc = card['image_uris']['png']
                # Request image from url and proceed if succesful
                response = requests.get(imgSrc)
                if response.ok:
                    # Write image content to a temp file
                    with open('data/temp.png', 'wb') as f:
                        f.write(response.content)
                    # Load and display temp file
                    img = Image.open('data/temp.png')
                    img.show()
                # Search is concluded
                return
    # If not in cache, have to pull from full Oracle database
    with open('data/oracle.json', encoding='utf8') as f:
        db = json.load(f)
        for card in db:
            # Compare target card to each card in Oracle (non-case-sensitive, ignores commas)
            if card['name'].lower().replace(",","") == cardName.lower().replace(",",""):
                # Extract url for PNG image from card object
                imgSrc = card['image_uris']['png']
                # Request image from url and proceed if succesful
                response = requests.get(imgSrc)
                if response.ok:
                    # Write image content to a temp file
                    with open('data/temp.png', 'wb') as f:
                        f.write(response.content)
                    # Load and display temp file
                    img = Image.open('data/temp.png')
                    img.show()
                # Search is concluded
                return
# END PRINTCARD

"""
pre: file corresponding to param:deckName must exist and have some data in it. If creating a new deck without the use of method:createDeck(), this data can just be '[]'.
param: cardName, name of card matching format of 'name' field of Oracle data.
param: deckName, name of deck to be added to.
post: card with name param:cardName is written to file with name corresponding to param:deckName.
return: -1 if file corresponding to param:deckName does not exist or param:cardName is not found in the cache or Oracle. 
"""   
def addToDeck(cardName:str, deckName:str) -> int:
    # Lookup target card and return with error if not found
    card = lookupCard(cardName)
    if card == None:
        return -1
    # Store path to deck file
    deckPath = 'data/decks/' + deckName + '.json'
    try:
        with open(deckPath, 'r') as f:
            # Read deck
            deck = f.read()
        with open(deckPath, 'w') as f:
            # Write back all but closing ']'
            f.write(deck[0:len(deck)-1])
        with open(deckPath, 'a') as f:
            # Add line break unless deck var is empty (would consist only of '[]')
            if len(deck) > 2:
                f.write(',\n')
            # Write in new card
            json.dump(card, f)
            # Close deck
            f.write(']')
    # Return error code if requested deck DNE
    except FileNotFoundError:
        return -1
    # Normal return
    return 0
# END ADDTODECK

"""
pre: file corresponding to param:deckName must exist and have some data in it. If creating a new deck without the use of method:createDeck(), this data can just be '[]'.
param: cardName, name of card matching format of 'name' field of Oracle data.
param: deckName, name of deck to be removed from.
post: card with name param:cardName is written to file with name corresponding to param:deckName.
return: -1 if file corresponding to param:deckName does not exist or param:cardName is not found in the deck. 
"""   
def removeFromDeck(cardName:str, deckName:str) -> int:
    # Store path to deck file
    deckPath = 'data/decks/' + deckName + '.json'
    try:
        with open(deckPath, encoding='utf8') as f:
            # Read deck (as list of dictionaries)
            deck = json.load(f)
            deckSize = len(deck)
        with open(deckPath, 'w') as f:
            # Clear deck file and write new opener
            f.write('[')  
        with open(deckPath, 'a') as f:
            # Initialize tracking var    
            found = False
            # Append each card except the target card back onto the deck
            for i in range(deckSize):
                card = deck[i]
                # Compare target card to each card in deck (non-case-sensitive, ignores commas)
                if card['name'].lower().replace(",","") == cardName.lower().replace(",","") and not found:
                    # First instance of target card found is not written back
                    found = True
                else:
                    # Write card
                    json.dump(card, f)
                    # Write a newline for every card except the last added
                    if i != deckSize-1:
                        f.write(',\n')
            # Close deck
            f.write(']')
            # return with error if target card was not found
            if not found:
                return -1
            # Normal return
            return 0
    # Return error code if requested deck DNE
    except FileNotFoundError:
        return -1
# END REMOVEFROMDECK

"""
param: deckName, name of deck to be created.
post: deck file with name corresponding to param:deckName is created.
return: -1 if file corresponding to param:deckName already exists. 
"""   
def createDeck(deckName:str) -> int:
    # Store path to deck file
    deckPath = 'data/decks/' + deckName + '.json'
    # Return error code if requested deck exists
    if os.path.isfile(deckPath):
        return -1
    # Write new file into existence
    with open(deckPath, 'w') as f:
        # Write brackets into new file
        f.write('[]')
    # Normal return
    return 0
# END CREATEDECK

"""
param: deckName, name of deck to be deleted.
post: deck file with name corresponding to param:deckName is deleted.
return: -1 if file corresponding to param:deckName does not exists. 
"""   
def deleteDeck(deckName:str) -> int:
    # Store path to deck file
    deckPath = 'data/decks/' + deckName + '.json'
    # If deck exists, delete it
    if os.path.isfile(deckPath):
        os.remove(deckPath)
        # Normal return
        return 0
    # Return error code if requested deck DNE
    return -1
# END DELETEDECK

"""
post: list of decks is printed.
"""   
def printDeckList():
    # Read all files in decks folder
    fileNames = os.listdir('data/decks/')
    for fileName in fileNames:
        # Exclude the _details file
        if fileName != '_details.txt':
            # Print current file's name minus the file extension
            nameLength = len(fileName)
            print(fileName[0:nameLength-5])
# END PRINTDECKLIST
            

"""
param: deckName, name of deck to be printed.
post: deck file with name corresponding to param:deckName is printed.
return: -1 if file corresponding to param:deckName does not exist. 
"""   
def printDeck(deckName:str) -> int:
    # Store path to deck file
    deckPath = 'data/decks/' + deckName + '.json'
    try:
        with open(deckPath, encoding='utf8') as f:
            # Initialize list of card dictonaries
            cardDicts = []
            # Read deck (as list of dictionaries)
            deck = json.load(f)
            # Print number of cards in deck
            print(str(len(deck)) + ' cards\n')
            for card in deck:
                # Store name of current card
                cardName = card['name']
                # Initialize tracking var for each card
                found = False
                for cardDict in cardDicts:
                    # Compare current card to each card in list of card dictionaries (non-case-sensitive, ignores commas)
                    if cardDict.get('name').lower().replace(",","") == cardName.lower().replace(",",""):
                        # If card name is already in list of dictionaries, increment quantity for that name
                        cardDict.update({'quantity' : cardDict.get('quantity')+1})
                        found = True
                if not found:
                    # If card name is not already in list of dictionaries, add it with a quantity of 1
                    cardDicts.append({'name' : cardName, 'quantity' : 1})
            # Sort completed list of dictionaries alphabetically by card name
            cardDicts.sort(key=lambda e : e['name'])
            for i in range(len(cardDicts)):
                # print current dictionary name and quantity (if quantity > 1)
                print(cardDicts[i].get('name'), end="")
                quantity = cardDicts[i].get('quantity')
                if quantity > 1:
                    print(" x" + str(quantity))
                else:
                    print("")
            # Normal return
            return 0
    # Return error code if requested deck DNE
    except FileNotFoundError:
        return -1
# END PRINTDECK
    
"""
param: deckName, name of deck to be exported.
param: fileName, name of file to be exported to.
post: deck file with name corresponding to param:deckName is exported.
return: -1 if file corresponding to param:deckName does not exist. 
"""   
def exportDeck(deckName:str, fileName:str) -> int:
    # Store path to deck file
    deckPath = 'data/decks/' + deckName + '.json'
    try:
        with open(deckPath, encoding='utf8') as f:
            with open(fileName, 'w') as dest:
                # Initialize list of card dictonaries
                cardDicts = []
                # Read deck (as list of dictionaries)
                deck = json.load(f)
                for card in deck:
                    # Store name of current card
                    cardName = card['name']
                    # Initialize tracking var for each card
                    found = False
                    for cardDict in cardDicts:
                        # Compare current card to each card in list of card dictionaries (non-case-sensitive, ignores commas)
                        if cardDict.get('name').lower().replace(",","") == cardName.lower().replace(",",""):
                            # If card name is already in list of dictionaries, increment quantity for that name
                            cardDict.update({'quantity' : cardDict.get('quantity')+1})
                            found = True
                    if not found:
                        # If card name is not already in list of dictionaries, add it with a quantity of 1
                        cardDicts.append({'name' : cardName, 'quantity' : 1})
                # Sort completed list of dictionaries alphabetically by card name
                cardDicts.sort(key=lambda e : e['name'])
                for i in range(len(cardDicts)):
                    # write current dictionary name and quantity (if quantity > 1) to destination file
                    dest.write(cardDicts[i].get('name'))
                    quantity = cardDicts[i].get('quantity')
                    if quantity > 1:
                        dest.write(" x" + str(quantity) + '\n')
                    else:
                        dest.write('\n')
                # Normal return
                return 0
    # Return error code if requested deck or destination file DNE
    except FileNotFoundError:
        return -1
# END EXPORTDECK
    
"""
pre: file 'data/decks/_details.txt' must exist and have its first character be a digit representing the number of default-named decks that currently exist. Currently allows for only 9.
return: returns the next default name available. 
"""   
def getDefaultDeckName() -> str:
    with open('data/decks/_details.txt', 'r') as f:
        # Read details
        details = f.read()
        # Store first digit of details
        n = details[0]
        # Construct default deckname using first digit of details
        deckName = 'deck' + n
        # Return
        return deckName
# END GETDEFAULTDECKNAME

"""
pre: file 'data/decks/_details.txt' must exist and have its first character be a digit representing the number of default-named decks that currently exist.
post: increments the digit stored in file 'data/decks/_details.txt' representing the number of default-named decks in existence.
"""   
def incDefaultDeckName():
    with open('data/decks/_details.txt', 'r') as f:
        # Read details
        details = f.read()
        # Store first digit of details
        n = details[0]
    with open('data/decks/_details.txt', 'w') as f:
        # Increment
        n = str(int(n) + 1)
        # Write back details with new first digit
        f.write(n + details[1:len(details)])
# END INCDEFAULTDECKNAME

"""
pre: file 'data/decks/_details.txt' must exist and have all but its first character representing the name of the deck last referenced by the user, or the default if no deck has been referenced.
return: returns the string stored in in file 'data/decks/_details.txt' representing the name of the deck last referenced by the user, or the default if no deck has been referenced.
"""   
def getRecentDeckName() -> str:
    # Initialize deck name
    deckName = ''
    with open('data/decks/_details.txt', 'r') as f:
        # Read details
        details = f.read()
        # Set deck name to be all but the first digit of details
        deckName = details[1:len(details)]
    # Return
    return deckName
# END GETRECENTDECKNAME

"""
pre: file 'data/decks/_details.txt' must exist and have all but its first character representing the name of the deck last referenced by the user, or the default if no deck has been referenced.
param: deckName, name of deck to be referenced in the future.
post: updates the string stored in in file 'data/decks/_details.txt' representing the name of the deck last referenced by the user to be param:deckName.
"""   
def updateRecentDeck(deckName:str):
    with open('data/decks/_details.txt', 'r') as f:
        # Read details
        details = f.read()
    with open('data/decks/_details.txt', 'w') as f:
        # Write back first digit of details
        f.write(details[0])
    with open('data/decks/_details.txt', 'a') as f:
        # Write back updated deck name as new remaining digits of details
        f.write(deckName)
# END UPDATERECENTDECK

"""
pre: file corresponding to param:deckName must exist and have some data in it. If creating a new deck without the use of method:createDeck(), this data can just be '[]'.
param: deckName, name of deck to goldfish with.
post: list seven random cards from the deck of name param:deckName
return: -1 if file corresponding to param:deckName does not exist. 
"""   
def goldfish(deckName:str) -> int:
    # Store path to deck file
    deckPath = 'data/decks/' + deckName + '.json'
    try:
        with open(deckPath, encoding='utf8') as f:
            # Read deck (as list of dictionaries)
            deck = json.load(f)
            # Initialize list of unique random indices of the deck
            uniqueRandIndices = []
            # Store deck size
            numCards = len(deck)
            # Initialize starting hand size
            handSize = 7
            # Reduce starting hand size if deck is too small
            if handSize > numCards:
                handSize = numCards
            # Generate a number of random indices of the deck equal to the hand size
            for _ in range(0,handSize):
                # Initialize random index
                randIndex = -1
                # Generate a random index of the deck until one that has not been stored already is generated
                while randIndex in uniqueRandIndices or randIndex == -1:
                    randIndex = rng.randint(0,numCards-1)
                # Store random index
                uniqueRandIndices.append(randIndex)
            # Initialize hand
            hand = []
            # Load cards into hand using list of random indices of the deck
            for i in uniqueRandIndices:
                hand.append(deck[i]['name'])
            # Print cards in hand    
            print(hand)
    # Return error code if requested deck DNE
    except FileNotFoundError:
        return -1
    # Normal return
    return 0
# END GOLDFISH

"""
param: request, a string containing a card name and optionally a quantity of that card. If included, the quantity should follow the card name and be preceded by a space.
post: list seven random cards from the deck of name param:deckName
return: -1 if file corresponding to param:deckName does not exist. 
"""   
def parseCardRequest(request:str) -> (str, int):
    # Store request string size
    length = len(request)
    # Find index of last white space character in request string
    splitIndex = request.rfind(" ")
    # If index was found and is not the final index, split request string along this index
    if splitIndex != -1 and splitIndex != length:
        finalStmt = request[splitIndex+1:length]
        # If the second part of the resulting string can be converted to an int, return both parts
        try:
            return request[0:splitIndex], int(finalStmt)
        # Catch error if above return failed
        except ValueError:
            pass
    # If the second part of the resulting string cannot be converted to an int, return the original string along with quantity 1
    return request, 1
# END PARSECARDREQUEST

"""
pre: User must have an unbroken internet connection during pull
post: Data in file data/oracle.json is updated from Scryfall.
"""   
def pullData():
    # Request main data interface from Scryfall API
    response = requests.get('https://api.scryfall.com/bulk-data')
    if response.ok:
        # Store main data interface string
        bulkDataStr = response.text
        # Convert main data interface string to JSON
        bulkDataJSON = json.loads(bulkDataStr)
        # Extract Oracle download URI from main data interface
        oracleURI = bulkDataJSON['data'][0]['download_uri']
        # Request Oracle data from URI
        response = requests.get(oracleURI)
        if response.ok:
            # Store Oracle data string
            oracleData = response.text
            with open('data/oracle.json', 'w', encoding='utf8') as f:
                # Write to Oracle file
                f.write(oracleData)
            # Report success and return
            print('Pull successful')
            return
    # Report failure if a bad response was received from either request
    print('Pull failed')
# END PARSECARDREQUEST


if __name__ == '__main__':
    print('Welcome to the MTG Fold!\nEnter "help" for help.')
    while True:
        print('> ', end=''),
        command = input().lower()
        if command == 'help' or command == 'h':
            print('Options:\n- New Deck\n- Clone Deck\n- Delete Deck\n- List Decks\n- View Deck\n- Export Deck\n- View Card\n- Add Card\n- Add From File\n- Remove Card\n- Replace Card\n- Goldfish\n- Pull Data\n- Quit')
        elif command == 'new deck' or command == 'new':
            defaultDeckName = getDefaultDeckName()
            print('Enter deck name: (' + defaultDeckName + ')')
            deckName = input()
            if deckName == '':
                deckName = defaultDeckName
                incDefaultDeckName()
            res = createDeck(deckName)
            if res == -1:
                print('Deck already exists')
            else:
                print(deckName + ' was created')
            updateRecentDeck(deckName)
        elif command == 'clone deck' or command == 'clone':
            recentDeckName = getRecentDeckName()
            print('Clone from: (' + recentDeckName + ')')
            deckName = input()
            if deckName == '':
                deckName = recentDeckName
            else:
                updateRecentDeck(deckName)
            defaultDeckName = 'new' + deckName
            print('Enter new deck name: (' + defaultDeckName + ')')
            deckName = input()
            if deckName == '':
                deckName = defaultDeckName
            createDeck(deckName)
            updateRecentDeck(deckName)
        elif command == 'delete deck' or command == 'delete':
            recentDeckName = getRecentDeckName()
            print('Delete deck: (' + recentDeckName + ')')
            deckName = input()
            if deckName == '':
                deckName = recentDeckName
            res = deleteDeck(deckName)
            if res == -1:
                print('Deck does not exist')
            else:
                print(deckName + ' was deleted')
        elif command == 'list decks' or command == 'list':
            printDeckList()
        elif command == 'export deck' or command == 'export':
            recentDeckName = getRecentDeckName()
            print('Export deck: (' + recentDeckName + ')')
            deckName = input()
            if deckName == '':
                deckName = recentDeckName
            else:
                updateRecentDeck(deckName)
            print('Export to file:')
            fileName = input()
            exportDeck(deckName, fileName)
            print('Exported ' + deckName)
        elif command == 'view deck':
            recentDeckName = getRecentDeckName()
            print('View deck: (' + recentDeckName + ')')
            deckName = input()
            if deckName == '':
                deckName = recentDeckName
            else:
                updateRecentDeck(deckName)
            printDeck(deckName)
        elif command == 'view card':
            print('Enter card name:')
            cardName=input()
            printCard(cardName)
        elif command == 'add card' or command == 'add':
            print('Enter card name:')
            cardName, cardQuantity = parseCardRequest(input())
            recentDeckName = getRecentDeckName()
            print('Add to: (' + recentDeckName + ')')
            deckName = input()
            if deckName == '':
                deckName = recentDeckName
            else:
                updateRecentDeck(deckName)
            if cardName == 'random':
                randCards = []
                for _ in range(cardQuantity):
                    card = lookupRandom()
                    cardName = card['name']
                    addToDeck(cardName, deckName)
                    randCards.append(cardName)
                print('Added the following cards:')
                for i in range(cardQuantity):
                    print(randCards[i])
            else:
                found = True
                for _ in range(cardQuantity):
                    res = addToDeck(cardName, deckName)
                    if res == -1:
                        found = False
                        break
                if found:
                    print("Added ", end="")
                    if cardQuantity > 1:
                        print(str(cardQuantity) + "x ", end="")
                    print(cardName)
                else:
                    print("Card not found.")
        elif command == 'add from file' or command == 'adds':
            print('Enter file name:')
            fileName = input()
            recentDeckName = getRecentDeckName()
            print('Add to: (' + recentDeckName + ')')
            deckName = input()
            if deckName == '':
                deckName = recentDeckName
            else:
                updateRecentDeck(deckName)
            try:
                with open(fileName, 'r') as f:
                    addStr = f.read()
                    addList = addStr.split('\n')
                    addCount = 0
                    failCount = 0
                    for addCard in addList:
                        cardName, cardQuantity = parseCardRequest(addCard)
                        addCount += cardQuantity
                        for _ in range(cardQuantity):
                            res = addToDeck(cardName, deckName)
                            if res == -1:
                                print('Card ' + cardName + ' was not found.')
                                failCount += 1
                                break
                    print(str(addCount-failCount) + ' cards added')
            except FileNotFoundError:
                print('Specified file does not exist')
        elif command == 'remove card' or command == 'remove':
            print('Enter card name: ')
            cardName, cardQuantity = parseCardRequest(input())
            recentDeckName = getRecentDeckName()
            print('Remove from: (' + recentDeckName + ')')
            deckName = input()
            if deckName == '':
                deckName = recentDeckName
            else:
                updateRecentDeck(deckName)
            found = True
            for _ in range(cardQuantity):
                res = removeFromDeck(cardName, deckName)
                if res == -1:
                    found = False
                    break
            if found:
                print("Removed ", end="")
                if cardQuantity > 1:
                    print(str(cardQuantity) + "x ", end="")
                print(cardName)
            else:
                print("Card not found in deck.")
        elif command == 'replace card' or command == 'replace':
            print('Enter name of card to remove: ')
            cardName, cardQuantity = parseCardRequest(input())
            recentDeckName = getRecentDeckName()
            print('Remove from: (' + recentDeckName + ')')
            deckName = input()
            if deckName == '':
                deckName = recentDeckName
            else:
                updateRecentDeck(deckName)
            found = True
            for _ in range(cardQuantity):
                res = removeFromDeck(cardName, deckName)
                if res == -1:
                    found = False
                    break
            if found:
                print("Removed ", end="")
                if cardQuantity > 1:
                    print(str(cardQuantity) + "x ", end="")
                print(cardName)
                print('Enter name of card to add: ')
                cardName, cardQuantity = parseCardRequest(input())
                if cardName.lower() == 'random':
                    randCards = []
                    for _ in range(cardQuantity):
                        card = lookupRandom()
                        cardName = card['name']
                        addToDeck(cardName, deckName)
                        randCards.append(cardName)
                    print('Added the following cards:')
                    for i in range(cardQuantity):
                        print(randCards[i])
                else:
                    found = True
                    for _ in range(cardQuantity):
                        res = addToDeck(cardName, deckName)
                        if res == -1:
                            found = False
                            break
                    if found:
                        print("Added ", end="")
                        if cardQuantity > 1:
                            print(str(cardQuantity) + "x ", end="")
                        print(cardName)
                    else:
                        print("Card not found.") 
            else:
                print("Card not found in deck.")       
        elif command == 'goldfish':
            recentDeckName = getRecentDeckName()
            print('Goldfish with: (' + recentDeckName + ')')
            deckName = input()
            if deckName == '':
                deckName = recentDeckName
            else:
                updateRecentDeck(deckName)
            goldfish(deckName)
        elif command == 'pull data' or command == 'pull':
            pullData()
        elif command == 'quit' or command == 'q':
            break
        else:
            print('Command not recognized. Enter "help" for help.')


            
