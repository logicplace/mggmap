#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
import sys
import codecs
import re
from xml.dom.minidom import parse
from mimetypes import guess_type

def Exists(dPaths):
	for x in dPaths:
		if dPaths[x] is None:
			print 'ERROR: %s path does not exist.' % x
			return False
		elif not os.path.exists(dPaths[x]):
			print 'ERROR: %s path "%s" does not exist.' % (x,dPaths[x])
			return False
		#endif
	#endfor
	return True
#enddef

def main():
	lPaths = [
		"/usr/share/gnome-games/mahjongg/games/",
		"/usr/local/share/gnome-games/mahjongg/games/"
	]
	sPath = None
	for x in lPaths:
		if os.path.exists(x):
			sPath = x
			break
		#endif
	#endfor
	
	lScorePaths = [
		"/usr/local/var/games/",
		"/var/games/"
	]
	sScorePath = None
	for x in lScorePaths:
		if os.path.exists(x):
			sScorePath = x
			break
		#endif
	#endfor
	
	iArgc = len(sys.argv)
	if iArgc > 1 and re.match(r'[\-/]([?h]|-?help)',sys.argv[1]):
		print("Mahjongg Map Tool by Wa (logicplace.com)\n" +
			("Usage: %s [options] [-c[i] File]\n" % sys.argv[0]) +
			("Usage: %s [options] [-i File]\n" % sys.argv[0]) +
			("       %s [options] [-v [ScoreName [ScoreName ...]]]\n" % sys.argv[0]) +
			"Options:\n"+
			" -f  Set the location of the map folder. Default searches known locations.\n"
			" -s  Set the location of the score folder. Default searches known locations.\n"
			"Commands:\n"+
			" -c  Compile a file into a map. See ReadMe for specifics.\n"+
			" -v  Validate map files. If no ScoreNames are given, it validates all of them.\n"
			" -i  Installs the given map file."
		)
		return
	#endif
	
	iI = 1
	while iI < iArgc:
		sI = sys.argv[iI]
		# Options
		if sI == "-f":
			# Set maps path
			try:
				if sys.argv[iI+1][0] != '-':
					iI += 1
					sPath = sys.argv[iI]
				#endif
			except: pass
		elif sI == "-s":
			# Set score path
			try:
				if sys.argv[iI+1][0] != '-':
					iI += 1
					sScorePath = sys.argv[iI]
				#endif
			except: pass
		# Commands
		elif sI in ["-c","-ic","-ci"]:
			if not Exists({"Map":sPath,"Score":sScorePath}): return False
			# Compile file
			if len(sys.argv) > iI+1:
				sMapFile = Compile(sys.argv[iI+1])
				if 'i' in sI and sMapFile: Install(sPath,sScorePath,sMapFile)
			else:
				print("Please provide the file to compile.")
				return
			#endif
		elif sI == "-v":
			if not Exists({"Map":sPath,"Score":sScorePath}): return False
			# Validate maps
			lMapNames = sys.argv[iI+1:] if len(sys.argv) > iI+1 else []
			ValidateMaps(sPath,lMapNames)
			return
		elif sI == "-i":
			if not Exists({"Map":sPath,"Score":sScorePath}): return False
			# Install map
			Install(sPath,sScorePath,sys.argv[iI+1])
		#endif
		iI += 1
	#endwhile
#enddef

def Install(sPath,sScorePath,sFilename):
	global reFInfo
	moX = reFInfo.match(sFilename)
	try:
		#sPath = moX.group(1)
		sName = moX.group(4)
		sExt = moX.group(5)
		hIn,hOut = open(sFilename,"rb"), open(os.path.join(sPath,"%s.%s" % (sName,sExt)),"wb")
		hOut.write(hIn.read())
		hIn.close()
		hOut.close()
		sScoreName = os.path.join(sScorePath,"mahjongg.%s.scores" % sName)
		open(sScoreName,"w").close()
		os.chmod(sScoreName,0666)
	except:
		print("Failed installation. (Need to sudo or something?)")
	#endif
#enddef

def LayerRange(e,iSt,iEd):
	if e.hasAttribute("z"):
		try:
			iZ = int(e.getAttribute("z"))
			iSt = iZ if iSt is None else min(iSt,iZ)
			iEd = iZ if iEd is None else  max(iEd,iZ)
		except: pass
	#endif
	return (iSt,iEd)
#enddef

def ValidateMaps(sPath,lMapNames):
	for sDirpath,lDirnames,lFilenames in os.walk(sPath):
		for sI in lFilenames:
			try:
				hDom = parse(os.path.join(sDirpath,sI))
				lMaps = hDom.getElementsByTagName("map")
				for eMap in lMaps:
					if not eMap.hasAttribute("scorename"):
						print("(%s) Error: Map with no scorename." % sI)
						continue
					#endif
					sScoreName = eMap.getAttribute("scorename")
					if not lMapNames or sScoreName in lMapNames:
						if not eMap.hasAttribute("name"):
							print("(%s) Error: Map \"%s\" has no name." % (sI,sScoreName))
						#endif
						lLayers  = eMap.getElementsByTagName("layer")
						lTiles   = eMap.getElementsByTagName("tile")
						lRows    = eMap.getElementsByTagName("row")
						lColumns = eMap.getElementsByTagName("column")
						lBlocks  = eMap.getElementsByTagName("block")
					
						# Count layers
						iFirstLayer, iLastLayer = None,None
						iI = 0
						for eLayer in lLayers:
							if eLayer.hasAttribute("z"):
								iFirstLayer,iLastLayer = LayerRange(eLayer,iFirstLayer,iLastLayer)
							else:
								print("(%s) Warning: Layer %i has no z attribute" % (sScoreName,iI))
							#endif
							iI += 1
						#endfor
					
						# Count tiles
						iTileTotal = 0
						iI = 0
						for eI in lTiles:
							iFirstLayer,iLastLayer = LayerRange(eI,iFirstLayer,iLastLayer)
							if not eI.hasAttribute("x") or not eI.hasAttribute("y"):
								print("(%s) Error: Tile %i must have both x and y attributes" % (sScoreName,iI))
							else:
								iTileTotal += 1
							#endif
							iI += 1
						#endfor
					
						# Count rows
						iRowTotal = [0,0]
						iI = 0
						for eI in lRows:
							iFirstLayer,iLastLayer = LayerRange(eI,iFirstLayer,iLastLayer)
							if not eI.hasAttribute("y") or not eI.hasAttribute("left") or \
							   not eI.hasAttribute("right"):
								print("(%s) Error: Row %i must have y, left, and right attributes" % (sScoreName,iI))
							else:
								iRowTotal[0] += 1
								iRowTotal[1] += float(eI.getAttribute("right"))-float(eI.getAttribute("left"))+1
							#endif
							iI += 1
						#endfor
					
						# Count columns
						iColumnTotal = [0,0]
						iI = 0
						for eI in lColumns:
							iFirstLayer,iLastLayer = LayerRange(eI,iFirstLayer,iLastLayer)
							if not eI.hasAttribute("x") or not eI.hasAttribute("top") or \
							   not eI.hasAttribute("bottom"):
								print("(%s) Error: Column %i must have x, top, and bottom attributes" % (sScoreName,iI))
							else:
								iColumnTotal[0] += 1
								iColumnTotal[1] += float(eI.getAttribute("bottom"))-float(eI.getAttribute("top"))+1
							#endif
							iI += 1
						#endfor
					
						# Count blocks
						iBlockTotal = [0,0]
						iI = 0
						for eI in lBlocks:
							iFirstLayer,iLastLayer = LayerRange(eI,iFirstLayer,iLastLayer)
							if not eI.hasAttribute("left") or not eI.hasAttribute("right") or \
							   not eI.hasAttribute("top") or not eI.hasAttribute("bottom"):
								print("(%s) Error: Block %i must have left, right, top, and bottom attributes" % (sScoreName,iI))
							else:
								iBlockTotal[0] += 1
								iBlockTotal[1] += (float(eI.getAttribute("bottom"))-
								float(eI.getAttribute("top"))+1)*(float(eI.getAttribute("right"))-
								float(eI.getAttribute("left"))+1)
							#endif
							iI += 1
						#endfor
					
						iTotal = iTileTotal + iRowTotal[1] + iColumnTotal[1] + iBlockTotal[1]
					
						# Print stats
						print(("(%s) Statistics:\n" % sScoreName)+
							(" * %i layers\n" % (iLastLayer-iFirstLayer+1 if iLastLayer else 1))+
							(" * %i lone tiles\n" % iTileTotal)+
							(" * %i tiles in %i rows\n" % (iRowTotal[1],iRowTotal[0]))+
							(" * %i tiles in %i columns\n" % (iColumnTotal[1],iColumnTotal[0]))+
							(" * %i tiles in %i blocks\n" % (iBlockTotal[1],iBlockTotal[0]))+
							(" * For a total of %i tiles" % iTotal)
						)
						if iTotal != 144: print("(%s) Warning: Requires a total of 144 tiles." % sScoreName)
					#endif
				#endfor
			except:
				print("(%s) Parsing error or something" % sI)
			#endtry
		#endfor
	#endfor
#enddef

reFInfo = re.compile(r'(.*/)?(?:\[([^\]]*)\](?:[ _]*|[\-.]?))?(?:(.+)\.)?([a-zA-Z][a-zA-Z0-9_]*)\.([A-Za-z0-9]+)$')
def Compile(sFilename):
	global reFInfo
	# Get file info from filename
	# 2: Author name
	# 3: Map name
	# 4: Score name
	moX = reFInfo.match(sFilename)
	if moX:
		dInfo = {
			"path": moX.group(1) or "",
			"author": moX.group(2) or "",
			"map": (moX.group(3) or "").replace("_"," "),
			"score": moX.group(4)
		}

		sType,sEncoding = guess_type(sFilename)
		sMain = sType.split("/")[0] if type(sType) is str else "text"
		if sMain == "image":
			return CompileImage(sFilename,dInfo)
		elif sMain == "text":
			return CompileText(sFilename,dInfo)
		else:
			print("Cannot compile %s files" % sType)
		#endif
	else:
		print("Filename is too strange")
	#endif
	return None
#enddef

def CompileImage(sFilename,dInfo):
	print("Image compiling coming soon~")
#enddef

def CompileText(sFilename,dInfo):
	# Open and read file
	hFile = codecs.open(sFilename,"r","utf8")
	lLines = hFile.readlines()
	hFile.close()
	
	# Parse file
	sComments = u""
	lMap = []
	bBegun = False
	
	for sLine in lLines:
		sLine = unicode(sLine)
		iHash = sLine.find(u"#")
		if iHash != -1:
			# Comment
			sComment = sLine[iHash+1:].strip()
			sLine = sLine[:iHash]
			if iHash == 0:
				# Check for special comments
				if sComment[:4] == u"Map:":
					sMap = sComment[4:].strip()
					if dInfo["map"] and dInfo["map"] != sMap:
						print("Map name mismatch (filename vs. internal). Using internal name.")
					#endif
					dInfo["map"] = sMap
				elif sComment[:7] == u"Author:":
					sAuthor = sComment[7:].strip()
					if dInfo["author"] and dInfo["author"] != sAuthor:
						print("Author name mismatch (filename vs. internal). Using internal name.")
					#endif
					dInfo["author"] = sAuthor
				elif sComment == u"*": break
				# Otherwise just append it to the list of regular comments
				else: sComments += sComment+"\n"
			#endif
		#endif
		sLine = sLine.strip()
		if sLine: bBegun = True
		# Data
		if bBegun:
			lMap.append(sLine)
		#endif
	#endfor
	
	mMap = Map(lMap)
	if mMap.ok:
		mMap.Block()
		
		sOut = os.path.join(dInfo["path"],"%s.map" % dInfo["score"])
		hOut = codecs.open(sOut,"w")
		hOut.write("<!-- %s by %s -->\n<!-- Map compiled with Mahjongg Map Tool -->\n" % (dInfo["map"],dInfo["author"] or "Unknown"))
		if sComments: hOut.write("<!--\n%s-->\n" % sComments)
	
		mMap.WriteOut(hOut,dInfo)
	
		hOut.close()
		return sOut
	#endif
	return sFilename
#enddef

def b2l(s):
	lRet = []
	for sI in s: lRet.append(sI == 't')
	return lRet
#enddef

class Map:
	num = [ # Numbers
		u' 0０🀃🀀🀂🀁🀄🀅🀆🀢🀣🀤🀥🀦🀧🀨🀩🀪🀫',
		u'1１🀇🀐🀙▁',
		u'2２🀈🀑🀚▂',
		u'3３🀉🀒🀛▃',
		u'4４🀊🀓🀜▄',
		u'5５🀋🀔🀝▅',
		u'6６🀌🀕🀞▆',
		u'7７🀍🀖🀟▇',
		u'8８🀎🀗🀠█',
		u'9９🀏🀘🀡'
	]
	b2d = u' ░▒▓█' # Box to Density
	g2l = { # grams to layers
		# Monograms
		u' ':[False],u'⚋':[False],u'⚊':[True],'_':[True],
		# Digrams
		u'⚏':b2l('ff'),u'⚎':b2l('ft'),u'⚍':b2l('tf'),u'⚌':b2l('tt'),
		# Trigrams
		u'☷':b2l('fff'),u'☶':b2l('fft'),u'☵':b2l('ftf'),u'☳':b2l('tff'),
		u'☱':b2l('ttf'),u'☲':b2l('tft'),u'☴':b2l('ftt'),u'☰':b2l('ttt'),
		# Hexagrams
		u'䷀':b2l('tttttt'),u'䷁':b2l('ffffff'),u'䷂':b2l('tffftf'),
		u'䷃':b2l('ftffft'),u'䷄':b2l('tttftf'),u'䷅':b2l('ftfttt'),
		u'䷆':b2l('ftffff'),u'䷇':b2l('fffftf'),u'䷈':b2l('tttftt'),
		u'䷉':b2l('ttfttt'),u'䷊':b2l('tttfff'),u'䷋':b2l('fffttt'),
		u'䷌':b2l('tftttt'),u'䷍':b2l('ttttft'),u'䷎':b2l('fftfff'),
		u'䷏':b2l('ffftff'),u'䷐':b2l('tffttf'),u'䷑':b2l('fttfft'),
		u'䷒':b2l('ttffff'),u'䷓':b2l('fffftt'),u'䷔':b2l('tfftft'),
		u'䷕':b2l('tftfft'),u'䷖':b2l('ffffft'),u'䷗':b2l('tfffff'),
		u'䷘':b2l('tffttt'),u'䷙':b2l('tttfft'),u'䷚':b2l('tfffft'),
		u'䷛':b2l('fttttf'),u'䷜':b2l('ftfftf'),u'䷝':b2l('tfttft'),
		u'䷞':b2l('fftttf'),u'䷟':b2l('ftttff'),u'䷠':b2l('fftttt'),
		u'䷡':b2l('ttttff'),u'䷢':b2l('ffftft'),u'䷣':b2l('tftfff'),
		u'䷤':b2l('tftftt'),u'䷥':b2l('ttftft'),u'䷦':b2l('fftftf'),
		u'䷧':b2l('ftftff'),u'䷨':b2l('ttffft'),u'䷩':b2l('tffftt'),
		u'䷪':b2l('tttttf'),u'䷫':b2l('fttttt'),u'䷬':b2l('fffttf'),
		u'䷭':b2l('fttfff'),u'䷮':b2l('ftfttf'),u'䷯':b2l('fttftf'),
		u'䷰':b2l('tftttf'),u'䷱':b2l('ftttft'),u'䷲':b2l('tfftff'),
		u'䷳':b2l('fftfft'),u'䷴':b2l('fftftt'),u'䷵':b2l('ttftff'),
		u'䷶':b2l('tfttff'),u'䷷':b2l('ffttft'),u'䷸':b2l('fttftt'),
		u'䷹':b2l('ttfttf'),u'䷺':b2l('ftfftt'),u'䷻':b2l('ttfftf'),
		u'䷼':b2l('ttfftt'),u'䷽':b2l('ffttff'),u'䷾':b2l('tftftf'),
		u'䷿':b2l('ftftft')
	}
	lines = {
		'#': u'0123456789', # Numbers (for marking depth)
		'c1': u'┌┍┎┏╒╓╔╭','c2': u'┐┑┒┓╕╖╗╮',
		'c3': u'└┕┖┗╘╙╚╰','c4': u'┘┙┚┛╛╜╝╯',
		'o1': u'┬┭┮┯┰┱┲┳╤╥╦',
		'o2': u'├┝┞┟┠┡┢┣╞╟╠','o3': u'┤┥┦┧┨┩┪┫╡╢╣',
		'o4': u'┴┵┶┷┸┹┺┻╧╨╩',
		'o5': u'┼┽┾┿╀╁╂╃╄╅╆╇╈╉╊╋╪╫╬',
		'v': u'│┃┆┇┊┋╎╏║╽╿',
		'h': u'─━┄┅┈┉╌╍═╼╾'
	}
	blk = u' ▄▝▘▗▖▚▞▟▙▜▛█\\' # Valid block chars

	def __init__(self,lMap):
		self.map = []
		self.blocks = []
		self.width = self.height = 0
		
		iWidth = 0;
		# Create valid char lists for each type:
		vnum = u"".join(self.num)
		vgrm = u"".join(self.g2l)
		vlns = u""
		for sI in self.g2l: vgrm += sI
		for sI in self.lines: vlns += self.lines[sI]
		lValid = [vnum,self.b2d,vgrm,vlns,self.blk]
		
		# Validate that all characters in the map are in one set
		for sI in lMap:
			iWidth = max(iWidth,len(sI))
			for sC in sI:
				iI = 0
				while iI < len(lValid):
					if unicode(sC) not in unicode(lValid[iI]): lValid.pop(iI)
					else: iI += 1
				#endwhile
			#endfor
		#endfor
		
		if len(lValid) >= 1:
			# Parse into map
			for x in lValid:
				if x == vnum: # Number as depth form
					for iY in range(len(lMap)):
						sLine = lMap[iY]
						sLine += " " * (iWidth - len(sI))
						for iX in range(iWidth):
							sC = sLine[iX]
							if   sC in self.num[1]: self.__SetStack(iX,iY,[True])
							elif sC in self.num[2]: self.__SetStack(iX,iY,[True]*2)
							elif sC in self.num[3]: self.__SetStack(iX,iY,[True]*3)
							elif sC in self.num[4]: self.__SetStack(iX,iY,[True]*4)
							elif sC in self.num[5]: self.__SetStack(iX,iY,[True]*5)
							elif sC in self.num[6]: self.__SetStack(iX,iY,[True]*6)
							elif sC in self.num[7]: self.__SetStack(iX,iY,[True]*7)
							elif sC in self.num[8]: self.__SetStack(iX,iY,[True]*8)
							elif sC in self.num[9]: self.__SetStack(iX,iY,[True]*9)
						#endfor
					#endfor
					break
				elif x == vgrm: # *grams for fine depth (up to 6)
					for iY in range(len(lMap)):
						sLine = lMap[iY]
						sLine += " " * (iWidth - len(sI))
						for iX in range(iWidth):
							self.__SetStack(iX,iY,self.g2l[sLine[iX]])
						#endfor
					#endfor
					break
				# TODO: Other formats
				#endif
			#endfor
			self.__Normalize()
			
			self.ok = True
		else:
			print("Not sure how to read this..")
			self.ok = False
		#endif
	#enddef
	
	def __SetStack(self,iX,iY,lStack):
		iLen = len(lStack)
		# Make sure all requested depths exist
		for iI in range(iLen-len(self.map)): self.map.append([])
		self.width = max(self.width,iX+1)
		self.height = max(self.height,iY+1)
		for iZ in range(iLen):
			# Make sure all requested columns exist
			for iI in range(iY-(len(self.map[iZ])-1)): self.map[iZ].append([])
			# Make sure all requested rows exist
			self.map[iZ][iY] += [False] * max(0,iX-(len(self.map[iZ][iY])-1))
			# Set cell
			self.map[iZ][iY][iX] = lStack[iZ]
		#endfor
	#endif
	
	def __Normalize(self):
		for lZ in self.map:
			for iI in range(self.height-(len(lZ)-1)): lZ.append([])
			for lY in lZ: lY += [False] * max(0,self.width-(len(lY)-1))
		#endfor
	#enddef
	
	def Block(self):
		self.blocks = []
		for lLayer in self.map:
			lBlocks = []
			lUnused = []
			for iI in range(len(lLayer)): lUnused.append([True] * self.width)
			for iY in range(len(lLayer)):
				for iX in range(self.width):
					if lLayer[iY][iX] and lUnused[iY][iX]:
						# TODO: Search block spanny-ness
						# For now just do rows
						iTX = iX
						lUnused[iY][iTX] = False
						while iTX < self.width and lLayer[iY][iTX+1] and lUnused[iY][iTX+1]:
							iTX += 1
							lUnused[iY][iTX] = False
						#endwhile
						lBlocks.append([iX,iY,iTX,iY])
					#endif
				#endfor
			#endfor
			self.blocks.append(lBlocks)
		#endfor
	#enddef
	
	def WriteOut(self,hOut,dInfo):
		hOut.write('<mahjongg>\n\t<map name="%s" scorename="%s">\n' % (dInfo["map"],dInfo["score"]))
		
		if self.blocks:
			for iZ in range(len(self.blocks)):
				hOut.write('\t\t<layer z="%i">\n' % iZ)
				for lB in self.blocks[iZ]:
					if lB[2] != lB[0] and lB[3] != lB[1]:
						hOut.write('\t\t\t<block left="%s" top="%s" right="%s" bottom="%s"/>\n' % tuple(lB))
					elif lB[2] == lB[0] and lB[3] != lB[1]:
						hOut.write('\t\t\t<column x="%s" top="%s" bottom="%s"/>\n' % (lB[0],lB[1],lB[3]))
					elif lB[2] != lB[0] and lB[3] == lB[1]:
						hOut.write('\t\t\t<row y="%s" left="%s" right="%s"/>\n' % (lB[1],lB[0],lB[2]))
					elif lB[2] == lB[0] and lB[3] == lB[1]:
						hOut.write('\t\t\t<tile x="%s" y="%s"/>\n' % (lB[0],lB[1]))
					#endif
				#endfor
				hOut.write('\t\t</layer>\n')
			#endfor
		else:
			for iZ in range(len(self.map)):
				hOut.write('\t\t<layer z="%i">\n' % iZ)
				for iY in range(len(self.map[iZ])):
					for iX in range(self.width):
						if self.map[iZ][iY][iX]:
							hOut.write('\t\t\t<tile x="%s" y="%s"/>\n' % (iX,iY))
						#endif
					#endfor
				#endfor
				hOut.write('\t\t</layer>\n')
			#endfor
		#endif
		hOut.write('\t</map>\n</mahjongg>')
		# TODO: Write out how it was parsed
	#enddef
	
#endclass

main()
