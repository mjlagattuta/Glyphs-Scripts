#MenuTitle: Kerns to Kern Classes
# -*- coding: utf-8 -*-

__doc__="""
Uses existing kernKeys and a set tolerance level to merge flat kerning into classes

TODO: Address the i and j use of dotless i and dotless j so that they do not lose kerning as currently happens******


MAYBE: Make the script compatible with kerning that has some class-based kerning already. To do this I will need to modify the way the script uses the kerning dictionary
Perhaps I can check the rightKerningKey on the left glyph and the leftKerningKey on the right glyph and use regex to see if there is a class for it or not, then handle those results acccordingly. The expected behavior would be for 4 case:
(1) Glyph + Glyph
Should reference a core pair and:
If reference exists then create the class kern if there is none, else use existing
If no reference exists leave it alone

(2) Class + Glyph
Should reference a core pair and do the same as (1)


(3) Glyph + Class
should reference a core pair asnd do the same as (1)


(4) Class + Class
I believe this to be outside the scope of the script.
"""

import GlyphsApp
import time
import sys
import re

start = time.time()
count = 0

font = Glyphs.font

################################################
###############   Set Tolernce   ###############
tolerance = 5.0
###############   Set Tolernce   ###############
################################################

# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
# for glyph in font.glyphs:
	# glyphRef = re.sub( ',.*', '', re.sub( '\(\s*', '', re.sub( '\n', '', str(Glyphs.ligatureComponents(glyph.name)))))
	# if glyphRef == 'None' and glyph.category != 'Mark':
		# print glyph.name, glyph.category, glyph.subCategory, glyphRef

# This may not be needed --- Manual lookups not covered by Glyphs.ligatureComponents()
# manualComponentDict_L = {
# 	'Alpha':'A',
# 	'B':'B'
# 	}
# manualComponentDict_R = {

# 	}
	
# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
# Set up dictionary to map glyph IDs to glyph names probably not needed
# glyphIdDict = {}
# for glyph in font.glyphs:
# 	glyphIdDict.update({glyph.id:glyph.name})
		
# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
# Defs (can condense left and right into one method and take an extra parameter to determine the difference)
def leftNew(name):
	glyphRef = re.sub( ',.*', '', re.sub( '\(\s*', '', re.sub( '\n', '', str(Glyphs.ligatureComponents(name)))))

	# if referenced glyph has a class, use that
	if glyphRef != 'None':
		newName = font.glyphs[glyphRef].rightKerningKey
	# if referenced glyph has a class, use that, and if there is no class then the glyphd name is used instead ensuring it stays an exception
	else:
		newName = font.glyphs[name].rightKerningKey
	return newName
	
def rightNew(name):
	glyphRef = re.sub( ',.*', '', re.sub( '\(\s*', '', re.sub( '\n', '', str(Glyphs.ligatureComponents(name)))))

	# if referenced glyph has a class, use that
	if glyphRef != 'None':
		newName = font.glyphs[glyphRef].leftKerningKey
		##### set the glyphs kerning class to match if it not already so
	# if referenced glyph has a class, use that, and if there is no class then the glyphd name is used instead ensuring it stays an exception
	else:
		newName = font.glyphs[name].leftKerningKey
	return newName
	
def correctKern(leftGlyph, rightGlyph, kernValue):
	# this is not currently used. Was trying to resolve exceptions with i accents but those may be best resolved as manual exceptions after the fact
	narrow = False
	glyphRefLeft = re.sub( ',.*', '', re.sub( '\(\s*', '', re.sub( '\n', '', str(Glyphs.ligatureComponents(leftGlyph)))))
	glyphRefRight = re.sub( ',.*', '', re.sub( '\(\s*', '', re.sub( '\n', '', str(Glyphs.ligatureComponents(rightGlyph)))))
	if glyphRefLeft != 'None' and glyphRefLeft != "idotless" and glyphRefLeft != "jdotless":
		leftRefName = glyphRefLeft
	elif glyphRefLeft == "idotless":
		leftRefName = "i"
		narrow = True
	elif glyphRefLeft == "jdotless":
		leftRefName = "j"
		narrow = True
	else:
		try:
			leftRefName = font.glyphs[leftGlyph].layers[0].components[0].name
		except:
			leftRefName = leftGlyph
	
	if glyphRefRight != 'None' and glyphRefRight != "idotless" and glyphRefRight != "jdotless":
		rightRefName = glyphRefRight
	elif glyphRefRight == "idotless":
		rightRefName = "i"
		narrow = True
	elif glyphRefRight == "jdotless":
		rightRefName = "j"
		narrow = True
	else:
		try:
			rightRefName = font.glyphs[rightGlyph].layers[0].components[0].name
		except:
			rightRefName = rightGlyph
		
	if leftRefName == leftGlyph and rightRefName == rightGlyph:
		addKern = True
	else:
		addKern = False
		
	if font.kerningForPair(font.selectedFontMaster.id, font.glyphs[leftRefName].rightKerningKey, font.glyphs[rightRefName].leftKerningKey) < 10000:
		refKernValue = font.kerningForPair(font.selectedFontMaster.id, font.glyphs[leftRefName].rightKerningKey, font.glyphs[rightRefName].leftKerningKey)
	else:
		refKernValue = font.kerningForPair(font.selectedFontMaster.id, leftRefName, rightRefName)
	
	# if there is a reference kern value
	if refKernValue < 10000:
		# if this kern is 
		if kernValue >= (refKernValue - tolerance) and kernValue <= (refKernValue + tolerance):
			newKernValue = refKernValue
			removeKern = True
		elif addKern == False:# and narrow == False:
			newKernValue = refKernValue
			removeKern = True
		else:
			newKernValue = kernValue
			removeKern = False
	else:
		if kernValue >= (0 - tolerance) and kernValue <= (0 + tolerance):
			newKernValue = refKernValue
			removeKern = True
		elif addKern == False:# and narrow == False:
			newKernValue = refKernValue
			removeKern = True
		else:
			newKernValue = kernValue
			removeKern = False
	return newKernValue, removeKern, addKern

def leftExists(left):
	try:
		check = font.kerning[font.selectedFontMaster.id][left]
		return True
	except:
		return False


def rightExists(left, right):
	try:
		check = font.kerning[font.selectedFontMaster.id][left][right]
		return True
	except:
		return False
		
# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
# Main
# Run through all glyphs
for left in font.glyphs:
	# If the left has a kern lookup, proceed, otherwise skip
	if leftExists(left.id) == True:
		# Run through all glyphs
		for right in font.glyphs:
			# If there is a kerning pair for left + right proceed, otherwise skip
			if rightExists(left.id, right.id):
				kernValue = font.kerningForPair(font.selectedFontMaster.id, left.name, right.name)
				# check if there is a kern or a kern exception
				if kernValue < 10000:
					# Get class of left glyph
					leftUpdated = leftNew(left.name)
					# Get class of right glyph
					rightUpdated = rightNew(right.name)
					# Gets correct kern value
					kernValueNew = correctKern(left.name, right.name, kernValue)[0]

					# print left.name, right.name, kernValue, "    ", leftUpdated, rightUpdated, kernValueNew

					if correctKern(left.name, right.name, kernValue)[1] == True:
						font.removeKerningForPair(font.selectedFontMaster.id, left.name, right.name)
						if correctKern(left.name, right.name, kernValue)[2] == True:
						# if font.kerningForPair(font.selectedFontMaster.id, leftUpdated, rightUpdated) > 10000:
							font.setKerningForPair(font.selectedFontMaster.id, leftUpdated, rightUpdated, kernValueNew)
							count = count + 1
							print "Moved '%s %s' pair into new pair '%s %s'" % (left.name, right.name, leftUpdated, rightUpdated), time.time() - start, count
						else:
							count = count + 1
							print "Moved '%s %s' pair into existing pair '%s %s'" % (left.name, right.name, leftUpdated, rightUpdated), time.time() - start, count
					else:
						print  "Did not move '%s %s' pair" % (left.name, right.name), time.time() - start, count
			else:
				pass
	else:
		pass



# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
# —————————————————————————————————— Macro for testing script on a pair by pair basis ——————————————————————————————————————
# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

# font = Glyphs.font
# import re

# # Tester for kern condenser script

# def correctKern(leftGlyph, rightGlyph, kernValue):
# 	narrow = False
# 	glyphRefLeft = re.sub( ',.*', '', re.sub( '\(\s*', '', re.sub( '\n', '', str(Glyphs.ligatureComponents(leftGlyph)))))
# 	glyphRefRight = re.sub( ',.*', '', re.sub( '\(\s*', '', re.sub( '\n', '', str(Glyphs.ligatureComponents(rightGlyph)))))
# 	if glyphRefLeft != 'None' and glyphRefLeft != "idotless" and glyphRefLeft != "jdotless":
# 		leftRefName = glyphRefLeft
# 	elif glyphRefLeft == "idotless":
# 		leftRefName = "i"
# 		narrow = True
# 	elif glyphRefLeft == "jdotless":
# 		leftRefName = "j"
# 		narrow = True
# 	else:
# 		try:
# 			leftRefName = font.glyphs[leftGlyph].layers[0].components[0].name
# 		except:
# 			leftRefName = leftGlyph
	
# 	if glyphRefRight != 'None' and glyphRefRight != "idotless" and glyphRefRight != "jdotless":
# 		rightRefName = glyphRefRight
# 	elif glyphRefRight == "idotless":
# 		rightRefName = "i"
# 		narrow = True
# 	elif glyphRefRight == "jdotless":
# 		rightRefName = "j"
# 		narrow = True
# 	else:
# 		try:
# 			rightRefName = font.glyphs[rightGlyph].layers[0].components[0].name
# 		except:
# 			rightRefName = rightGlyph
		
# 	if leftRefName == leftGlyph and rightRefName == rightGlyph:
# 		addKern = True
# 	else:
# 		addKern = False
		
# 	if font.kerningForPair(font.selectedFontMaster.id, font.glyphs[leftRefName].rightKerningKey, font.glyphs[rightRefName].leftKerningKey) < 10000:
# 		refKernValue = font.kerningForPair(font.selectedFontMaster.id, font.glyphs[leftRefName].rightKerningKey, font.glyphs[rightRefName].leftKerningKey)
# 	else:
# 		refKernValue = font.kerningForPair(font.selectedFontMaster.id, leftRefName, rightRefName)
	
# 	# if there is a reference kern value
# 	if refKernValue < 10000:
# 		# if this kern is 
# 		if kernValue >= (refKernValue - tolerance) and kernValue <= (refKernValue + tolerance):
# 			newKernValue = refKernValue
# 			removeKern = True
# 		elif addKern == False:# and narrow == False:
# 			newKernValue = refKernValue
# 			removeKern = True
# 		else:
# 			newKernValue = kernValue
# 			removeKern = False
# 	else:
# 		if kernValue >= (0 - tolerance) and kernValue <= (0 + tolerance):
# 			newKernValue = refKernValue
# 			removeKern = True
# 		elif addKern == False:# and narrow == False:
# 			newKernValue = refKernValue
# 			removeKern = True
# 		else:
# 			newKernValue = kernValue
# 			removeKern = False
		
# 	print leftRefName, rightRefName, refKernValue
# 	return newKernValue, removeKern, addKern
	
# left = "r"
# right = "i"
	
# kernValue = font.kerningForPair(font.selectedFontMaster.id, left, right)

# print left, right, kernValue	
# print correctKern(left, right, kernValue)
