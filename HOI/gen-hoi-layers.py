font = Glyphs.font
import re

# Set up a cubic HOI layer
# Will need to convert this to work with multiple paths
			
currentGlyph = font.selectedLayers[0].parent.name
		
def addNode(layerId, idHOI, setting):
	i = 0
	for path in font.glyphs[currentGlyph].layers[layerId].paths:
		pathIndex = path.parent.indexOfPath_(path)
		for node in path.nodes:
			newNode = GSNode()
			newNode.x = node.x
			newNode.y = node.y
		
			if setting == 2:
				newNode.type = "offcurve"
			elif setting == 1:
				newNode.type = "line"
				font.glyphs[currentGlyph].layers[idHOI].paths.append(GSPath())
			else:
				newNode.type = "curve"
			print layerId, pathIndex, node.index, i
			font.glyphs[currentGlyph].layers[idHOI].paths[i].nodes.append(newNode)
			i = i + 1
			
		

def getFullName(layerName):
	for layer in font.glyphs[currentGlyph].layers:
		if re.match(layerName + ".*}$", layer.name) != None:
			return layer.name
	return layerName
	

def populateHOILayer(aName, cName, dName, bName, hoiName, cubicNum):	
	cName = getFullName(cName)
	dName = getFullName(dName)
	bName = getFullName(bName)
	
	if font.glyphs[currentGlyph].layers[hoiName] == None:
		newHOILayer = font.glyphs[currentGlyph].layers[aName].copy()
		newHOILayer.name = hoiName
		newHOILayer.paths = []
		font.glyphs[currentGlyph].layers.append(newHOILayer)
		
	if cubicNum == 1:
		addNode(aName, hoiName, 1)
	addNode(cName, hoiName, 2)
	addNode(dName, hoiName, 2)
	addNode(bName, hoiName, 3)


populateHOILayer("Regular", "500 C1", "500 D1", "500 B", "B HOI", 1)
populateHOILayer("Regular", "1000 C1", "1000 D1", "1000 B", "B HOI", 2)
# populateHOILayer("Regular Oblique", "E1", "F1", "G", "G HOI")
# populateHOILayer("Bold", "H1", "I1", "J", "J HOI")
# populateHOILayer("Bold Oblique", "K1", "L1", "M", "M HOI")