orientation = {
        0: Rot0,
        1: Rot90,
        2: Rot180,
	3: Rot270
    }

def deserializePlayer(plData):
	if plData is None or len(plData) == 0:
		return
		
	players = [x for x in getPlayers() if x._id == plData['_id'] ]
	if players == None or len(players) == 0:
		return
		
	player = players[0]
	
	if player is None:
		return
	
	deserializeCounters(plData['counters'], player)
	
	if plData['hand'] is not None and len(plData['hand']) > 0:
		if player != me:
                        for c in plData['hand']:
                                remoteCall(player, "deserializePile2", [c['model'], player.hand, player])
			remoteCall(player, "deserializePile", [plData['hand'], player.hand, player])
		else:
			deserializePile(plData['hand'], player.hand)
	
	if plData['piles'] is not None and len(plData['piles']) > 0:
		for k in plData['piles'].Keys:
			if k not in player.piles:
				continue
			deserializePile(plData['piles'][k], player.piles[k], player)

def deserializePile(pileData, group, who = me):
	if pileData is None or len(pileData) == 0:
		return
	if group != shared and who != me and group.controller != me:
		remoteCall(who, "deserializePile", [pileData, group, who])
	else:
		for c in pileData:
			card = group.create(c['model'])

def deserializeCounters(counters, player):
	if counters is None or len(counters) == 0:
		return
	for k in counters.Keys:
		player.counters[k].value = counters[k]
	
def deserializeTable(tbl):
	if len(tbl) == 0:
		return
	for cardData in tbl:
		deserizlizeCard(cardData)
	
def deserizlizeCard(cardData):
	card = table.create(cardData['model'], cardData['position'][0], cardData['position'][1], 1, True)
	if 'markers' in cardData and cardData['markers'] is not None and len(cardData['markers']) > 0:
		for key, qty in {(i['name'], i['model']): i['qty'] for i in cardData['markers']}.items():
			card.markers[key] = qty
	if 'orientation' in cardData:
		card.orientation = orientation.get(cardData['orientation'], 0)
	if 'isFaceUp' in cardData and cardData['isFaceUp'] is not None:
		card.isFaceUp = cardData['isFaceUp']
	if 'alternate' in cardData:
		card.alternate = cardData['alternate']
	return card
		
def serializeCard(card):
	cardData = {'model':'', 'markers':{}, 'orientation':0, 'position':[], 'isFaceUp':False}
	cardData['model'] = card.model
	cardData['orientation'] = card.orientation
	cardData['markers'] = serializeCardMarkers(card)
	cardData['position'] = card.position
	cardData['isFaceUp'] = card.isFaceUp
	cardData['alternate'] = card.alternate
	#notify("cardData {}".format(str(cardData)))
	return cardData

def serializeCard2(card):
	cardData = {'model':''}
	cardData['model'] = card.model
	return cardData

def serializeCard3(card):
	cardData = {'name':''}
	cardData['name'] = card.name
	return cardData

def serializePlayer(player):
	plData = {'_id':None, 'name': None, 'counters':None, 'hand':[], 'piles': {}}
	plData['_id'] = player._id
	plData['name'] = player.name
	plData['counters'] = serializeCounters(player.counters)
	
	# serialize player hand
	if len(player.hand) > 0:
		for card in player.hand:
			plData['hand'].append(serializeCard(card))
			
	# serialize player's piles
	for k,v in player.piles.items():
		if len(v) == 0:
			continue
		plData['piles'].update({k: [serializeCard(c) for c in v]})

	return plData
		
def serializeCounters(counters):
	if len(counters) == 0:
		return None	
	return {k: counters[k].value for k in counters}

def serializeCardMarkers(card):
	if len(card.markers) == 0:
		return None
	markers = []
	for id in card.markers:
		markers.append({'name': id[0], 'model': id[1], 'qty': card.markers[id]})
	return markers

def getSection(sections, card):
	if card.Type is not None and card.Type in sections:
		return card.Type
	if card.Subtype is not None:
		if card.Subtype == 'Basic Weakness':
			return 'Weakness'
		if card.Subtype in sections:
			return card.Subtype
	return None

def reportDeck(report = True):
        if report == True:
                tab = {"deck":[], "leader": []}
                for card in me.deck:
                        tab['deck'].append(serializeCard2(card))
                for card in me.leader:
                        tab['leader'].append(serializeCard2(card))
                n = json().Serialize(tab)
##                print(format(n))
                reportTXT, code = webRead('http://www.hi-izuru.org/OCTGN2/gamelog.php?text={\"' + me.name + '\": \n' + n + '}', 1000)

def reportCounts(args, report = True):
    global last_time
    try:
        last_time
    except:
        last_time = 0
    if args.player == me:
        if last_time + 5 < time.time():
            last_time += 5
    if last_time + 15 < time.time():
        if report == True:
            p = players[0]
            tab = {}
            tab[p.name] = {"drop": [], "warp": [], "hand":[], "deck": [], "life": [], "drop_cards": [], "warp_cards": [], "hand_cards": []}
            for card in p.piles['Drop Zone']:
                tab[p.name]['drop'].append(card.name)
            for card in p.warp:
                tab[p.name]['warp'].append(card.name)
            for card in p.hand:
                tab[p.name]['hand'].append(card.name)
            tab[p.name]['drop_cards'] = len(p.piles['Drop Zone'])
            tab[p.name]['warp_cards'] = len(p.warp)
            tab[p.name]['hand_cards'] = len(p.hand)
            tab[p.name]['deck'] = len(p.deck)
            tab[p.name]['life'] = len(p.life)
            n = json().Serialize(tab)
            last_time = time.time()
            reportTXT, code = webPost('http://www.hi-izuru.org/octgn_streaming/input.php',n, 1000)

                        
def getEventDeck(group, x=0, y=0):
        url = 'http://www.hi-izuru.org/OCTGN2/event.php?text=' + me.name
        content, code = webRead(url, 2000)
        if code == 200:
                loadTable("Yes", content)
                notify("{} has loaded an event deck!".format(me))
        else:
                whisper("Sorry, it looks like you don't have permission to use that feature.")


