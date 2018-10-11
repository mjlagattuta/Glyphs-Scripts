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
import math
import re

class viewHOI(ReporterPlugin):
	# The dialog view (e.g., panel or window)
	sliderView = objc.IBOutlet()

	# The sliders and button placed inside the view
	# TODO: slider number should be based on number of axes (there will be no limit with Glyphs App 3.0)
	# can use a for loop to gen them:: 	 globals()['slider%s' % (i + 1)] = objc.IBOutlet()
	# the issue is getting a variable amount of slider views to work and a variable number of methods using @objc.IBAction
	slider1 = objc.IBOutlet()
	slider2 = objc.IBOutlet() 
	slider3 = objc.IBOutlet() 
	slider4 = objc.IBOutlet()
	slider5 = objc.IBOutlet()
	slider6 = objc.IBOutlet()
	sync1 = objc.IBOutlet()
	sync2 = objc.IBOutlet() 
	sync3 = objc.IBOutlet() 
	sync4 = objc.IBOutlet()
	sync5 = objc.IBOutlet()
	sync6 = objc.IBOutlet()
	axisPreviewSelector = objc.IBOutlet()
	button = objc.IBOutlet()
	button2 = objc.IBOutlet()

	# Axis variables
	# TODO eventually: Fetch these values(DONE) + determine number of axes(important for Glyphs App 3)
	globals()['axis1Value'] = 84.0
	globals()['axis2Value'] = 0.0
	globals()['axis3Value'] = 0.0
	globals()['axis4Value'] = 0.0
	globals()['axis5Value'] = 0.0
	globals()['axis6Value'] = 1000.0

	globals()['check1'] = False
	globals()['check2'] = False
	globals()['check3'] = False
	globals()['check4'] = False
	globals()['check5'] = False
	globals()['check6'] = False

	selection = []
	nodeType = []
	showFuture = False
	angleTolerance = 1.0  # Tolerance is in degrees and anything above this value will appear red, anything below it will approach yellow and then green at 0.0
	font = Glyphs.font

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
				if master.widthValue > globals()['axis%sMax' % (index + 1)]:
					globals()['axis%sMax' % (index + 1)] = master.widthValue
			elif index == 2:
				if master.customValue < globals()['axis%sMin' % (index + 1)]:
					globals()['axis%sMin' % (index + 1)] = master.customValue
				if master.customValue > globals()['axis%sMax' % (index + 1)]:
					globals()['axis%sMax' % (index + 1)] = master.customValue
			elif index == 3:
				if master.customValue1 < globals()['axis%sMin' % (index + 1)]:
					globals()['axis%sMin' % (index + 1)] = master.customValue1
				if master.customValue1 > globals()['axis%sMax' % (index + 1)]:
					globals()['axis%sMax' % (index + 1)] = master.customValue1
			elif index == 4:
				if master.customValue2 < globals()['axis%sMin' % (index + 1)]:
					globals()['axis%sMin' % (index + 1)] = master.customValue2
				if master.customValue2 > globals()['axis%sMax' % (index + 1)]:
					globals()['axis%sMax' % (index + 1)] = master.customValue2
			elif index == 5:
				if master.customValue3 < globals()['axis%sMin' % (index + 1)]:
					globals()['axis%sMin' % (index + 1)] = master.customValue3
				if master.customValue3 > globals()['axis%sMax' % (index + 1)]:
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
			# Set axis values
			self.checkMasters(font, globals()['axis%s' % (i + 1)], i)
			self.checkVirtualMasters(font, globals()['axis%s' % (i + 1)], i)

			# Set slider values
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
			elif i == 2:
				self.slider3.setMinValue_(globals()['axis%sMin' % (i + 1)])
				self.slider3.setMaxValue_(globals()['axis%sMax' % (i + 1)])
				print "slider3"
				print globals()['axis%sMin' % (i + 1)]
				print globals()['axis%sMax' % (i + 1)]
			elif i == 3:
				self.slider4.setMinValue_(globals()['axis%sMin' % (i + 1)])
				self.slider4.setMaxValue_(globals()['axis%sMax' % (i + 1)])
				print "slider4"
				print globals()['axis%sMin' % (i + 1)]
				print globals()['axis%sMax' % (i + 1)]
			elif i == 4:
				self.slider5.setMinValue_(globals()['axis%sMin' % (i + 1)])
				self.slider5.setMaxValue_(globals()['axis%sMax' % (i + 1)])
				print "slider5"
				print globals()['axis%sMin' % (i + 1)]
				print globals()['axis%sMax' % (i + 1)]
			elif i == 5:
				self.slider6.setMinValue_(globals()['axis%sMin' % (i + 1)])
				self.slider6.setMaxValue_(globals()['axis%sMax' % (i + 1)])
				print "slider6"
				print globals()['axis%sMin' % (i + 1)]
				print globals()['axis%sMax' % (i + 1)]

	def settings(self):
		# Load .nib file next to plugin.py
		self.loadNib("sliderView", __file__)
		self.menuName = Glyphs.localize({'en': u'HOI Viewer', 'de': u'Mein Plugin'})
		# Load slider view as a right-click context menu
		self.generalContextMenus = [{'name': 'HOI Viewer', 'view': self.sliderView}]

	# Updates the temp instance and the drawings based on the sliders
	# TODO: Figure out how to pull the state of the check boxes and then set values equal based on it
	# Maybe use a dictionary to link axes?
	def sliderUpdate(self):
		sliderList = [self.slider1, self.slider2, self.slider3, self.slider4, self.slider5, self.slider6]

		keySlider = None
		for i in range(len(self.font.axes)):
			if globals()['check%s' % (i + 1)] == True:
				keySlider = i
				break

		for i in range(len(self.font.axes)):
			# if keySlider != None:
			# 	keySliderAlias = vars(viewHOI)['slider%s' % (keySlider)])
			# sliderAlias = vars(viewHOI)['slider%s' % (i + 1)]
			if globals()['check%s' % (i + 1)] == True:
				globals()['axis%sValue' % (i + 1)] = sliderList[keySlider].floatValue()
			else:
				globals()['axis%sValue' % (i + 1)] = sliderList[i].floatValue()

		# axis1Value = self.slider1.floatValue()
		# axis2Value = self.slider2.floatValue()
		# axis3Value = self.slider3.floatValue()
		# axis4Value = self.slider4.floatValue()
		# axis5Value = self.slider5.floatValue()
		# axis6Value = self.slider6.floatValue()

		layer = Glyphs.font.selectedLayers[0]
		currentGlyphName = layer.parent.name

		tempInstance = self.font.instances[0].copy()
		tempInstance.name = "tempInstance"
		tempInstance.weightValue = axis1Value
		tempInstance.widthValue = axis2Value
		tempInstance.customValue = axis3Value
		tempInstance.setInterpolationCustom1_(axis4Value)
		tempInstance.setInterpolationCustom2_(axis5Value)
		tempInstance.setInterpolationCustom3_(axis6Value)
		self.tempInstance = tempInstance
		
		Glyphs.redraw()


	# Slider actions use the sliderUpdate method
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

	@objc.IBAction
	def slider5_(self, sender):
		self.sliderUpdate()

	@objc.IBAction
	def slider6_(self, sender):
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

	@objc.IBAction
	def sync1_(self, sender):
		if globals()['check1'] == True:
			globals()['check1'] = False
		else:
			globals()['check1'] = True

	@objc.IBAction
	def sync2_(self, sender):
		if globals()['check2'] == True:
			globals()['check2'] = False
		else:
			globals()['check2'] = True

	@objc.IBAction
	def sync3_(self, sender):
		if globals()['check3'] == True:
			globals()['check3'] = False
		else:
			globals()['check3'] = True

	@objc.IBAction
	def sync4_(self, sender):
		if globals()['check4'] == True:
			globals()['check4'] = False
		else:
			globals()['check4'] = True

	@objc.IBAction
	def sync5_(self, sender):
		if globals()['check5'] == True:
			globals()['check5'] = False
		else:
			globals()['check5'] = True

	@objc.IBAction
	def sync6_(self, sender):
		if globals()['check6'] == True:
			globals()['check6'] = False
		else:
			globals()['check6'] = True

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
		futureTempInstance = self.font.instances[0].copy()
		futureTempInstance.name = "futuretempInstance"
		futureTempInstance.weightValue = axis1Value
		futureTempInstance.widthValue = axis2Value

		# TODO: these should be set to axis#Values like the rest of them, and then choosing a preview axis will decide which ones become zero
		futureTempInstance.customValue = 0
		futureTempInstance.setInterpolationCustom1_(0)
		futureTempInstance.setInterpolationCustom2_(0)

		futureTempInstance.setInterpolationCustom3_(axis6Value)

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
		if self.font != Glyphs.font:
				self.setup = True

		if self.setup == True:
			self.font = Glyphs.font
			iterAxes = range(len(self.font.axes))
			self.makeAxisVariables(self.font, iterAxes)
			self.setAxisExtremes(self.font, iterAxes)
			self.setup = False

		# move this to a method? then store in a variable with all the relevant axes values
		tempInstance = self.font.instances[0].copy()
		tempInstance.name = "tempInstance"
		tempInstance.weightValue = axis1Value
		tempInstance.widthValue = axis2Value
		tempInstance.customValue = axis3Value
		tempInstance.setInterpolationCustom1_(axis4Value)
		tempInstance.setInterpolationCustom2_(axis5Value)
		tempInstance.setInterpolationCustom3_(axis6Value)

		currentGlyphName = layer.parent.name
		masterLayer = layer.parent.layers[layer.associatedMasterId]

		cx1 = None
		cy1 = None
		cx2 = None
		cy2 = None

		# For more than one path
		tempFontLayer = tempInstance.interpolatedFontProxy.glyphs[currentGlyphName].layers[0]

		pathIndex = 0
		t = NSBezierPath.bezierPath()

		# Draw glyph preview  ——————————————————————————————————————————————————————————————————————————————————————

		# Move this to its own method?? parameters (self, tempFontLayer)
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



		# Draw nodes + lines between selected nodes for angle/kink proofing ———————————————————————————————————————————
		p = NSBezierPath.bezierPath()
		scale = self.font.currentTab.scale
		lineScale = 0.0 / scale
		nodeScale = 8.0 / scale

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

	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
