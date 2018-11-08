# Draw lines between t values of beziers

font = Glyphs.font

# Set Resolution
resolution = 20.0

numberOfPaths = len(font.selectedLayers[0].paths)
currentGlyphName = font.selectedLayers[0].parent.name

def pointOnBezier(t, path):
	C0 = (1-t) * (1-t) * (1-t)
	C1 = 3 * (1-t) * (1-t) * t
	C2 = 3 * (1-t) * t * t
	C3 = t * t * t
	
	P0 = path.nodes[0]
	P1 = path.nodes[1]
	P2 = path.nodes[2]
	P3 = path.nodes[3]
	
	x = C0 * P0.x + C1 * P1.x + C2 * P2.x + C3 * P3.x
	y = C0 * P0.y + C1 * P1.y + C2 * P2.y + C3 * P3.y
	
	return (x, y)

	
for j in range(numberOfPaths):
	print j
	for i in range(int(resolution)  + 1):
		t = i / resolution
		thisPoint = GSNode()
		thisPoint.x = pointOnBezier(t, font.selectedLayers[0].paths[j])[0]
		thisPoint.y = pointOnBezier(t, font.selectedLayers[0].paths[j])[1]
		if j == 0:
			newPath = GSPath()
			font.selectedLayers[0].paths.append(newPath)
	
		font.selectedLayers[0].paths[i+numberOfPaths].nodes.append(thisPoint)