####################################################
##Import regular expression module, system file modules and time module.
import re
import nt
import sys
import time

##Initializing some variables.  The first four are for automatic card placement.
##The card placement code needs a total overhaul so these will be deprecated.
##comboColor defines what color border is placed around cards being combo'd.
##The last two variables assign the GUID for markers used represents +/- modifiers.
xBattle = -400
xEnergy = -400
xBattle2 = 325
xEnergy2 = 325
comboColor = "#00ff00"
CounterMarker =("Power", "3ef3165f-b02f-458a-823e-cb7d9247c269")
CounterMarker2 = ("PowerN", "8b12e609-12f3-4bec-9e8f-8ad2cf7c6d58")

##Initialize variables when a deck is loaded.  Global variables may be deprecated?
##reportDeck is a test function to report decklists to a server.
##This has never gone beyond testing, but it could be used for meta reporting.
def onDeckLoaded(args):
        init()
        global log_entries
        global last_time
        last_time = time.time()
        reportDeck(True)

##Initializing coordinate variables, redundant design with the global variables.
##specMode checks the player's local settings to check preference on Spectator Mode.
def init():
        xBattle = -400
        xEnergy = -400
        xBattle2 = 325
        xEnergy2 = 325
        global specMode
        specMode = getSetting("spectatorMode", False)

##Pretty sure this test function isn't used anymore.
def test():
        specMode2 = getSetting("spectatorMode", False)

##Complicated concept, will explain in the future.
def activate(card, x=0, y=0):
        if card.Name in card_list:
                for f in card_list[card.Name]:
                        f(*card_list[card.Name][f])
        else:
                whisper("This card doesn't have an automated ability.  Sorry!")

##Search "top" X cards for cards which meet arbitrarily complex criteria.
def tutorTopComplex(group=me.Deck, count=None, num=1, q='', zone=me.hand):
        mute()
        ##Initialize variable to track cards.
        topCards = []
        ##Loop over top X cards.
        for c in group.top(count):
                ##See if card matches critiera, if so, add to topCards list.
                if matchComplex(c, q):
                        topCards.append(c)
        ##Create dialob box to pick from valid options.
        dlg = cardDlg(topCards)
        ##Specify maximum number of cards that can be selected.
        dlg.max = num
        ##Show dialog box and store cards chosen by player.
        cardsSelected = dlg.show()
        ##Move any selected cards to the correct zone.
        if cardsSelected:
                for card in cardsSelected:
                        card.moveTo(zone)
                        notify("{} puts {} into their hand.".format(me, card.properties["Name"]))
        ##Shuffle the deck after.
        me.Deck.shuffle()  

##Check if card (c) meets criteria listed in q.
def matchComplex(c, q):
        for prop in q:
                if type(q[prop]) is str:
                        if not rSearch(c.properties[prop], q[prop]):
                               return()
                else:
                        t = q[prop][1]
                        v = q[prop][0]
                        if t == 'i':
                                if not rSearch(c.properties[prop], v):
                                        return()
                        elif t == 'e':
                                if not c.properties[prop] == v:
                                        return()
                        elif t == 'l':
                                if not int(c.properties[prop].split("(",1)[0]) < v:
                                        return()
                        elif t == 'g':
                                if not int(c.properties[prop].split("(",1)[0]) > v:
                                        return()
                        elif t == 'ge':
                                if not int(c.properties[prop].split("(",1)[0]) >= v:
                                        return()
                        elif t == 'le':
                                if not int(c.properties[prop].split("(",1)[0]) <= v:
                                        return()
                        elif t == 'ne':
                                if c.properties[prop] == v:
                                        return()
                        elif t == 'b':
                                if not c.properties[prop].startswith(v):
                                        return()
        return(c)

##Use a regular expression to search a string for specified value.
def rSearch(c,q=''):
        mute()
        ##Copy c variable to c_p to allow function to be extended in the future?
        ##Maybe this should be removed?
        c_p = c
        if re.search(q, c_p):
                return True

##Outdated function, all calls should go to tutorTopComplex instead.
def tutorTop(group=me.Deck, count=None, num=1, trait='', p='', zone=me.hand):
        mute()
        if count == None:
            count = askInteger("Scry how many cards?", 1)
        if count == None or count == 0:
            return
        topCards = []
        for c in group.top(count):
                if re.search(re.escape(p), c.properties[trait]):
                        topCards.append(c)
        dlg = cardDlg(topCards)
        dlg.max = num
        cardsSelected = dlg.show()
        if cardsSelected:
                for card in cardsSelected:
                        mute()
                        card.moveTo(zone)
                        notify("{} puts {} into their hand.".format(me, card.properties["Name"]))
        me.Deck.shuffle()

##Search for Dragon Balls.
def dbSearch(args='', num=7):
        mute()
        topCards = []
        for c in me.Deck:
                if c.Text.startswith('Dragon Ball'):
                        topCards.append(c)
        d = me.Deck.create('815eeabb-50d0-4f7f-9bea-10318289a24c',1)
        topCards.append(d)        
        for c in me.Life:
                if c.Text.startswith('Dragon Ball'):
                        topCards.append(c)        
        dlg = cardDlg(topCards)
        dlg.max = num
        dlg.title = "Searching Life and Deck for DBs"
        dlg.text = "DBs on the left are in your Deck, DBs on the right are in your Life.  Please don't select the display card."
        cardsSelected = dlg.show()
        if cardsSelected:
                for card in cardsSelected:
                        mute()
                        if card == d:
                                notifyBar("#FF00FF", "Please stop trying to break things  >.<")
                                return
                        card.moveTo(me.hand)
                        notify("{} puts {} into their hand.".format(me, card.properties["Name"]))
        d.delete()
        me.Deck.shuffle()
        me.Life.shuffle()

##Used for cards like Time Patrol Trunks.
##Needs further documentation due to awkward workaround.
def scry(group=me.Deck, count=None, num=1, trait='', p='', zone=me.hand, reveal=False):
    mute()
    if count == None:
        count = askInteger("Look at how many cards?", 1)
    if count == None or count == 0:
        return
    topCards = []
    for c in group.top(count):
        topCards.append(c)
        c.peek()
    dlg = cardDlg(topCards, [])
    dlg.max = count
    dlg.title = "Looking at the top X"
    dlg.label = "Top of Library"
    dlg.bottomLabel = "Bottom of Library"
    dlg.text = "Reorder cards to the top or bottom.\n\n(Select a card in the top box to put it in your hand.)"
    cardsSelected = dlg.show()
    for c in reversed(dlg.list):
        c.moveTo(group)
    for c in dlg.bottomList:
        c.moveToBottom(group)
    if cardsSelected:
        for card in cardsSelected:
                card.moveTo(me.hand)
                if reveal == True:
                        notify("{} puts {} into their hand.".format(me, card.Name))
                else:
                        notify("{} puts a card into their hand.".format(me))
    notify("{} looked at {} cards, putting {} on the bottom of their deck.".format(me, count, len(dlg.bottomList)))
    group.visibility = "none"


##Allows for sideboarding during a match.  Hasn't seen much use so perhaps remove?
def sideboard(group=me.Deck, x = 0, y = 0):
    mute()
    topCards = []
    for c in me.Deck.top(100):
        topCards.append(c)
        c.peek()
    dlg = cardDlg(topCards)
    botCards = []
    for c in me.sideboard:
        botCards.append(c)
        c.peek()
    dlg = cardDlg(topCards, botCards)
    dlg.title = "Sideboarding"
    dlg.label = "Deck"
    dlg.bottomLabel = "Sideboard"
    dlg.text = "Move cards between your deck and sideboard."
    cards = dlg.show()
    for c in reversed(dlg.list):
        c.moveTo(me.Deck)
    for c in dlg.bottomList:
        c.moveTo(sideboard)
    me.Deck.visibility = "none"
    me.Sideboard.visibility = "Me"

##Called whenever a card is moved.
##Checks if Spectator Mode is on.  If so, used workaround to show hand to
##spectators without showing it to the opponent and use reportCOunts.
##reportCounts will be documented in the future.
def moveCards(args):
        cards = args.cards
        global specMode
        if args.player == me:
                specMode = getSetting("spectatorMode", False)
                if specMode:
                        spectatorModeOn(False)
                        me.hand.visibility = 'all'
                        if len(players)>1:
                                x = 0
                                for p in players:
                                        if x > 0:
                                                me.hand.removeViewer(players[x])
                                        x = x+1
        reportCounts(args)
        return()


def initializeGame():
        mute()
        ##Get version number, check if there's a new changelog message since the last version.
        v1, v2, v3, v4 = gameVersion.split('.')  ## split apart the game's version number
        v1 = int(v1) * 1000000
        v2 = int(v2) * 10000
        v3 = int(v3) * 100
        v4 = int(v4)
        currentVersion = v1 + v2 + v3 + v4  ## An integer interpretation of the version number, for comparisons later
        lastVersion = getSetting("lastVersion", (currentVersion))
        for log in sorted(changelog):  ## Sort the dictionary numerically
                if lastVersion < log:  ## Trigger a changelog for each update they haven't seen yet.
                        stringVersion, date, text = changelog[log]
                        updates = '\n-'.join(text)
                        choice = confirm("What's new in {} ({}):\n-{}".format(stringVersion, date, updates))
                        if choice == False:
                                notify("What, you don't like my hard work?")
                        elif choice == None:
                                notify("Really, are you trying to break things?")
        setSetting("lastVersion", currentVersion)
        ##Pretty sure this is outdated and not used anymore(?)
        global log_entries
        log_entries = {}
        log_entries['Player:'] = me.name
        if len(players) == 2:
                log_entries['Enemy:'] = players[1].name


##Handle comboing.
def combo(card, x=0, y=25):
        mute()
        y = 10
        src = card.group
##        notify(src.name)
##        if src.name == "Hand":
##                pass
        if card.highlight == None:
                cardsInTable = [c for c in table if c.controller == me]
                if me._id == 1:
                        x = -400
                        for c in cardsInTable:
                                if c.position[0] >= x:
                                        x = c.position[0]
                else:
                        x = 325
                        for c in cardsInTable:
                                if c.position[0] < x:
                                        x = c.position[0]
                if me._id == 1:
                        card.moveToTable(x + 75, y)
                else:
                        card.moveToTable(x - 75, y*-1 -90)
                card.orientation = Rot270
                card.highlight = comboColor
                ##Check combo value of card and set markers showing it.
                if re.search("5000", card.Combo):
                        card.markers[CounterMarker] = 5000
                elif re.search("10000", card.Combo):
                        card.markers[CounterMarker] = 10000
                elif re.search("Super Combo", card.Text):
                        card.markers[CounterMarker] = 10000
                notify("{} combos with {} from their {}.".format(me, card, src.name))
        ##If command used on combo'd card, remove border and untap it.
        else:
                card.highlight = None
                card.orientation = Rot0
        
##Display changes stored in changelog.py if any new entries exist.
def changeLog(group, x = 0, y = 0):
        mute()
        allLog = sorted(changelog, reverse = True)  ##sorts the changelog so the most recent entries appear first.
        count = 1
        while count != 0:
                stringVersion, date, text = changelog[allLog[count - 1]]
                updates = '\n-'.join(text)
                num = askChoice("What's new in {} ({}):\n-{}".format(stringVersion, date, updates), [], customButtons = ["<- older", "close", "newer ->"])
                if num == 0 or num == -2: ## If the player closes the window
                        count = 0
                elif num == -1: ## If the player chooses 'older'
                        if len(allLog) > count:
                                count += 1
                elif num == -3 and count > 1: ## If the player chooses 'newer'
                        count -= 1

##Turn Spectator Mode on, save choice for future matches.
def spectatorModeOn(whisp=False, x = 0, y = 0):
        mute()
        global specMode
        specMode = True
        if whisp != False:
                whisper("{} turns on spectator mode.".format(me))
        setSetting("spectatorMode", True)

##Turn Spectator Mode off, save choice for future matches.
##Also reset visibility of hand to default.
def spectatorModeOff(card, x = 0, y = 0):
        mute()
        global specMode
        specMode = False
        me.hand.visibility = 'me'
        whisper("{} turns off spectator mode.".format(me))
        setSetting("spectatorMode", False)

##If called on a single card, send that card to the warp.
##If called on a group, send entire group to warp.
##That should only be possible by default for the Discard Pile.
def warp(group, x = 0, y = 0):
        if type(group) is Card:
                group.moveTo(me.piles["Warp"])
                notify("{} moves {} to their Warp.".format(me, group))
        else:
                mute()
                count = len(group)
                for card in group:
                        card.moveTo(me.piles["Warp"])
                notify("{} sends {} cards from their Drop Zone to the Warp!".format(me, count))


##Used via the Activate command, KOs cards which meet the specified criteria.
##See Activate documentation for further information.
def kill(count = 1, opponentOnly = False, zone=me.piles["Drop Zone"], q=""):
        mute()
        cardsInTable = []
        targets = []
        if opponentOnly:
                cardsInTable = [c for c in table if c.controller != me and c.orientation == Rot0 and not (re.search("Leader", c.Type))]
                for c in cardsInTable:
                        if matchComplex(c, q):
                                targets.append(c)
        else:
                cardsInTable = [c for c in table if c.orientation == Rot0 and not (re.search("Leader", c.Type))]
                for c in cardsInTable:
                        if matchComplex(c, q):
                                targets.append(c)
        if len(cardsInTable) < 1:
                whisper("There are no targets!")
                return
        dlg = cardDlg(cardsInTable)
        dlg.max = count
        cardsSelected = dlg.show()
        if cardsSelected:
                for card in cardsSelected:
                        if card.controller == me:
                                card.moveTo(zone)
                        else:
                                remoteCall(card.controller, "toDrop", card)
                        notify("{} kills {} !".format(me, card))

##Move card to hand.
def toHand(card):
        mute()
        card.moveTo(card.owner.hand)

##Move card to Drop.
def toDrop(card):
        mute()
        card.moveTo(card.owner.piles["Drop Zone"])

##Move card to top of deck.
def toTop(card):
        card.moveTo(card.owner.Deck)

##Move card to bottomof deck.
def toBottom(card):
        card.moveToBottom(card)

##Called as part of game setup process, plays leader to the table.
def playLeader(card):
        if me._id == 1:
                card.moveToTable(-405, 0)
        else: 
                card.moveToTable(330, -90)

			
#Sets up the game. Resets Your side. Draws 6, plays the Leader card
##Created by Manveer Singh.
def setup(group, x = 0, y = 0):
	cardsInTable = [c for c in table if c.controller == me and c.owner == me]
	cardsInLife = [c for c in me.piles['Life']] 
	cardsInHand = [c for c in me.hand]
	cardsInDrop = [c for c in me.piles['Drop Zone']]
	cardsInWarp = [c for c in me.piles['Warp']]
	if cardsInTable or cardsInHand or cardsInDrop or cardsInLife:
		if confirm("Are you sure you want to setup game? Current setup will be lost"):
                        for card in cardsInTable:
                                findLeader(card)
			for card in cardsInLife:
				findLeader(card)
			for card in cardsInHand:
				findLeader(card)
			for card in cardsInDrop:
				findLeader(card)
			for card in cardsInWarp:
				findLeader(card)
		else:
			return
	mute()
        global xBattle, xEnergy, xBattle2, xEnergy2
        init()
	if len(me.Deck) < 25: #We need at least 25 cards to properly setup the game
		whisper("Not enough cards in deck")
		return
	leaderCards = [c for c in me.piles['Leader']]	
	if len(leaderCards) != 1: 
		whisper("You must play exactly 1 leader card!")
		return
	for card in me.piles['Leader']:
		playLeader(card)
		break
	me.Deck.shuffle()
	for card in me.Deck.top(6): 
		card.moveTo(me.hand)
	notify("{} Draws six cards".format(me))	

##Sets up life.  Can be called manually or from the Mulligan function.
def setupLife(group, x = 0, y = 0): #Sets up 8 life
	for card in me.Deck.top(8):
		card.moveTo(me.piles['Life'], 0)
	notify("{} sets up their Life.".format(me))	

##Handles tapping and untapping.
def tap(card, x = 0, y = 0):
    mute()
    card.orientation ^= Rot90
    if card.orientation & Rot90 == Rot90:
        notify('{} taps {}.'.format(me, card))
    else:
        notify('{} untaps {}.'.format(me, card))	

def untapAll(group, x = 0, y = 0): #Modified it to account for Energy which will be played upside down
	mute()
	for card in group:
		if not card.controller == me:
			continue
		if card.orientation == Rot90:
			card.orientation = Rot0
		if card.orientation == Rot270:
			card.orientation = Rot180
	notify("{} untaps all their cards.".format(me))			

##Used card alternates to link unawakened and awakened sides.
def awaken(card, x = 0, y = 0): 
	mute()
	if (re.search("Leader", card.Type)):
		altName = card.alternateProperty('awakened', 'name')
                card.alternate = 'awakened'
		notify("{}'s' {} awakens to {}.".format(me, altName, card))
		card.Type = "Leader"

##Mostly for if players awaken when they shouldn't, also works with Wish leaders.
def unawaken(card, x = 0, y = 0): 
	mute()
	altName = card.alternateProperty('awakened', 'name')
        card.alternate = ''
	notify("{}'s' {} reverts to its base form.".format(me, altName, card))
	return

##Draws hand up to 6 cards, if Life isn't set up, set it up.
def mulligan(group):
        mute()
        cards = 6 - len(me.hand)
        if cards > 0:
                group.shuffle()
                drawMany(group, cards)
                notify("{} draws {} cards off the mulligan.".format(me, cards))
        if len(me.piles['Life']) == 0:
                setupLife("")

def token(group, x = 0, y = 0, guid='', quantity=1):
        ##Create tokens.
        ##If card information passed, used that information.
        if guid:
                token=table.create(guid, x, y, quantity)
        ##When card information not passed, prompt player for card information.
        else:
                ##Ask which token, and how many copies.
                guid, quantity = askCard({"Rarity":"Token"}, "And")
                ##Catch invalid response.
                if quantity == 0:
                        return
                ##Prevent game from crashing due to too many copies being made.
                if quantity < 10:
                        token = table.create(guid, x, y, quantity)
                else:
                        whisper("You can't make more than 9 tokens at once.")

			
def clearAll(group, x = 0, y= 0):
    notify("{} clears all targets and combat.".format(me))
    for card in group:
		if card.controller == me:
			card.target(False)
			card.highlight = None

def roll20(group, x = 0, y = 0):
    mute()
    n = rnd(1, 20)
    notify("{} rolls {} on a 20-sided die.".format(me, n))

def flipCoin(group, x = 0, y = 0):
    mute()
    n = rnd(1, 2)
    if n == 1:
        notify("{} flips heads.".format(me))
    else:
        notify("{} flips tails.".format(me))

##Turns cards face up/face down.		  
def flip(card, x = 0, y = 0):
    mute()
    if card.isFaceUp:
        notify("{} turns {} face down.".format(me, card))
        card.isFaceUp = False
    else:
        card.isFaceUp = True
        notify("{} turns {} face up.".format(me, card))

def discard(card, x = 0, y = 0): #Renamed
        mute()
        card.moveTo(me.piles['Drop Zone'])
	notify("{} discards {}".format(me, card))

##Power buffs/debuffs use separate counters.  These functions need to check if
##The opposite type exists to determine if more + counters should be added or -
##counters should be removed, and vice versa.  Add/Remove X may be bugged.
def addCounter5(card, x = 0, y = 0):
	mute()
	if card.markers[CounterMarker2] > 0:
                card.markers[CounterMarker2] -= 5000
        else:
                card.markers[CounterMarker] += 5000

def addCounter10(card, x = 0, y = 0):
	mute()
	card.markers[CounterMarker] += 10000

def addCounterN5(card, x = 0, y = 0):
	mute()
	if card.markers[CounterMarker] > 0:
                card.markers[CounterMarker] -= 5000
        else:
                card.markers[CounterMarker2] += 5000

def addCounterN10(card, x = 0, y = 0):
	mute()
	card.markers[CounterMarker] -= 10000

def removeCounter(card, x = 0 , y = 0):
	mute()
	card.markers[CounterMarker] -= 1
	  
def setCounter(card, x = 0, y = 0):
	mute()
	quantity = askInteger("How many counters", 0)
	if quantity:
                removeCounters(card)
        	card.markers[CounterMarker] = quantity

def setCounterN(card, x = 0, y = 0):
	mute()
	quantity = askInteger("How many counters", 0)
	if quantnty:
                removeCounters(card)
                card.markers[CounterMarker2] = quantity

def removeCounters(card, x = 0, y = 0):
        mute()
        for marker in card.markers:
                card.markers[marker] = 0

##Handles auto-placement of played cards.  Very crude, should be rewritten.		
def play(card, x = 0, y = 0): #Extra Cards will go to Drop after being played
	mute()
	x = 0
	cardsInTable = [c for c in table if c.controller == me]
	if me._id == 1:
                cards = [c for c in cardsInTable if c.position[1] >= 0 and c.position[1] <= 50]
                x = -400
                for c in cards:
                        if c.position[0] > x:
                                x = c.position[0]
        else:
                cards = [c for c in cardsInTable if c.position[1] >= -90 and c.position[1] <= -40]
                x = 325
                for c in cards:
                        if c.position[0] < x:
                                x = c.position[0]
	if card.Type=="Extra": card.moveTo(card.owner.piles['Drop Zone'])
        elif me._id == 1:
		card.moveToTable(x + 75, 0)
	else:
                card.moveToTable(x - 75, -90)
	notify("{} plays {}.".format(me, card))


##As with the play function, should be rewritten to work more smoothly.
def toEnergy(card, y = 90):
        mute()
        src = card.group
        cardsInTable = [c for c in table if c.controller == me and (c.orientation == Rot180 or Rot270)]
        if me._id == 1:
                x = -400
                for c in cardsInTable:
                        if c.position[0] >= x:
                                x = c.position[0]
        else:
                x = 325
                for c in cardsInTable:
                        if c.position[0] < x:
                                x = c.position[0]
        if me._id == 1:
                card.moveToTable(x + 75, y)
        else:
                card.moveToTable(x - 75, y*-1 -90)
        card.orientation = Rot180
        notify("{} charges {} from their {} as energy.".format(me, card, src.name))

##Charge top card of specified group to enegry.
def topCardEnergy(group, count = 1, x = 0, y = 0):
	mute()
	for i in range(0,count):
		if len(group) == 0: return
		card = group[0]
		toEnergy(card)

##Move specified card to life.
def toLife(card):
	mute()
	src = card.group
	card.moveTo(card.owner.piles['Life'])
	notify("{} puts a card from their {} as Life.".format(me, src.name))

##Used in game setup process.
def findLeader(card):
        if card.Type=="Leader":  card.moveTo(me.Leader)
        else: card.moveTo(me.deck)

def randomDiscard(group):
	mute()
	card = group.random()
	if card == None: return
	notify("{} randomly discards {}.".format(me,card.name))
	card.moveTo(me.piles['Drop Zone'])

##Allows for a prompt to ask how many cards should be drawn.
def draw(group, conditional = False, count = 1, x = 0, y = 0): #Added draw function to include choice
    mute()
    for i in range(0,count):
        if len(group) == 0:
            return
        if conditional == True:
            choiceList = ['Yes', 'No']
            colorsList = ['#FF0000', '#FF0000']
            choice = askChoice("Draw a card?", choiceList, colorsList)
            if choice == 0 or choice == 2:
                return 
        card = group[0]
        card.moveTo(card.owner.hand)
        notify("{} draws a card from their {}.".format(me, group.name))

##Like draw(), allow for prompt asking how many cards should be milled.
def mill(group, conditional = False, count = 1, x = 0, y = 0): #Added draw function to include choice
    mute()
    for i in range(0,count):
        if len(group) == 0:
            return
        if conditional == True:
            choiceList = ['Yes', 'No']
            colorsList = ['#6F6F6F', '#FF0000']
            choice = askChoice("Mill a card?", choiceList, colorsList)
            if choice == 0 or choice == 2:
                return 
        card = group[0]
        card.moveTo(card.owner.piles["Drop Zone"])
        notify("{} mills a card from their {}.".format(me, group.name))

def drawMany(group, count = None):
	if len(group) == 0: return
	mute()
	if count == None: count = askInteger("Draw how many cards?", 0)
	for card in group.top(count): card.moveTo(me.hand)
	notify("{} draws {} cards.".format(me, count))

def drawBottom(group, x = 0, y = 0):
	if len(group) == 0: return
	mute()
	group.bottom().moveTo(me.hand)
	notify("{} draws a card from the bottom.".format(me))

def shuffle(group):
	group.shuffle()
  
def lookAtTopCards(num, targetZone='hand'): #Added function for looking at top X cards and take a card
    mute()
    notify("{} looks at the top {} cards of their deck".format(me,num))
    cardList = [card for card in me.Deck.top(num)]
    choice = askCard(cardList, 'Choose a card to take')
    toHand(choice, show = True)
    me.Deck.shuffle() 
	
def lookAtDeck(): #For Automation
    mute()
    notify("{} looks at their Deck.".format(me))
    me.Deck.lookAt(-1)
	
#---------------------------------------------------------------------------
# Phases
#---------------------------------------------------------------------------
##Not used, leftover code from previous game which was used as template.
##Should probably be deleted, but need to verify doing so won't break anything.

def showCurrentPhase(phaseNR = None): # Just say a nice notification about which phase you're on.
   if phaseNR: notify(phases[phaseNR])
   else: notify(phases[num(me.getGlobalVariable('phase'))])

def endMyTurn(opponent = None):
   if not opponent: opponent = findOpponent()
   me.setGlobalVariable('phase','0') # In case we're on the last phase (Force), we end our turn.
   notify("=== {} has ended their turn ===.".format(me))
   opponent.setActivePlayer() 
      
def nextPhase(group = table, x = 0, y = 0, setTo = None):  
# Function to take you to the next phase. 
   mute()
   phase = num(me.getGlobalVariable('phase'))
   if phase == 3: 
      endMyTurn()
      return  
   else:
      if not me.isActivePlayer and confirm("Your opponent does not seem to have ended their turn yet. Switch to your turn?"):
         remoteCall(findOpponent(),'endMyTurn',[me])
         rnd(1,1000) # Pause to wait until they change their turn
      phase += 1
      if phase == 1: goToDraw()
      elif phase == 2: goToPlanning()
      elif phase == 3: goToDeclare()

def goToDraw(group = table, x = 0, y = 0): # Go directly to the Balance phase
   mute()
   me.setGlobalVariable('phase','1')
   showCurrentPhase(1)
         
def goToPlanning(group = table, x = 0, y = 0): # Go directly to the Balance phase
   mute()
   me.setGlobalVariable('phase','2')
   showCurrentPhase(2)
         
def goToDeclare(group = table, x = 0, y = 0): # Go directly to the Balance phase
   mute()
   me.setGlobalVariable('phase','3')
   showCurrentPhase(3)

#---------------------------------------------------------------------------
# Meta Functions
#---------------------------------------------------------------------------
##Not used, leftover code from previous game which was used as template.
##Should probably be deleted, but need to verify doing so won't break anything.

def findOpponent(position = '0', multiText = "Choose which opponent you're targeting with this effect."):
   opponentList = fetchAllOpponents()
   if len(opponentList) == 1: opponentPL = opponentList[0]
   else:
      if position == 'Ask':
         choice = SingleChoice(multiText, [pl.name for pl in opponentList])
         opponentPL = opponentList[choice]         
      else: opponentPL = opponentList[num(position)]
   return opponentPL

def fetchAllOpponents(targetPL = me):
   opponentList = []
   if len(getPlayers()) > 1:
      for player in getPlayers():
         if player != targetPL: opponentList.append(player) # Opponent needs to be not us, and of a different type. 
   else: opponentList = [me] # For debug purposes
   return opponentList   

def playerside():
   if me.hasInvertedTable(): side = -1
   else: side = 1   
   return side
   
 
#------------------------------------------------------------------------------
# Button and Announcement functions
#------------------------------------------------------------------------------
##Allow users to send standardized messages quickly to reduce typing needing.

def BUTTON_NR(group = None,x=0,y=0):
   notify("--- {} has no counters.".format(me))

def BUTTON_NB(group = None,x=0,y=0):  
   notify("--- {} is using no blockers.".format(me))

def BUTTON_NC(group = None,x=0,y=0):  
   notify("--- {} isn't comboing any cards.".format(me))

def BUTTON_FC(group = None,x=0,y=0):
        mute()
        comboTotal = 0
        for card in table:
                if card.highlight == comboColor and card.controller == me:
                      comboTotal += card.markers[CounterMarker]

        if comboTotal != 0:
                notify("--- {} is finished comboing, with {} Combo Power".format(me,comboTotal))
        else:
                notify("--- {} is finished comboing.".format(me))
                              


##I don't think this function is used currently.
def declarePass(group, x=0, y=0):
   notify("--- {} Passes".format(me))    

