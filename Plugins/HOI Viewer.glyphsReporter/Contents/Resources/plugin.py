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

from __future__ import print_function
import objc
import GlyphsApp
from GlyphsApp import *
from GlyphsApp.plugins import *
import math
import time
import re

glyphsVersion = Glyphs.buildNumber
def getAxisName(axis):
	if glyphsVersion > 3000:
		return axis.name
	return axis["Name"]

class viewHOI(ReporterPlugin):
	# The dialog view (e.g., panel or window)
	# TODO: currently this is a right click context menu but may make more sense as a persistent window
	sliderView = objc.IBOutlet()

	# The sliders and UI elements placed inside the view
	# TODO: slider number should be based on number of axes (there will be no limit with Glyphs App 3.0)
	## can use a for loop to gen them:: 	 globals()['slider%s' % (i + 1)] = objc.IBOutlet()
	## the issue is getting a variable amount of slider views to work and a variable number of methods using @objc.IBAction
	# TODO: Add options to change the type of preview shown (i.e. turn node view on and off, outline and fill view, etc.)
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
	# DONE: Fetch these values
	# TODO: Determine number of axes(important for Glyphs App 3)
	globals()['axis1Value'] = 100.0
	globals()['axis2Value'] = 0.0
	globals()['axis3Value'] = 0.0
	globals()['axis4Value'] = 0.0
	globals()['axis5Value'] = 0.0
	globals()['axis6Value'] = 0.0

	globals()['check1'] = False
	globals()['check2'] = False
	globals()['check3'] = False
	globals()['check4'] = False
	globals()['check5'] = False
	globals()['check6'] = False

	font = Glyphs.font

	selection = []
	nodeType = []
	showFuture = False

#########  Set Tolerance  #########

	angleTolerance = 1.0 

#########  Set Tolerance  #########

	setup = True

	# Set up variables for the name of each axis "axis" + "#" starting from 1
	# Also makes variables for Min and Max values
	@objc.python_method
	def makeAxisVariables(self, font, iterAxes):
		for i in iterAxes:
			globals()['axis%s' % (i + 1)] = getAxisName(font.axes[i])
			globals()['axis%sMin' % (i + 1)] = 100000.0
			globals()['axis%sMax' % (i + 1)] = -100000.0
		
	@objc.python_method
	def checkMasters(self, font, axis, index):
		for master in font.masters:
			axisValue = master.axes[index]
			if axisValue < globals()['axis%sMin' % (index + 1)]:
				globals()['axis%sMin' % (index + 1)] = axisValue
			if axisValue > globals()['axis%sMax' % (index + 1)]:
				globals()['axis%sMax' % (index + 1)] = axisValue

	@objc.python_method
	def checkVirtualMasters(self, font, axis, index):
		for parameter in font.customParameters:
			if parameter.name == "Virtual Master":
				for item in parameter.value:
					if item["Axis"] == axis:
						if float(item["Location"]) < float(globals()['axis%sMin' % (index + 1)]):
							globals()['axis%sMin' % (index + 1)] = float(item["Location"])
						if float(item["Location"]) > float(globals()['axis%sMax' % (index + 1)]):
							globals()['axis%sMax' % (index + 1)] = float(item["Location"])

	# Can maybe truncate this
	@objc.python_method
	def setAxisExtremes(self, font, iterAxes):
		for i in iterAxes:
			# Set axis values
			self.checkMasters(font, globals()['axis%s' % (i + 1)], i)
			self.checkVirtualMasters(font, globals()['axis%s' % (i + 1)], i)
			
			minValue = globals()['axis%sMin' % (i + 1)]
			maxValue = globals()['axis%sMax' % (i + 1)]
			# Set slider values
			if i == 0:
				self.slider1.setMinValue_(minValue)
				self.slider1.setMaxValue_(maxValue)
			elif i == 1:
				self.slider2.setMinValue_(minValue)
				self.slider2.setMaxValue_(maxValue)
			elif i == 2:
				self.slider3.setMinValue_(minValue)
				self.slider3.setMaxValue_(maxValue)
			elif i == 3:
				self.slider4.setMinValue_(minValue)
				self.slider4.setMaxValue_(maxValue)
			elif i == 4:
				self.slider5.setMinValue_(minValue)
				self.slider5.setMaxValue_(maxValue)
			elif i == 5:
				self.slider6.setMinValue_(minValue)
				self.slider6.setMaxValue_(maxValue)
			print(getAxisName(font.axes[i]))
			print(minValue)
			print(maxValue)

	@objc.python_method
	def settings(self):
		# Load .nib file next to plugin.py
		self.loadNib("sliderView", __file__)
		self.menuName = Glyphs.localize({'en': u'HOI Viewer'})
		# Load slider view as a right-click context menu
		self.generalContextMenus = [{'name': 'HOI Viewer', 'view': self.sliderView}]

	# Updates the temp instance and the drawings based on the sliders
	# DONE: Figure out how to pull the state of the check boxes and then set values equal based on it
	# TODO: use a dictionary to link axes rather than iterating through them
	@objc.python_method
	def sliderUpdate(self):
		sliderList = [self.slider1, self.slider2, self.slider3, self.slider4, self.slider5, self.slider6]
		keySlider = None

		for i in range(len(self.font.axes)):
			if globals()['check%s' % (i + 1)] == True:
				keySlider = i
				break

		# TODO: have sliders that are synced have UI feedback
		for i in range(len(self.font.axes)):
			# if keySlider != None:
			# 	keySliderAlias = vars(viewHOI)['slider%s' % (keySlider)])
			# sliderAlias = vars(viewHOI)['slider%s' % (i + 1)]
			if globals()['check%s' % (i + 1)] == True:
				globals()['axis%sValue' % (i + 1)] = sliderList[keySlider].floatValue()
			else:
				globals()['axis%sValue' % (i + 1)] = sliderList[i].floatValue()

		tempInstance = GSInstance()
		tempInstance.name = "tempInstance"
		tempInstance.weightValue = axis1Value
		tempInstance.widthValue = axis2Value
		tempInstance.customValue = axis3Value
		tempInstance.setInterpolationCustom1_(axis4Value)
		tempInstance.setInterpolationCustom3_(axis6Value)
		tempInstance.setInterpolationCustom2_(axis5Value)
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

	# Toggle axis preview
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

	# generate nodes on canvas
	@objc.python_method
	def roundDotForPoint( self, thisPoint, markerWidth ):
		"""
		from Show Angled Handles by MekkaBlue
		Returns a circle with thisRadius around thisPoint.
		"""
		myRect = NSRect( ( thisPoint.x - markerWidth * 0.5, thisPoint.y - markerWidth * 0.5 ), ( markerWidth, markerWidth ) )
		return NSBezierPath.bezierPathWithOvalInRect_(myRect)

	# If nodes are stacked calculate using the next node
	@objc.python_method
	def getDelta(self, node, node2, previous):
		if previous == True:
			previous = True
			dx = node.x - node2.x
			dy = node.y - node2.y
			node3 = node.parent.nodes[(node2.index - 1)]
		else:
			previous = False
			dx = node2.x - node.x
			dy = node2.y - node.y
			node3 = node.parent.nodes[(node2.index + 1)]

		if dy == 0.0 and dx == 0.0:
			return self.getDelta(node, node3, previous)
		else:
			return [dx, dy]

	# Node color changes based on angle (change the 'angleTolerance' variable)
	@objc.python_method
	def nodeColor(self, nodePrev, node, nodeNext):
		deltaPrev = self.getDelta(node, nodePrev, True)
		deltaNext = self.getDelta(node, nodeNext, False)

		dx1 = deltaPrev[0]
		dy1 = deltaPrev[1]

		dx2 = deltaNext[0] 
		dy2 = deltaNext[1]

		angle1 = math.degrees(math.atan2(dy1, dx1))
		angle2 = math.degrees(math.atan2(dy2, dx2))
		diff = abs(angle2 - angle1)

		# Ensure angle is relative
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
		# return (1.0, 1.0)


# Start sync layers defs ———————————————————————————————————————————————————————————————————————
	# These functions are currently not being used...too slow
	# TODO: make currentGlyph a class variable rather than a local one
	# TODO: find a way to keep HOI layers in sync
	@objc.python_method
	def getFullName(self, layerName):
		currentGlyph = Glyphs.font.selectedLayers[0].parent

		for layer in currentGlyph.layers:
			if re.match(layerName + ".*}$", layer.name):
				return layer.name

	# Sync everything to the primary control masters V2
	# needs to work with more paths*****
	@objc.python_method
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
	@objc.python_method
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

	# TODO: Preview axis should have separate checkboxes than syncing axes
	# TODO: Preview should be based on the min and max value of each axis
	@objc.python_method
	def showAll(self, layer, currentGlyphName, pathIndex, interpolatedIndex, nodeScale, futureFontLayer):
		x2 = futureFontLayer.paths[pathIndex].nodes[interpolatedIndex].x
		y2 = futureFontLayer.paths[pathIndex].nodes[interpolatedIndex].y

		ThisPoint = NSMakePoint(x2, y2)

		pNode = NSBezierPath.bezierPath()

		# Changes node color based on angle
		color = self.nodeColor(futureFontLayer.paths[pathIndex].nodes[interpolatedIndex - 1], 
							   futureFontLayer.paths[pathIndex].nodes[interpolatedIndex],
							   futureFontLayer.paths[pathIndex].nodes[interpolatedIndex + 1])
		NSColor.colorWithCalibratedRed_green_blue_alpha_(color[0] ,color[1] , 0.0, 0.45).set()

		# Line Viz
		# x1 = futureFontLayer.paths[pathIndex].nodes[interpolatedIndex - 1].x
		# y1 = futureFontLayer.paths[pathIndex].nodes[interpolatedIndex - 1].y
		# startPoint = NSMakePoint(x1, y1)
		# pNode.setLineWidth_(nodeScale)
		# pNode.moveToPoint_(startPoint)
		# pNode.lineToPoint_(ThisPoint)
		# pNode.stroke()

		# Node Viz
		pNode.appendBezierPath_( self.roundDotForPoint( ThisPoint, nodeScale) )
		pNode.fill()

	# MAYBE change this to background instead
	@objc.python_method
	def background(self, layer):
		print("Start BG Draw")
		start = time.time()
		currentGlyphName = layer.parent.name
		masterLayer = layer.parent.layers[layer.associatedMasterId]

		# MAYBE move these 2 'if' blockds into a method
		if self.font != Glyphs.font:
				self.setup = True

		if self.setup == True:
			self.font = Glyphs.font
			iterAxes = range(len(self.font.axes))
			self.makeAxisVariables(self.font, iterAxes)
			self.setAxisExtremes(self.font, iterAxes)
			self.setup = False

		# MAYBE move this to a method and store in a variable with all the relevant axes values
		startInstance = time.time()
		tempInstance = GSInstance()
		tempInstance.setFont_(self.font)
		tempInstance.name = "tempInstance"
		tempInstance.axes = [axis1Value, axis2Value, axis3Value, axis4Value, axis6Value, axis5Value + 1, axis5Value]

		tempFontLayer = tempInstance.interpolatedFontProxy.glyphs[currentGlyphName].layers[0]
		endInstance = time.time() - startInstance
		print("Copy + Update Instance Time:", endInstance)

		if self.showFuture == True:
			previewProxies = []

			futureTempInstance = tempInstance.copy()
			futureTempInstance.name = "futuretempInstance"

			preview = {"axis1": "axis1Val", "axis2": "axis2Val", "axis3": "axis3Val", "axis4": "axis4Val", "axis5": "axis5Val", "axis6": "axis6Val",
					   "axis1Val": axis1Value, "axis2Val": axis2Value, "axis3Val": axis3Value, "axis4Val": axis4Value, "axis5Val": axis5Value, "axis6Val": axis6Value,
					   "preview": 0.0}

			resolution = 20
			increment = 50.0

			# DONE: these should be set to axis#Values like the rest of them, and then choosing a preview axis will decide which ones become zero
			for i in range(len(self.font.axes)):
				if globals()['check%s' % (i + 1)] == True:
					axisString = 'axis%s' % (i + 1)
					previewMin = globals()['axis%sMin' % (i + 1)]
					# Sets up axis to reference the preview value
					preview.update({axisString: "preview"})
					increment = (globals()['axis%sMax' % (i + 1)] - globals()['axis%sMin' % (i + 1)]) / resolution

			# If this can be faster, then the range can be more to show smaller increments, or show more points at once
			print("Making Preview Proxies")
			startProxies = time.time()
			for i in range(resolution):
				try:
					plotPoint = previewMin + (i * increment)
					preview.update({"preview": plotPoint})
				except:
					print("No axis set to preview")

				futureTempInstance.weightValue = preview[preview["axis1"]]
				futureTempInstance.widthValue = preview[preview["axis2"]]
				futureTempInstance.customValue = preview[preview["axis3"]]
				futureTempInstance.setInterpolationCustom1_(preview[preview["axis4"]])
				futureTempInstance.setInterpolationCustom2_(preview[preview["axis5"]])
				futureTempInstance.setInterpolationCustom3_(preview[preview["axis6"]])

				# This is what slows things down
				futureFontLayer = futureTempInstance.interpolatedFontProxy.glyphs[currentGlyphName].layers[0]

				previewProxies.append(futureFontLayer)
			print("Finished Making Proxies", time.time() - startProxies)

		# TODO: find a way to implement this in the foreground draw nodes loop. Should make it slightly faster
		# def glyphPreview(self, masterLayer, pathIndex, node, tempFontLayer, tSub):
		# 	if node.type == "offcurve":
		# 		return

		# 	tx2 = tempFontLayer.paths[pathIndex].nodes[node.index].x
		# 	ty2 = tempFontLayer.paths[pathIndex].nodes[node.index].y

		# 	if node.type == "line":
		# 		tx1 = tempFontLayer.paths[pathIndex].nodes[node.index - 1].x
		# 		ty1 = tempFontLayer.paths[pathIndex].nodes[node.index - 1].y
		# 		tSub.moveToPoint_(NSMakePoint(tx1, ty1))

		# 		tSub.lineToPoint_(NSMakePoint(tx2, ty2))
		# 	else:
		# 		tx1 = tempFontLayer.paths[pathIndex].nodes[node.index - 3].x
		# 		ty1 = tempFontLayer.paths[pathIndex].nodes[node.index - 3].y
		# 		tSub.moveToPoint_(NSMakePoint(tx1, ty1))

		# 		cx1 = tempFontLayer.paths[pathIndex].nodes[node.index - 2].x
		# 		cy1 = tempFontLayer.paths[pathIndex].nodes[node.index - 2].y
		# 		cx2 = tempFontLayer.paths[pathIndex].nodes[node.index - 1].x
		# 		cy2 = tempFontLayer.paths[pathIndex].nodes[node.index - 1].y
		# 		tSub.curveToPoint_controlPoint1_controlPoint2_(NSMakePoint(tx2, ty2), NSMakePoint(cx1, cy1), NSMakePoint(cx2, cy2))

		# Draw glyph preview  ——————————————————————————————————————————————————————————————————————————————————————
		startVarPrev = time.time()
		pathIndex = 0
		t = NSBezierPath.bezierPath()

		# Move this to its own method?? parameters (self, tempFontLayer)
		for path in masterLayer.paths:
			cx1 = None
			cy1 = None
			cx2 = None
			cy2 = None
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
		endVarPrev = time.time()
		print("Draw Var Preview Time:", time.time() - startVarPrev)

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
		t = NSBezierPath.bezierPath()
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
							drawFuture = time.time()
							for proxy in previewProxies:
								self.showAll(layer, currentGlyphName, pathIndex, interpolatedIndex, nodeScale, proxy)
							print("Drew Future %s" % (time.time() - drawFuture))

						# FUTURE block ————————————————————————————————————————————————————————————

						ThisPoint = NSMakePoint(x2, y2)
						pNode = NSBezierPath.bezierPath()
						# (1) Adding code for showing nodes and changing color based on angle
						pNode.appendBezierPath_( self.roundDotForPoint( ThisPoint, nodeScale ) )

						# Changes node color based on angle
						color = self.nodeColor(tempFontLayer.paths[pathIndex].nodes[interpolatedIndex - 1],  tempFontLayer.paths[pathIndex].nodes[interpolatedIndex],  tempFontLayer.paths[pathIndex].nodes[interpolatedIndex + 1])

						# Changes node color based on angle
						NSColor.colorWithCalibratedRed_green_blue_alpha_(color[0] ,color[1] , 0.0, 1.00).set()
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
						drawFuture = time.time()
						for proxy in previewProxies:
							self.showAll(layer, currentGlyphName, pathIndex, interpolatedIndex, nodeScale, proxy)
						print("Drew Future %s" % (time.time() - drawFuture))

					# FUTURE block ————————————————————————————————————————————————————————————

					pNode = NSBezierPath.bezierPath()

					ThisPoint = NSMakePoint(x2, y2)

					# (1) Adding code for showing nodes and changing color based on angle
					pNode.appendBezierPath_( self.roundDotForPoint( ThisPoint, nodeScale ) )

					color = self.nodeColor(tempFontLayer.paths[pathIndex].nodes[interpolatedIndex - 1],  tempFontLayer.paths[pathIndex].nodes[interpolatedIndex],  tempFontLayer.paths[pathIndex].nodes[interpolatedIndex + 1])

					# Changes node color based on angle
					NSColor.colorWithCalibratedRed_green_blue_alpha_(color[0] ,color[1] , 0.0, 1.00).set()
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

		end = time.time()
		print(end - start)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
