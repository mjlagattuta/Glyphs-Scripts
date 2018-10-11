font = Glyphs.font
import re
import objc

# Sets the current glyph based on the layer being edited... font.selectLayers[0].parent = GSGlyph object for the current glyph
currentGlyphName = font.selectedLayers[0].parent.name

#################
# Set Variables #

# If set to false, the files master locations and instance values will all be changed
nonDestructive = True

# Width coordinates
wdthMax = 1000.0
wdthMin = 0.0

# Bold Extended and Bold Condensed original values
wghtWideMax = 232.0
wghtCondMax = 193.0

# Light Extended and Light Condensed original values
wghtWideMin = 34.0
wghtCondMin = 34.0

# Set these if using a 6 master setup with equal middle masters
wghtMid = 0.0
wghtCondMidNew = wghtCondMin + ((wghtMid - wghtCondMin) / (wghtCondMax - wghtCondMin)) * (wghtWideMax - wghtCondMin)

# Light Extended master index + Condensed Bold master index (starts from 0)
wideLightIndex = 2
condBoldIndex = 1
conMidIndex = 1

# Set Variables #
#################

for instance in font.instances:
	if instance.active == True:
		# Find max weight at this width
		wghtIntrMax = round(wghtCondMax + ( ((instance.widthValue - wdthMin) / (wdthMax - wdthMin)) * (wghtWideMax - wghtCondMax) ))
		
		# Find min width at this width
		wghtIntrMin = round(wghtCondMin + ( ((instance.widthValue - wdthMin) / (wdthMax - wdthMin)) * (wghtWideMin - wghtCondMin) ))
		
		# Original weight
		oldWght = instance.weightValue
		
		newWght = round( wghtCondMin + ( ((instance.weightValue - wghtIntrMin) / (wghtIntrMax - wghtIntrMin)) * (wghtWideMax - wghtCondMin)))
		# Compare values to ensure that weights were not being extrapolated beyond wghtIntrMax or wghtInterMin
		print oldWght, wghtIntrMin, wghtIntrMax, newWght
			
		# Adds 'before and after' layers to the first master layer for proofing to see if designspace was properly scaled
		if nonDestructive == True:
			
			# Store layer in a variable for the original outline
			origOutline = instance.interpolatedFontProxy.glyphs[currentGlyphName].layers[0]
			
			# Modify master locations for rectangualar desgin-space
			font.masters[wideLightIndex].setWeightValue_(wghtCondMin)
			font.masters[condBoldIndex].setWeightValue_(wghtWideMax)
			if len(font.masters) == 6:
				font.masters[condMidIndex].setWeightValue_(wghtCondMidNew)
			
			# Create a new instance
			testInstance = instance.copy()
			# Set to the newly calculated weight
			testInstance.weightValue = newWght
			
			# Store new layer
			newOutline = testInstance.interpolatedFontProxy.glyphs[currentGlyphName].layers[0]
			
			# Reset master locations
			font.masters[wideLightIndex].setWeightValue_(wghtWideMin)
			font.masters[condBoldIndex].setWeightValue_(wghtCondMax)
			if len(font.masters) == 6:
				font.masters[condMidIndex].setWeightValue_(wghtMid)
			
			# Create a new layer in the active glyph for the old outline named accordingly
			newLayerOld = font.glyphs[currentGlyphName].layers[0].copy()
			newLayerOld.name = "Old " + str(oldWght) + "_" + re.sub("\d* ", "", instance.name)
			newLayerOld.paths = []
			
			# Create a new layer in the active glyph for the new outline named accordingly
			newLayerNew = font.glyphs[currentGlyphName].layers[0].copy()
			newLayerNew.name = "New " + str(newWght) + "_" + re.sub("\d* ", "", instance.name)
			newLayerNew.paths = []
			
			# Add paths to each respective layer
			for i in range(len(origOutline.paths)):
				newLayerOld.paths.append(origOutline.paths[i])
				newLayerNew.paths.append(newOutline.paths[i])
				
			newLayerOld.roundCoordinates()
			newLayerNew.roundCoordinates()
				
			# Append layers
			font.glyphs[currentGlyphName].layers.append(newLayerOld)
			font.glyphs[currentGlyphName].layers.append(newLayerNew)

		# Actually modifies the values of the file, renames instances and makes master locations rectangular
		else:
			font.masters[wideLightIndex].setWeightValue_(wghtCondMin)
			font.masters[condBoldIndex].setWeightValue_(wghtWideMax)

			instance.weightValue = newWght

			instance.name = re.sub("\d* ", "%d" % int(newWght), instance.name)
			
if nonDestructive == False:		
	print "\nScaled file to a rectangular designspace"