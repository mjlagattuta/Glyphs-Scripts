# encoding: utf-8

###########################################################################################################
#
#
#	Reporter Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################

import objc
import GlyphsApp
from GlyphsApp import *
from GlyphsApp.plugins import *
# from Cocoa import NSBezierPath
import math
import re

class viewHOI(ReporterPlugin):
	# the dialog view (e.g., panel or window)
	sliderView = objc.IBOutlet()

	# the sliders and button placed inside the view
	# TODO: slider number should be based on number of axes (there will be no limit with Glyphs App 3.0)
	# can use a for loop to gen them:: 	 globals()['slider%s' % (i + 1)] = objc.IBOutlet()
	# the issue is getting a variable amount of slider views to work and a variable number of methods using @objc.IBAction
	slider1 = objc.IBOutlet()
	slider2 = objc.IBOutlet() 
	slider3 = objc.IBOutlet() 
	slider4 = objc.IBOutlet()
	button = objc.IBOutlet()
	button2 = objc.IBOutlet()

	# Axis variables
	# TODO eventually: Fetch these values + determine number of axes
	weightValue = 84.0
	slantValue = 0.0
	italicValue = 0.0
	monoValue = 1000.0
	selection = []
	nodeType = []
	showFuture = False
	angleTolerance = 1.0
	font = Glyphs.font
	# lastState = GSPath()

	setup = True
	# Set up variables for the name of each axis "axis" + "#" starting from 1
	# Also makes variables for Min and Max values
	def makeAxisVariables(self, font, iterAxes):
		for i in iterAxes:
			globals()['axis%s' % (i + 1)] = font.axes[i]["Name"]
			globals()['axis%sMin' % (i + 1)] = 100000.0
			globals()['axis%sMax' % (i + 1)] = -100000.0
		
	def checkMasters(self, font, axis, index):
		for master in font.masters:
			if index == 0:
				if master.weightValue < globals()['axis%sMin' % (index + 1)]:
					globals()['axis%sMin' % (index + 1)] = master.weightValue
				if master.weightValue > globals()['axis%sMax' % (index + 1)]:
					globals()['axis%sMax' % (index + 1)] = master.weightValue
			elif index == 1:
				if master.widthValue < globals()['axis%sMin' % (index + 1)]:
					globals()['axis%sMin' % (index + 1)] = master.widthValue
				if master.weightValue > globals()['axis%sMax' % (index + 1)]:
					globals()['axis%sMax' % (index + 1)] = master.widthValue
			elif index == 2:
				if master.customValue < globals()['axis%sMin' % (index + 1)]:
					globals()['axis%sMin' % (index + 1)] = master.customValue
				if master.weightValue > globals()['axis%sMax' % (index + 1)]:
					globals()['axis%sMax' % (index + 1)] = master.customValue
			elif index == 3:
				if master.customValue1 < globals()['axis%sMin' % (index + 1)]:
					globals()['axis%sMin' % (index + 1)] = master.customValue1
				if master.weightValue > globals()['axis%sMax' % (index + 1)]:
					globals()['axis%sMax' % (index + 1)] = master.customValue1
			elif index == 4:
				if master.customValue2 < globals()['axis%sMin' % (index + 1)]:
					globals()['axis%sMin' % (index + 1)] = master.customValue2
				if master.weightValue > globals()['axis%sMax' % (index + 1)]:
					globals()['axis%sMax' % (index + 1)] = master.customValue2
			elif index == 5:
				if master.customValue3 < globals()['axis%sMin' % (index + 1)]:
					globals()['axis%sMin' % (index + 1)] = master.customValue3
				if master.weightValue > globals()['axis%sMax' % (index + 1)]:
					globals()['axis%sMax' % (index + 1)] = master.customValue3
					
	def checkVirtualMasters(self, font, axis, index):
		for parameter in font.customParameters:
			if parameter.name == "Virtual Master":
				for item in parameter.value:
					if item["Axis"] == axis:
						if float(item["Location"]) < float(globals()['axis%sMin' % (index + 1)]):
							globals()['axis%sMin' % (index + 1)] = float(item["Location"])
						if float(item["Location"]) > float(globals()['axis%sMax' % (index + 1)]):
							globals()['axis%sMax' % (index + 1)] = float(item["Location"])

	def setAxisExtremes(self, font, iterAxes):
		for i in iterAxes:
			# Set sliders to values here
			self.checkMasters(font, globals()['axis%s' % (i + 1)], i)
			self.checkVirtualMasters(font, globals()['axis%s' % (i + 1)], i)

			if i == 0:
				self.slider1.setMinValue_(globals()['axis%sMin' % (i + 1)])
				self.slider1.setMaxValue_(globals()['axis%sMax' % (i + 1)])
				print "slider1"
				print globals()['axis%sMin' % (i + 1)]
				print globals()['axis%sMax' % (i + 1)]
			elif i == 1:
				self.slider2.setMinValue_(globals()['axis%sMin' % (i + 1)])
				self.slider2.setMaxValue_(globals()['axis%sMax' % (i + 1)])
				print "slider2"
				print globals()['axis%sMin' % (i + 1)]
				print globals()['axis%sMax' % (i + 1)]
			elif i == 2 or i == 3 or i == 4:
				self.slider3.setMinValue_(globals()['axis%sMin' % (i + 1)])
				self.slider3.setMaxValue_(globals()['axis%sMax' % (i + 1)])
				print "slider3"
				print globals()['axis%sMin' % (i + 1)]
				print globals()['axis%sMax' % (i + 1)]
			elif i == 5:
				self.slider4.setMinValue_(globals()['axis%sMin' % (i + 1)])
				self.slider4.setMaxValue_(globals()['axis%sMax' % (i + 1)])
				print "slider4"
				print globals()['axis%sMin' % (i + 1)]
				print globals()['axis%sMax' % (i + 1)]

				


	def settings(self):
		# Load .nib file next to plugin.py
		self.loadNib("sliderView", __file__)
		self.menuName = Glyphs.localize({'en': u'HOI Viewer', 'de': u'Mein Plugin'})
		# Load slider view as a right-click context menu
		self.generalContextMenus = [{'name': 'HOI Viewer', 'view': self.sliderView}]

		# TODO: pull these values from the file
		# self.slider1.setMinValue_(84.0)
		# self.slider1.setMaxValue_(132.0)
		# self.slider2.setMinValue_(0.0)
		# self.slider2.setMaxValue_(1000.0)
		# self.slider3.setMinValue_(0.0)
		# self.slider3.setMaxValue_(1000.0)
		# self.slider4.setMinValue_(0.0)
		# self.slider4.setMaxValue_(1000.0)

	# Updates the temp instance and the drawings based on the sliders
	def sliderUpdate(self):
		self.weightValue = self.slider1.floatValue()
		self.slantValue = self.slider2.floatValue()
		self.italicValue = self.slider3.floatValue()
		self.monoValue = self.slider4.floatValue()

		layer = Glyphs.font.selectedLayers[0]
		currentGlyphName = layer.parent.name

		tempInstance = layer.parent.parent.instances[0].copy()
		tempInstance.name = "tempInstance"
		tempInstance.weightValue = self.weightValue
		tempInstance.widthValue = self.slantValue
		tempInstance.customValue = self.italicValue
		tempInstance.setInterpolationCustom1_(self.italicValue)
		tempInstance.setInterpolationCustom2_(self.italicValue)
		tempInstance.setInterpolationCustom3_(self.monoValue)
		self.tempInstance = tempInstance
		
		Glyphs.redraw()


	# Slider actions use the sliderUpdate function
	@objc.IBAction
	def slider1_(self, sender):
		self.sliderUpdate()

	@objc.IBAction
	def slider2_(self, sender):
		self.sliderUpdate()

	@objc.IBAction
	def slider3_(self, sender):
		self.sliderUpdate()

	@objc.IBAction
	def slider4_(self, sender):
		self.sliderUpdate()

	# reset selection
	@objc.IBAction
	def button_(self, sender):
		self.selection = []
		self.nodeType = []
		Glyphs.redraw()

	# Toggle future
	@objc.IBAction
	def button2_(self, sender):
		if self.showFuture == True:
			self.showFuture = False
		else:
			self.showFuture = True
		Glyphs.redraw()

	# generate nodes in preview
	def roundDotForPoint( self, thisPoint, markerWidth ):
		"""
		from Show Angled Handles by MekkaBlue
		Returns a circle with thisRadius around thisPoint.
		"""
		myRect = NSRect( ( thisPoint.x - markerWidth * 0.5, thisPoint.y - markerWidth * 0.5 ), ( markerWidth, markerWidth ) )
		return NSBezierPath.bezierPathWithOvalInRect_(myRect)

	# node color changes based on angle (change the 'angleTolerance' variable)
	def nodeColor(self, nodePrev, node, nodeNext):
		dx1 = node.x - nodePrev.x
		dy1 = node.y - nodePrev.y
		angle1 = math.degrees(math.atan2(dy1, dx1))
		dx2 = nodeNext.x - node.x 
		dy2 = nodeNext.y - node.y
		angle2 = math.degrees(math.atan2(dy2, dx2))
		diff = abs(angle2 - angle1)

		if diff > 180:
			diff = 360 - diff
		if diff >= (self.angleTolerance * 2):
			redValue = 1.0
			greenValue = 0.0
		elif diff < self.angleTolerance:
			redValue = (diff % self.angleTolerance) / self.angleTolerance
			greenValue = 1.0
		else:
			redValue = 1.0
			greenValue = 1.0 - ((diff % self.angleTolerance) / self.angleTolerance)

		return (redValue, greenValue)


	# Start sync layers defs ———————————————————————————————————————————————————————————————————————
	# These functions are currently now being used...too slow
	# need to make currentGlyph a class variable rather than a local one
	def getFullName(self, layerName):
		currentGlyph = Glyphs.font.selectedLayers[0].parent

		for layer in currentGlyph.layers:
			if re.match(layerName + ".*}$", layer.name):
				return layer.name

	# Sync everything to the primary control masters V2
	# needs to work with more paths*****
	def syncToControl(self, aName, cName, dName, bName, hoiName):	
		currentGlyph = Glyphs.font.selectedLayers[0].parent
		
		c2Name = self.getFullName(re.sub("\d", "2", cName))
		c3Name = self.getFullName(re.sub("\d", "3", cName))
		cName = self.getFullName(cName)
		
		d2Name = self.getFullName(re.sub("\d", "2", dName))
		d3Name = self.getFullName(re.sub("\d", "3", dName))
		dName = self.getFullName(dName)
		bName = self.getFullName(bName)

		for node in currentGlyph.layers[0].paths[0].nodes:	
			currentGlyph.layers[c2Name].paths[0].nodes[node.index].position = currentGlyph.layers[cName].paths[0].nodes[node.index].position
			currentGlyph.layers[c3Name].paths[0].nodes[node.index].position = currentGlyph.layers[cName].paths[0].nodes[node.index].position
			
			currentGlyph.layers[d2Name].paths[0].nodes[node.index].position = currentGlyph.layers[dName].paths[0].nodes[node.index].position
			currentGlyph.layers[d3Name].paths[0].nodes[node.index].position = currentGlyph.layers[dName].paths[0].nodes[node.index].position
			
			currentGlyph.layers[hoiName].paths[node.index].nodes[0].position = currentGlyph.layers[aName].paths[0].nodes[node.index].position
			currentGlyph.layers[hoiName].paths[node.index].nodes[1].position = currentGlyph.layers[cName].paths[0].nodes[node.index].position
			currentGlyph.layers[hoiName].paths[node.index].nodes[2].position = currentGlyph.layers[dName].paths[0].nodes[node.index].position
			currentGlyph.layers[hoiName].paths[node.index].nodes[3].position = currentGlyph.layers[bName].paths[0].nodes[node.index].position


	# Sync everything to the respective HOI layer V2
	# needs to work with more paths*****
	def syncToHOI(self, aName, cName, dName, bName, hoiName):	
		currentGlyph = Glyphs.font.selectedLayers[0].parent
		
		c2Name = self.getFullName(re.sub("\d", "2", cName))
		c3Name = self.getFullName(re.sub("\d", "3", cName))
		cName = self.getFullName(cName)
		
		d2Name = self.getFullName(re.sub("\d", "2", dName))
		d3Name = self.getFullName(re.sub("\d", "3", dName))
		dName = self.getFullName(dName)
		bName = self.getFullName(bName)

		for node in currentGlyph.layers[0].paths[0].nodes:	
			currentGlyph.layers[aName].paths[0].nodes[node.index].position = currentGlyph.layers[hoiName].paths[node.index].nodes[0].position
			
			currentGlyph.layers[cName].paths[0].nodes[node.index].position = currentGlyph.layers[hoiName].paths[node.index].nodes[1].position
			currentGlyph.layers[c2Name].paths[0].nodes[node.index].position = currentGlyph.layers[hoiName].paths[node.index].nodes[1].position
			currentGlyph.layers[c3Name].paths[0].nodes[node.index].position = currentGlyph.layers[hoiName].paths[node.index].nodes[1].position
			
			currentGlyph.layers[dName].paths[0].nodes[node.index].position = currentGlyph.layers[hoiName].paths[node.index].nodes[2].position
			currentGlyph.layers[d2Name].paths[0].nodes[node.index].position = currentGlyph.layers[hoiName].paths[node.index].nodes[2].position
			currentGlyph.layers[d3Name].paths[0].nodes[node.index].position = currentGlyph.layers[hoiName].paths[node.index].nodes[2].position
			
			currentGlyph.layers[bName].paths[0].nodes[node.index].position = currentGlyph.layers[hoiName].paths[node.index].nodes[3].position

	# End sync layers defs —————————————————————————————————————————————————————————————————————————

	# There should be an option in the interface to check off which axis you can preview along
	# This should work in tandem with the HOI selection to allow multiple axes to be previewed at the same time
	def showAll(self, layer, currentGlyphName, pathIndex, interpolatedIndex, nodeScale):
		# Can iterate here to view the angle of the point at intervals ahead and behind the current preview
		futureTempInstance = layer.parent.parent.instances[0].copy()
		futureTempInstance.name = "futuretempInstance"
		futureTempInstance.weightValue = self.weightValue
		futureTempInstance.widthValue = self.slantValue
		futureTempInstance.setInterpolationCustom3_(self.monoValue)
		futureTempInstance.customValue = 0
		futureTempInstance.setInterpolationCustom1_(0)
		futureTempInstance.setInterpolationCustom2_(0)

		# If this can be faster then the range can be more to show smaller increments, or show more points at once
		for i in range(20):
			# For line visualization
			# if i == 0:
			# 	futureFontLayer = futureTempInstance.interpolatedFontProxy.glyphs[currentGlyphName].layers[0]
			# 	x1 = futureFontLayer.paths[pathIndex].nodes[interpolatedIndex].x
			# 	y1 = futureFontLayer.paths[pathIndex].nodes[interpolatedIndex].y
			# else:
			# 	x1 = x2
			# 	y1 = y2

			# pNode = NSBezierPath.bezierPath()
			# pNode.moveToPoint_(NSMakePoint(x1, y1))

			futureTempInstance.customValue = i * 50
			futureTempInstance.setInterpolationCustom1_(i * 50)
			futureTempInstance.setInterpolationCustom2_(i * 50)

			futureFontLayer = futureTempInstance.interpolatedFontProxy.glyphs[currentGlyphName].layers[0]

			x2 = futureFontLayer.paths[pathIndex].nodes[interpolatedIndex].x
			y2 = futureFontLayer.paths[pathIndex].nodes[interpolatedIndex].y

			ThisPoint = NSMakePoint(x2, y2)

			# For point visualization
			pNode = NSBezierPath.bezierPath()
			pNode.appendBezierPath_( self.roundDotForPoint( ThisPoint, nodeScale) )

			# Changes node color based on angle
			NSColor.colorWithCalibratedRed_green_blue_alpha_(
				self.nodeColor(futureFontLayer.paths[pathIndex].nodes[interpolatedIndex - 1],  futureFontLayer.paths[pathIndex].nodes[interpolatedIndex],  futureFontLayer.paths[pathIndex].nodes[interpolatedIndex + 1])[0] ,
				self.nodeColor(futureFontLayer.paths[pathIndex].nodes[interpolatedIndex - 1],  futureFontLayer.paths[pathIndex].nodes[interpolatedIndex],  futureFontLayer.paths[pathIndex].nodes[interpolatedIndex + 1])[1] ,
				0.0,
				0.45).set()
			# pNode.setLineWidth_(nodeScale)
			# pNode.lineToPoint_(ThisPoint)
			pNode.fill()

		
	def foreground(self, layer):
		if layer.parent.parent != self.font:
				self.setup = True

		if self.setup == True:
			self.font = layer.parent.parent
			iterAxes = range(len(self.font.axes))
			self.makeAxisVariables(self.font, iterAxes)
			self.setAxisExtremes(self.font, iterAxes)
			self.setup = False


		# is this necessary?
		self.italicValue = self.slider3.floatValue()

		tempInstance = layer.parent.parent.instances[0].copy()
		tempInstance.name = "tempInstance"
		tempInstance.weightValue = self.weightValue
		tempInstance.widthValue = self.slantValue
		tempInstance.customValue = self.italicValue
		tempInstance.setInterpolationCustom1_(self.italicValue)
		tempInstance.setInterpolationCustom2_(self.italicValue)
		tempInstance.setInterpolationCustom3_(self.monoValue)

		currentGlyphName = layer.parent.name
		masterLayer = layer.parent.layers[layer.associatedMasterId]

		cx1 = None
		cy1 = None
		cx2 = None
		cy2 = None

		# Need to deprecate this
		tempFont = tempInstance.interpolatedFontProxy.glyphs[currentGlyphName].layers[0].paths[0]

		# For more than one path
		tempFontLayer = tempInstance.interpolatedFontProxy.glyphs[currentGlyphName].layers[0]

		pathIndex = 0
		t = NSBezierPath.bezierPath()

		# Draw glyph preview  ——————————————————————————————————————————————————————————————————————————————————————

		for path in masterLayer.paths:
			tSub = NSBezierPath.bezierPath()

			tx1 = tempFontLayer.paths[pathIndex].nodes[-1].x
			ty1 = tempFontLayer.paths[pathIndex].nodes[-1].y
			tSub.moveToPoint_(NSMakePoint(tx1, ty1))

			# VF preview as fill
			for node in masterLayer.paths[pathIndex].nodes:
				if node.type != "offcurve":
					tx2 = tempFontLayer.paths[pathIndex].nodes[node.index].x
					ty2 = tempFontLayer.paths[pathIndex].nodes[node.index].y

				if node.type == "line":
					tSub.lineToPoint_(NSMakePoint(tx2, ty2))
				elif node.type == "offcurve":
					if cx1 == None:
						cx1 = tempFontLayer.paths[pathIndex].nodes[node.index].x
						cy1 = tempFontLayer.paths[pathIndex].nodes[node.index].y
					else:
						cx2 = tempFontLayer.paths[pathIndex].nodes[node.index].x
						cy2 = tempFontLayer.paths[pathIndex].nodes[node.index].y
				else:
					tSub.curveToPoint_controlPoint1_controlPoint2_(NSMakePoint(tx2, ty2), NSMakePoint(cx1, cy1), NSMakePoint(cx2, cy2))
					cx1 = None
					cy1 = None
					cx2 = None
					cy2 = None

			pathIndex = pathIndex + 1

			tSub.closePath()
			t.appendBezierPath_( tSub )
			NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.5, 0.5, 0.4).set()

		t.fill()

		# currentState = layer.paths[0]

		# Adding a state variable and an if statement makes this not as responsive as I'd like
		# if re.match("HOI$", layer.name) != None:
		# 	self.syncToHOI("Regular", "C1", "D1", "B", "B HOI")
		# 	self.syncToHOI("Regular Oblique", "E1", "F1", "G", "G HOI")
		# 	self.syncToHOI("Bold", "H1", "I1", "J", "J HOI")
		# 	self.syncToHOI("Bold Oblique", "K1", "L1", "M", "M HOI")
		# else:
		# 	self.syncToControl("Regular", "C1", "D1", "B", "B HOI")
		# 	self.syncToControl("Regular Oblique", "E1", "F1", "G", "G HOI")
		# 	self.syncToControl("Bold", "H1", "I1", "J", "J HOI")
		# 	self.syncToControl("Bold Oblique", "K1", "L1", "M", "M HOI")

		# self.lastState = currentState



		# Draw nodes + lines between nodes for angle/kink proofing ———————————————————————————————————————————————

		p = NSBezierPath.bezierPath()
		scale = layer.parent.parent.currentTab.scale
		lineScale = 0.0 / scale
		nodeScale = 8.0 / scale
		# (1) Adding code for showing nodes and changing color based on angle

		# VF preview selection
		if self.selection == []:
			pLine = NSBezierPath.bezierPath()

			pathIndex = 0
			for path in masterLayer.paths:
				pathSelection = []
				pathNodeTypes = []
				for node in layer.paths[pathIndex].nodes:
					if node.selected:
						x1 = tempFontLayer.paths[pathIndex].nodes[node.index - 1].x
						y1 = tempFontLayer.paths[pathIndex].nodes[node.index - 1].y
						pLine.moveToPoint_(NSMakePoint(x1, y1))
						break

				for node in layer.paths[pathIndex].nodes:
					if node.selected:
						interpolatedIndex = node.index
						pathSelection.append(interpolatedIndex)
						pathNodeTypes.append(node.type)

						x2 = tempFontLayer.paths[pathIndex].nodes[interpolatedIndex].x
						y2 = tempFontLayer.paths[pathIndex].nodes[interpolatedIndex].y

						NSColor.blueColor().set()

						# p.moveToPoint_(NSMakePoint(x1, y1))
						pLine.lineToPoint_(NSMakePoint(x2, y2))
						# pLine.setLineWidth_(lineScale)
						# p.stroke()
						p.appendBezierPath_( pLine )

						# FUTURE block ————————————————————————————————————————————————————————————

						if self.showFuture == True and node.type != "offcurve":
							self.showAll(layer, currentGlyphName, pathIndex, interpolatedIndex, nodeScale)

						# FUTURE block ————————————————————————————————————————————————————————————

						ThisPoint = NSMakePoint(x2, y2)
						pNode = NSBezierPath.bezierPath()
						# (1) Adding code for showing nodes and changing color based on angle
						pNode.appendBezierPath_( self.roundDotForPoint( ThisPoint, nodeScale ) )

						# Changes node color based on angle
						NSColor.colorWithCalibratedRed_green_blue_alpha_(
							self.nodeColor(tempFontLayer.paths[pathIndex].nodes[interpolatedIndex - 1],  tempFontLayer.paths[pathIndex].nodes[interpolatedIndex],  tempFontLayer.paths[pathIndex].nodes[interpolatedIndex + 1])[0] ,
							self.nodeColor(tempFontLayer.paths[pathIndex].nodes[interpolatedIndex - 1],  tempFontLayer.paths[pathIndex].nodes[interpolatedIndex],  tempFontLayer.paths[pathIndex].nodes[interpolatedIndex + 1])[1] ,
							0.0,
							1.0).set()
						pNode.fill()

						if node.type != "offcurve":
							NSColor.colorWithCalibratedRed_green_blue_alpha_( 0.0, 0.0, 1.0, 1.0).set()
							pNode.setLineWidth_(lineScale * 4)
							pNode.stroke()

				if pathSelection != []:
					self.selection.append(pathSelection)
					self.nodeType.append(pathNodeTypes)
				pathIndex = pathIndex + 1

		else:
			pathIndex = 0
			for path in masterLayer.paths:
				pLine = NSBezierPath.bezierPath()
				i = 0
				x1 = tempFontLayer.paths[pathIndex].nodes[self.selection[pathIndex][-1]].x
				y1 = tempFontLayer.paths[pathIndex].nodes[self.selection[pathIndex][-1]].y
				pLine.moveToPoint_(NSMakePoint(x1, y1))
				for nodeIndex in self.selection[pathIndex]:
					interpolatedIndex = nodeIndex

					x2 = tempFontLayer.paths[pathIndex].nodes[interpolatedIndex].x
					y2 = tempFontLayer.paths[pathIndex].nodes[interpolatedIndex].y

					# p.moveToPoint_(NSMakePoint(x1, y1))
					pLine.lineToPoint_(NSMakePoint(x2, y2))
					# pLine.setLineWidth_(lineScale)
					# p.stroke()
					p.appendBezierPath_( pLine )


					# FUTURE block ————————————————————————————————————————————————————————————

					if self.showFuture == True and self.nodeType[pathIndex][i] != "offcurve":
						self.showAll(layer, currentGlyphName, pathIndex, interpolatedIndex, nodeScale)

					# FUTURE block ————————————————————————————————————————————————————————————

					pNode = NSBezierPath.bezierPath()

					ThisPoint = NSMakePoint(x2, y2)

					# (1) Adding code for showing nodes and changing color based on angle
					pNode.appendBezierPath_( self.roundDotForPoint( ThisPoint, nodeScale ) )

					# Changes node color based on angle
					NSColor.colorWithCalibratedRed_green_blue_alpha_(
						self.nodeColor(tempFontLayer.paths[pathIndex].nodes[interpolatedIndex - 1],  tempFontLayer.paths[pathIndex].nodes[interpolatedIndex],  tempFontLayer.paths[pathIndex].nodes[interpolatedIndex + 1])[0] ,
						self.nodeColor(tempFontLayer.paths[pathIndex].nodes[interpolatedIndex - 1],  tempFontLayer.paths[pathIndex].nodes[interpolatedIndex],  tempFontLayer.paths[pathIndex].nodes[interpolatedIndex + 1])[1] ,
						0.0,
						1.0).set()
					pNode.fill()

					if self.nodeType[pathIndex][i] != "offcurve":
						NSColor.colorWithCalibratedRed_green_blue_alpha_( 0.0, 0.0, 1.0, 1.0).set()
						pNode.setLineWidth_(lineScale * 4)
						pNode.stroke()

					i = i + 1

				pathIndex = pathIndex + 1

		NSColor.blueColor().set()
		p.setLineWidth_(lineScale)
		p.stroke()

	# def inactiveLayer(self, layer):
	# 	NSColor.redColor().set()
	# 	if layer.paths:
	# 		layer.bezierPath.fill()
	# 	if layer.components:
	# 		for component in layer.components:
	# 			component.bezierPath.fill()

	# def preview(self, layer):
	# 	NSColor.blueColor().set()
	# 	if layer.paths:
	# 		layer.bezierPath.fill()
	# 	if layer.components:
	# 		for component in layer.components:
	# 			component.bezierPath.fill()

	
	# def doSomething(self):
	# 	print 'Just did something'
		
	# def conditionalContextMenus(self):

	# 	# Empty list of context menu items
	# 	contextMenus = []

	# 	# Execute only if layers are actually selected
	# 	if Glyphs.font.selectedLayers:
	# 		layer = Glyphs.font.selectedLayers[0]
			
	# 		# Exactly one object is selected and it’s an anchor
	# 		if len(layer.selection) == 1 and type(layer.selection[0]) == GSAnchor:
					
	# 			# Add context menu item
	# 			contextMenus.append({'name': '2nd View', 'view': self.sliderView})
	# 			contextMenus.append({'name': '2nd View', 'view': self.slider})

	# 	# Return list of context menu items
	# 	return contextMenus

	# def doSomethingElse(self):
	# 	print 'Just did something else'

	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
