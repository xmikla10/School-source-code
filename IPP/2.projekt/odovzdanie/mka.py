#!/usr/bin/env python3

#MKA:xmikla10

import os
import sys
import re
import string


# *********************************************************#
# NAZVY PROMENNYCH A FUNKCII :

# TI, KTERE POVAZUJEM ZA HLAVNI MAJI PREVAZNE SLOVENSKY NAZEV

# TI, KTERE SOU POMOCNE MAJI PREVAZNE ANGLICKY NAZEV
# *********************************************************#


# Funkce "main" reprezentuje hlavny beh programu
def main():
	#spracuje vstupni argumenty
	arguments = processArguments()
	if ( arguments.mka_wht == True ):
		whtInput = wht(arguments)
		arguments.mka_input = str(whtInput)

	#spracuje vstupni soubor
	inputFile = processInput(arguments)

	#overi semanticke chyby, ... 
	semantic  = Semantic(inputFile)

	# ak je zadane rozsirenie --wsfa
	if ( arguments.mka_wsfa == True ):
		semantic.wsfa(True)

	#overeni zda je automat dobre specifikony
	semantic.wellSpecAutomat()

	#ak je zadan -f alebo --find-non-finishing
	if ( arguments.mka_f == True ):
		semantic = semantic.pomFneukoncStav()
		if ( semantic ):
			saveTo = arguments.mka_output
			saveTo.write(str(semantic[0]))
			sys.exit()

	#ak je zadan -m alebo --minimize
	if ( arguments.mka_m == True ):
		semantic = semantic.minimalizacia()
	#pomocna promnenna reprezentujici nazev souboru	

	saveTo = arguments.mka_output
	#zapis do soubotu
	saveTo.write(str(semantic))
#********************************************************************************************#
# Trida reprezentuujici spracovani vstupu
class Arguments(object):
	 def __init__(self):
	 	self.mka_input = sys.stdin
	 	self.mka_output = sys.stdout
	 	self.mka_f = False
	 	self.mka_m = False
	 	self.mka_i = False
	 	self.mka_wht = False
	 	self.mka_wsfa = False
#********************************************************************************************#
# Funkce pro spracovani vstupnich argumentov
def processArguments():
	arguments = Arguments()

	for x in sys.argv[1:]:
		if x == '--help':
			if len(sys.argv) !=  2:
				print('Zle zadan argument --help')
				print('Pre vypis napovedy zadajte len --help')
				sys.exit(1)
			print("""--help
						pre vypisanie napovedy
					--input=filename
						zadany vstupny subor filename s popisom dobre specifikovaneho konecneho automatu
					--output=filename
						zadany vstupny subor filename s popisom vystledneho ekvivalentniho konecneho
						automatu v predepsanem formatu vystupu
					-f, --find-non-finishing
						hleda neukoncujici stav zadaneho dobre specifikovaneho konecneho automatu.
						Parametr nelze kombinovat s parametrem -m(resp. --minimalize)
					-m, --minimize
						provede minimalizaci dobre specifikovaneho konecneho automatu.
						Parametr nelze kombinovat s parametrem -f(resp. --find-non-finishing)
					-i, --case-insensitive
						nebude bran ohled na velikost znaku pri porovnanani symbolu ci stavu, tj.
						ve vystupu potom budou vsechna velka pismena prevedena na mala""")
			sys.exit(0)

		if x == '-f' or x == '--find-non-finishing':
			if arguments.mka_f == True: sys.exit(1) # pouzite viac ako raz s
			elif arguments.mka_m == True: sys.exit(1)
			else: arguments.mka_f = True

		if x == '-m' or x == '--minimize':
			if arguments.mka_m == True: sys.exit(1)   # pouzite viac ako raz 
			elif arguments.mka_f == True: sys.exit(1)
			else: arguments.mka_m = True
			
		if x == '-i' or x == '--case-insensitive':
			if arguments.mka_i == True: sys.exit(1)  # pouzite viac ako raz 
			else: arguments.mka_i = True

		if x == '--wsfa':
			if arguments.mka_wsfa == True: sys.exit(1)  # pouzite viac ako raz 
			else: arguments.mka_wsfa = True

		if x == '-w' or x == '--white-char':
			if arguments.mka_wht == True: sys.exit(1)
			else: arguments.mka_wht = True

		else:
			#b-begin, m-middle, e-end
			b,m,e = x.partition('=') 	

			if b == '--input':
				if e != '':
					if open(e, encoding="utf-8", mode="r"): arguments.mka_input = open(e, encoding="utf-8", mode="r")
					else:  sys.exit(1)

			if b == '--output':
				if e != '':
					if open(e, encoding='utf-8', mode="w"): arguments.mka_output = open(e, encoding="utf-8", mode="w")
					else: sys.exit(1)

			if( b != '--input' and b != '--output' and x != '--wsfa' and x != '--white-char' and x != '-w' and x != '-m' and x != '--minimize' and x != '-f' and x != '--find-non-finishing' and x != '-i' and x != '--case-insensitive'):
				print( x + ' - neznamy argument, pre pomoc napis --help')
				sys.exit(1)
			
	return arguments
#********************************************************************************************#
# Pomocna funkce pro třídu Semantic
def toArray( first, z ,number, element):
	try:
		pom = first[first.index(element[z*3 + number].pom)]
		return pom
	except:
		sys.exit(61)
#********************************************************************************************#
# Trida reprezentujici spravnu semantiku vstupniho souboru, minimalizaci konecneho automatu,...
class Semantic(object):
	#inicializuje objekty a kontroluje semanticke chyby
	def __init__(self, inputFile):
		self.pocStav = None
		self.konStav = []
		self.stav = []
		trueORfalse = True
		self.pomPole = []
		self.abeceda = []
		self.pravidlo = []
		self.pomPole2 = []
		#enumerate pouzivam preto lebo chcem prechadzat pole
		#a nechcem prist o pravidelne sa zvysujucu hodnotu
		if ( trueORfalse == True ):
			for x, element in enumerate(inputFile):
				if ( x == 0 ):
					for stav in element:
						if ( stav.pom not in self.stav ):
							self.stav.insert(len(self.stav), Stav(stav.pom))

				if ( x == 1 ):
					for symbol in element:
						if ( symbol.pom not in self.abeceda ):
							self.abeceda.insert(len(self.abeceda), Symbol(symbol.pom))

				if ( x == 2 ):
					length = len(element) / 3
					for z in range( 0, int(length)):
						fromS = toArray( self.stav, z, 0, element)
						symbol = toArray( self.abeceda, z, 1, element)
						toS = toArray( self.stav, z, 2, element)

						pravidlo = Pravidlo(fromS, toS, symbol)

						if ( pravidlo not in self.pravidlo):
							self.pravidlo.insert( len(self.pravidlo), pravidlo)

				if ( x == 3 ):
					self.pocStav = toArray( self.stav, 0, 0, element)

				if ( x == 4 ):
					for konStavPom in element:
						konStav = self.stav[self.stav.index(konStavPom.pom)]
						if self.konStav == False: sys.exit(61)
						if (konStav not in self.konStav):
							self.konStav.insert(len(self.konStav), konStav)
		else:
			sys.exit(61)
		alfabet = len(self.abeceda)
		if( alfabet == 0): sys.exit(61)

#********************************************************************************************#
# Funkcia ktera overuje zda je automat dobre specifikovan
	def wellSpecAutomat(self):

		for stav in self.stav:
			if ( stav != self.pocStav ):
				pravidla = self.pomPravidlo(stav, None, 2, 2)
				length = len(pravidla)
				if (length == 0):
					pom = stav
					sys.exit(62)
				else:
					pom = False
			else:
				pom = False

		for stav in self.stav:
			for symbol in self.abeceda:
				pravidla = self.pomPravidlo(stav, symbol, 2, 1)
				length = len(pravidla)
				if ( (pravidla == False) or (length == 0) ):
					sys.exit(62)

		self.pomFneukoncStav()
		return True

#********************************************************************************************#
# Funkcia pre rozsirenie --wsfa
	def wsfa(self, pom):
		pomFalse = None
		pomFneukoncStav = None

		pomFneukoncStav = self.pomFneukoncStav()
		for stav in pomFneukoncStav:
			for pravidlo in self.pomPravidlo( stav, None, 2, 1):
				if ( pom == True):
					self.pravidlo.remove(pravidlo)
				else:
					break
			for pravidlo in self.pomPravidlo( stav, None, 2, 2):
				if ( pom == True):
					self.pravidlo.remove(pravidlo)
				else:
					break

		self.stav.remove(stav)

		for stav in self.stav:
			for symbol in self.abeceda:
				pravidlo = self.pomPravidlo( stav, symbol, 2, 1)
				length = len(pravidlo)
				if ( length == 0 and pomFalse == None):
					pomFalse = Stav("qFALSE")
					length2 = len(self.stav)
					self.stav.insert( length, pomFalse)
				length3 = len(self.pravidlo)
				self.pravidlo.insert( length3, Pravidlo(stav, symbol, pomFalse))

#********************************************************************************************#
# Pomocna funkce pro nalezeni pravidla v konecnem automatu
	def pomPravidlo(self, stav, symbol, pom1=1,pom2=1):
		if ( pom1 == 1 ): pom1 = 1
		else: pomArray = []

		for rule in self.pravidlo:
			if ( pom2 == 2 ): control = rule.toS
			else: control = rule.fromS

			if (control == stav):
				if(rule.symbol == symbol or symbol is None):
					if ( pom1 == 2 ):
						length = len(pomArray)
						pomArray.insert(length, rule)
					else: return rule

		if ( pom1 == 1 ): return False
		else: return pomArray	
#********************************************************************************************#
# Pomocna funkce pro zisteni neukoncujuciho stavu
	def pomFneukoncStav(self):
		zasobnik = self.konStav[:]
		pomArray = []
		pomArray2 = []
		pom = True
		neukoncenyStav = []

		if ( pom == True):
			while zasobnik:
				current = zasobnik.pop()
				if current not in pomArray:
					length = len(pomArray)
					pomArray.insert( length, current)
				pravidla = self.pomPravidlo(current, None, 2, 2)

				for pravidlo in pravidla:
					if pravidlo.fromS not in pomArray:
						length = len(zasobnik)
						zasobnik.insert(length, pravidlo.fromS)
		else:
			pom = True

		for stav in self.stav:
			if stav not in pomArray:
				length = len(neukoncenyStav)
				neukoncenyStav.insert( length, stav)

		length = len(neukoncenyStav)

		if(neukoncenyStav):
			return neukoncenyStav

		if ( length > 1 ):
			sys.exit(62)
			
#********************************************************************************************#
# Funkce reprezentujici minimalizaci konecneho automatu
	def minimalizacia(self):
		pom1 = True
		skupina = []
		trueORfalse = True
		pomList = []
		stav = []
		pom2 = True
		symbolP = []
		pravidlo = []
		finall = []
		pomArray = []

		length = len(skupina)
		skupina.insert(length, StavG(self.konStav))

		for state in self.stav:
			if state not in self.konStav:
				if( pom2 == True):
					length = len(pomList)
					pomList.insert( length, state)
		length = len(skupina)
		skupina.insert( length, StavG(pomList))

		while trueORfalse != False:
			trueORfalse = False
			for group in skupina:
				groupArray = dict()
				for symbol in self.abeceda:
					for state in group:
						rule = self.pomPravidlo(state, symbol, 1, 1)
						outState = rule.toS
						for pomGroup in skupina:
							if( outState in pomGroup):
								if( pom2 == True):
									groupPom1 = pomGroup
								else: break
						if (groupPom1 in groupArray):
							if( pom2 == True):
								length = len(groupArray[groupPom1])
								groupArray[groupPom1].insert( length, state)
							else: break
						else: groupArray[groupPom1] = [state]

					if ( len(groupArray) != 1 ):
						for groupPom2, states in groupArray.items():
							if( pom2 == True):
								length = len(skupina)
								skupina.insert( length, StavG(states))
						if( pom2 == True):
							skupina.remove(group)
							trueORfalse = True
							break
					else: groupArray.clear()

				if( trueORfalse == True ): break
		for rule in self.pravidlo:
			for group in skupina:
				if (rule.fromS in group):
					if( pom2 == True):fromS = group
			symbol = rule.symbol
			for group in skupina:
				if ( rule.toS in group ):
					if( pom2 == True): toS = group
			if( pom2 == True):
				length = len(pravidlo)
				pravidlo.insert(length, Element(str(fromS), False))
				length = len(pravidlo)
				pravidlo.insert(length, Element(symbol.name, True))
				length = len(pravidlo)
				pravidlo.insert(length, Element(str(toS), False))
			else: break

		for group in skupina: 
			if( pom2 == True): group.stav.sort()

		for group in skupina:
			if( pom2 == True):
				length = len(stav)
				stav.insert(length, Element(str(group), False))
			else: break

		for symbol in self.abeceda:
			if( pom2 == True):
				length = len(symbolP)
				symbolP.insert(length, Element(symbol.name, True))
			else: break

		for group in skupina:
			if (self.pocStav in group):
				pom = group
				pom = str(pom)
		zacS = [ Element(pom, False) ]

		for group in skupina:
			for finalStav in self.konStav:
				if (finalStav in group):
					if( pom2 == True):
						length = len(finall)
						finall.insert(length, Element(str(group), False))
						break

		array = [stav, symbolP, pravidlo, zacS, finall]
		return Semantic(array)

#********************************************************************************************#
# Pomocna funkce pro vypis konecneho automatu
	def __str__(self):

		tmp = True
		pom = "(\n{"
		char = ", "

		length = len(self.stav)
		if length == 1: pom = pomStr(self.stav, s, 0)
		elif length > 1:
			self.stav.sort()
			for stav in self.stav[0:-1]:
				if ( tmp == True):
					string = str(stav)
					pom = pom + string + char
			pom = pomStr(self.stav, pom, -1)
		pom = pomStr2(pom, 1)

		length = len(self.abeceda)
		if length == 1: pom = pomStr(self.abeceda, pom, 0)
		elif length > 1:
			self.abeceda.sort()
			for symbol in self.abeceda[0:-1]:
				if ( tmp == True):
					string = str(symbol)
					pom = pom + string + char
			pom = pomStr(self.abeceda, pom, -1)
		pom = pomStr2(pom, 5)

		length = len(self.pravidlo)
		if length == 1: pom = pomStr(self.pravidlo, pom, 0)
		elif length > 1:
			self.pravidlo.sort()
			for pravidlo in self.pravidlo[0:-1]:
				if ( tmp == True):
					string = str(pravidlo)
					pom = pom + string + ",\n"
			pom = pomStr(self.pravidlo, pom, -1)
		pom = pomStr2(pom, 3)

		string = str(self.pocStav)
		if self.pocStav != None: pom+= string
		pom = pomStr2(pom, 4)

		length = len(self.konStav)
		if length == 1: pom = pomStr(self.konStav, pom, 0)
		elif length > 1:
			self.konStav.sort()
			for stav in self.konStav[0:-1]:
				if ( tmp == True):
					string = str(stav)
					pom = pom + string + char
			pom = pomStr(self.konStav, pom, -1)
		pom= pomStr2(pom, 2)

		return pom
#********************************************************************************************#
# Pomocna trida pro ukladani do retazcov
class White:
	withoutComment = ""
	finall = ""
	nazovInputu = ""
#********************************************************************************************#
# Funkcia pre rozsirenie WHT
# Nieje uplne dokoncena a pri vypise zle odriadkuje pravidla
def wht(arguments):
	s1 = White()
	pomList = []
	for line in arguments.mka_input:
		for char in line:
			if char == '#': break
			else:
				s1.withoutComment += line
				break

	length = len(s1.withoutComment)
	i = 0
	first = True
	whiteSpace = False
	second = False
	pom2 = False

	while i <= length-1 and second == False:
		for line in s1.withoutComment:
			for char in line:
				if(second == True): break
				elif(char == '('):
					i += 1
					s1.finall += char
				elif (char == '\n'):
					i += 1
					s1.finall += char
				elif( first == False):
					if (char == ' '):
						i += 1
						s1.finall += char
				elif ( first == True):
					if(char == '{'):
						i += 1
						s1.finall += char
					elif ( char.isalpha() or char.isdigit() ) and char == ',':
						i += 1
						s1.finall += char
					elif ( char.isalpha() or char.isdigit() ) and char != ',':
						i += 1
						s1.finall += char
						s1.finall += ','
					elif(char == '}'):
						x = len(s1.finall)-1
						if( s1.finall[x] == ','):
							s1.finall = s1.finall[:-1]
							s1.finall += char
							first = False
							i += 1
							second = True
							break
						else:
							i += 1
							s1.finall += char
							first = False
					elif(char == ' '):
						if whiteSpace == False:
							i += 1
							s1.finall += char
							whiteSpace = True
						elif whiteSpace == True:
							i += 1
							whiteSpace = False

	i += 1
	apostrof = False
	pomBreak = False
	s1.withoutComment = s1.withoutComment[i:length-1]
	for line in s1.withoutComment:
			for char in line:
				if(pomBreak == True): break
				if(char == ','):
					i += 1
					s1.finall += char
				elif( char == '\''):
					i += 1
					s1.finall += char
					apostrof = True
				elif (char == '\n'):
					i += 1
					s1.finall += char
				elif( char == ','):	
					i += 1
					s1.finall += char
				elif( char == '{'):	
					i += 1
					s1.finall += char
				elif ( char.isalpha() or char.isdigit() ):
					if(apostrof == True):
						i += 1
						s1.finall += char
					else:
						i += 1
						s1.finall += '\''
						s1.finall += char
						s1.finall += '\''
						apostrof = False
				elif( char == '}'):	
					i += 1
					s1.finall += char
					pomBreak = True
					s1.finall += ','
					s1.finall += '\n'
					s1.finall += '{'
					s1.finall += '\n'
					break	
	i -= 5
	pomBreak = False
	apostrof = False
	firstOrLast = True
	s1.withoutComment = s1.withoutComment[i:length-1]
	x = 1

	for line in s1.withoutComment:
			for char in line:
				if(pomBreak == True): break
				elif( char == '}'):	
					s1.finall = s1.finall[:-2]
					s1.finall += '\n'
					i += 1
					s1.finall += char
					s1.finall += ','
					pomBreak = True
					break
				elif( char == '-'):	
					i += 1
					s1.finall += char
				elif( char == '\n'):	
					i += 1
					s1.finall += char
				elif( char == '>'):	
					i += 1
					s1.finall += char
				elif( char == ' '):	
					i += 1
					s1.finall += char
				elif ( char.isalpha() or char.isdigit() ):
					if( x <= 3):
						if( firstOrLast == True):
							i += 1
							x += 1
							s1.finall += char
							firstOrLast = False
							if( x > 3):
								x = 1
								firstOrLast = True
								s1.finall += ','
						elif(firstOrLast == False):
							if ( apostrof == True):
								i += 1
								x += 1
								s1.finall += char
								firstOrLast = True
								apostrof = False
							elif ( apostrof != True):
								i += 1
								x += 1
								s1.finall += '\''
								s1.finall += char
								s1.finall += '\''
								firstOrLast = True

	i -= 4
	s1.withoutComment = s1.withoutComment[i:length-1]
	s1.finall += s1.withoutComment	
	return s1.finall
#********************************************************************************************#
# 1.Pomocni funkce pro spracovani __str__  v tride Semantic        
def pomStr(x, pom, number):
	pom += str(x[number])
	return pom;
#********************************************************************************************#
# 2.Pomocni funkce pro spracovani __str__  	v tride Semantic                
def pomStr2(pom, number):
	if( number == 1):
		pom += "},\n{"
	elif( number == 2):
		pom += "}\n)"
	elif( number == 3):
		pom += "\n},\n"
	elif( number == 4):
		pom += ",\n{"
	else:
		pom += "},\n{\n"
	return pom

#********************************************************************************************#
# Pomocni funkce pro overeni nazvu identifikatoru cez regularni vyraz
def regularExpression(s1, regEx):
    for element in s1.elements:
        for elem in element:
            if (elem.symbol == False):
            	regEx = regEx
            	result = regEx.match(elem.pom)
            	if result: return True
            	else: return False
			
#********************************************************************************************#
# Pomocni funkce pro funkci ProcessInput()
def toEndOfList(s1, pom, trueOrFalse):
	if trueOrFalse == True:
		s1.elements[s1.current].insert(len(s1.elements[s1.current]), Element(pom, True))
	else:
		s1.elements[s1.current].insert(len(s1.elements[s1.current]), Element(pom, False))

#********************************************************************************************#
# Funkce pro spracovani spravnych lexikalnych ci syntaktickych pravidel
def processInput(arguments):
    s1 = Struct()
    pom = ''
    pom1 = True
    charHash = '#'
    charRCbrace = '}'
    charLCbrace = '{'
    charRbrace = ')'
    charLbrace = '('
    charSlash = '\''
    charArrow = '->'
    charComma = ','

    for line in arguments.mka_input:
        for char in line:
            if (s1.pomSymbol == 1) :
                if (char != charSlash):
                    if (s1.apostrof != 1): pom = pom + char
                    else:
                    	toEndOfList(s1, pom, True)
                    	s1.pomSymbol = 0
                    	pom = ''
                elif(char == charSlash):
                	if (s1.apostrof == 1):
                		if ( pom1 == True):
                			pom = pom + charSlash
                			s1.apostrof = 0
                		else:
                			break
                	else: s1.apostrof = 1

            if (s1.pomSymbol == 0):
                if (str.isspace(char) and s1.sucPrvok == False):
                	if ( pom1 == True): continue
                if char == charHash: break

                if (s1.kaDef == True):
                    if (s1.sucPrvok != False):
                        if (char == charRCbrace):
                            s1.sucPrvok = False
                            toEndOfList(s1, pom, False)
                            pom = ''
                        elif (char == charComma):
                            toEndOfList(s1, pom, False)
                            pom = ''
                            if s1.current == 3:
                            	if ( pom1 == True):
                            		s1.current = s1.current + 1
                            		s1.sucPrvok = False
                            	else:
                            		break
                        elif (char == charSlash):
                        	if ( pom1 == True):
                        		s1.apostrof = 0
                        		s1.pomSymbol = 1
                        		toEndOfList(s1, pom, False)
                        		pom = ''
                        	else: break
                        #dalsi znak
                        else: pom = pom + char
                    else:
                        if (char == charComma):
                            s1.current = s1.current + 1
                            if (s1.current == 3 ): s1.sucPrvok = True

                        elif (char == charRbrace):
                        	length = len(s1.elements)
                        	length = length - 1
                        	if (s1.current != length):
                        		sys.exit(60)
                        	else: s1.kaDef = False

                        elif (char == charLCbrace): s1.sucPrvok = True
                        else:
                            sys.exit(60)
                else:
                    if ( char == charLbrace ): s1.kaDef = True
                    elif ( char != charLbrace ):
                    	if ( pom1 == True):
                        	sys.exit(60)
               
        if (s1.pomSymbol == 1 ):
            pom = pom + '\n'

    length = len(s1.elements)
    length = length - 1
    if ( s1.current != length ):
    	sys.exit(60)

    stripStates(pom)

    checkRules(pom, arguments.mka_i)

    return s1.elements
#********************************************************************************************#
# Pomocni funkce, ktera skontroluje pravidla a v pripade chyby vrati code: 60
def checkRules(pom, mka_i):
	s1 = Struct()
	charArrow = '->'
	regEx = re.compile(r"[_A-Za-z][_a-zA-Z0-9]*$")

	pom = len(s1.elements[2])
	if (pom % 3 != 0):
		sys.exit(60)

	for i, elem in enumerate(s1.elements[2]):
		if ( i % 3 == 1 and elem.symbol == False) or (i % 3 == 0 and elem.symbol== True):
			sys.exit(60)

		if (i % 3 == 2 ):
			if (elem.pom[0:2] != charArrow) == True or (elem.symbol) == True :
				sys.exit(60)
			else: 
				pom1 = elem.pom[2:]
				elem.pom = str.lstrip(pom1)

	regularExpression(s1, regEx)
	if regularExpression(s1, regEx) == False:
		sys.exit(60)

	length = len(s1.elements[3])

	if ( length != 1 ):
		sys.exit(60)

	if s1.elements[3][0].symbol:
		sys.exit(60)

	# ak je zadane -i alebo --case-insensitive tak vsetko je malym pismom
	if mka_i == True:
		for element in s1.elements:
			for elem in element:
				elem.pom = elem.pom.lower()

#********************************************************************************************#
# Pomocna funkcia, ktora  napr. aj vymaze stav ktory ma
def stripStates(pom):
	s1 = Struct()

	for element in s1.elements:
		pomElement = []
		for elem in element:
			if ( elem.symbol == False):
				elem.pom = str.strip(elem.pom)
				if not elem.pom:
					pomElement.insert(len(pomElement), elem)
		if pomElement:
			for elem in pomElement:
				element.remove(elem)
		else: continue
#********************************************************************************************#
# Trida sluziaca jak datova struktura
class Struct:
	elements = [[], [], [] , [], []]
	pomSymbol = 0
	kaDef = False
	sucPrvok = False
	current = 0
	apostrof = 0

#********************************************************************************************#
# Trida Element
class Element(object):
	def __init__(self, pom, symbol):
		self.pom = pom
		self.symbol = symbol

	def __cmp__(self, other): cmp(self.pom, other.pom)

	def __eq__(self, other):
		if type(other) is str:
			if( self.symbol == other): return True
			else: return False
		else: return self is other

#********************************************************************************************#
# Trida Symbol
class Symbol(object):
	def __init__(self, name): self.name = name

	def __cmp__(self, other): cmp(self.name, other.name)

	def __eq__(self, other):
		if type(other) is str:
			if( self.name == other): return True
			else: return False
		else: return self is other

	def __lt__(self, other):
		if( self.name < other.name): return True
		else: return False

	def __str__(self): 
		pomChar = "'"
		return pomChar + (str(self.name)).replace(pomChar, "''") + pomChar
#********************************************************************************************#
# Trida Pravidlo
class Pravidlo(object):
    def __init__(self, fromS, toS, pomSymbol):
        self.fromS = fromS
        self.toS = toS
        self.symbol = pomSymbol

    def __cmp__(self, other):
	    if (self.fromS == other.fromS):
	        if (self.symbol == other.symbol):
	            if (self.toS == other.toS): return 0
	            elif (self.toS < other.toS): return -1
	            else: return 1
	        elif (self.symbol < other.symbol): return -1
	        else: return 1
	    elif (self.fromS < other.fromS): return -1
	    else: return 1    

    def __eq__(self, other):
        if type(other) is Pravidlo:
        	if( self.fromS == other.fromS ):
        		if( self.symbol == other.symbol ):
        			if( self.toS == other.toS ): return True
        			else: return False
        		else: return False
        	else: return False
        else: return False

    def __lt__(self, other):
        if (self.fromS == other.fromS):
            if (self.symbol == other.symbol):
            	if( self.toS < other.toS ): return True
            	else: return False
            else:
            	if( self.symbol < other.symbol): return True
            	else: return False
        else:
        	if ( self.fromS < other.fromS ): return True
        	else: return False
       
    def __str__(self):
        return str(self.fromS) + " " + str(self.symbol) + " -> " + str(self.toS) 
#********************************************************************************************#
# Trida Stav
class Stav(object):
	def __init__(self, name): self.name = name

	def __cmp__(self, other): cmp(self.name, other.name)

	def __eq__(self, other):
		if type(other) is str:
			if( self.name == other): return True
			else: return False
		else: return self is other

	def __lt__(self, other):
		if( self.name < other.name): return True
		else: return False

	def __str__(self): return self.name
#********************************************************************************************#
# Trida StavG
class StavG(object):
    def __init__(self, stav):
        self.stav = []
        for state in stav: self.stav.insert(len(self.stav), state)
            
    def __eq__(self, other): return self is other
            
    def __len__(self):
    	length = len(self.stav)
    	return length
    
    def __iter__(self):
    	pom = []
    	for state in self.stav:
    		if pom.insert(len(pom), state): return state
    		else: yield state
            
    def __hash__(self):
    	string = str(self)
    	return hash(string)
    
    def __str__(self):
        string = ''
        for state in self.stav[0:-1]:
            string = string + str(state) + '_'

        string = string + str(self.stav[-1])
        return string
#********************************************************************************************#
main()