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

class viewHOI(ReporterPlugin):
	sliderView = objc.IBOutlet()  # the dialog view (e.g., panel or window)
	slider = objc.IBOutlet()      # the slider placed inside the view
	button = objc.IBOutlet()
	italicValue = 0.0
	selection = []

	def settings(self):
		# Load .nib file next to plugin.py
		self.loadNib("sliderView", __file__)
		self.menuName = Glyphs.localize({'en': u'HOI Viewer', 'de': u'Mein Plugin'})
		self.generalContextMenus = [{'name': 'HOI Viewer', 'view': self.sliderView}]
		self.slider.setMinValue_(0.0)
		self.slider.setMaxValue_(1000.0)

	@objc.IBAction
	def slider_(self, sender):
		self.italicValue = self.slider.floatValue()

		layer = Glyphs.font.selectedLayers[0]
		currentGlyph = layer.parent.name

		tempInstance = layer.parent.parent.instances[0].copy()
		tempInstance.name = "tempInstance"
		tempInstance.weightValue = 84
		tempInstance.widthValue = 0
		tempInstance.customValue = self.italicValue
		tempInstance.setInterpolationCustom1_(self.italicValue)
		tempInstance.setInterpolationCustom2_(self.italicValue)
		tempInstance.setInterpolationCustom3_(1000)
		self.tempInstance = tempInstance
		
		Glyphs.redraw()

	@objc.IBAction
	def button_(self, sender):
		self.selection = []
		Glyphs.redraw()

		
	def foreground(self, layer):
		self.italicValue = self.slider.floatValue()

		tempInstance = layer.parent.parent.instances[0].copy()
		tempInstance.name = "tempInstance"
		tempInstance.weightValue = 84
		tempInstance.widthValue = 0
		tempInstance.customValue = self.italicValue
		tempInstance.setInterpolationCustom1_(self.italicValue)
		tempInstance.setInterpolationCustom2_(self.italicValue)
		tempInstance.setInterpolationCustom3_(1000)

		p = NSBezierPath.bezierPath()
		NSColor.blueColor().set()

		currentGlyph = layer.parent.name

		if self.selection == []:
			for node in layer.paths[0].nodes:
				if node.selected:
					interpolatedIndex = node.index
					self.selection.append(interpolatedIndex)

					try:
						x1 = x0
						y1 = y0
					except:
						x1 = tempInstance.interpolatedFontProxy.glyphs[currentGlyph].layers[0].paths[0].nodes[interpolatedIndex].x
						y1 = tempInstance.interpolatedFontProxy.glyphs[currentGlyph].layers[0].paths[0].nodes[interpolatedIndex].y

					x2 = tempInstance.interpolatedFontProxy.glyphs[currentGlyph].layers[0].paths[0].nodes[interpolatedIndex].x
					y2 = tempInstance.interpolatedFontProxy.glyphs[currentGlyph].layers[0].paths[0].nodes[interpolatedIndex].y

					p.moveToPoint_(NSMakePoint(x1, y1))
			 		p.lineToPoint_(NSMakePoint(x2, y2))
			 		p.stroke()

					x0 = x2
			 		y0 = y2
		else:
			for nodeIndex in self.selection:
				interpolatedIndex = nodeIndex
				try:
					x1 = x0
					y1 = y0
				except:
					x1 = tempInstance.interpolatedFontProxy.glyphs[currentGlyph].layers[0].paths[0].nodes[interpolatedIndex].x
					y1 = tempInstance.interpolatedFontProxy.glyphs[currentGlyph].layers[0].paths[0].nodes[interpolatedIndex].y

				x2 = tempInstance.interpolatedFontProxy.glyphs[currentGlyph].layers[0].paths[0].nodes[interpolatedIndex].x
				y2 = tempInstance.interpolatedFontProxy.glyphs[currentGlyph].layers[0].paths[0].nodes[interpolatedIndex].y

				p.moveToPoint_(NSMakePoint(x1, y1))
		 		p.lineToPoint_(NSMakePoint(x2, y2))
		 		p.stroke()

				x0 = x2
		 		y0 = y2

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
	
	def doSomething(self):
		print 'Just did something'
		
	def conditionalContextMenus(self):

		# Empty list of context menu items
		contextMenus = []

		# Execute only if layers are actually selected
		if Glyphs.font.selectedLayers:
			layer = Glyphs.font.selectedLayers[0]
			
			# Exactly one object is selected and it’s an anchor
			if len(layer.selection) == 1 and type(layer.selection[0]) == GSAnchor:
					
				# Add context menu item
				contextMenus.append({'name': Glyphs.localize({'en': u'Do something else', 'de': u'Tu etwas anderes'}), 'action': self.doSomethingElse})

		# Return list of context menu items
		return contextMenus

	def doSomethingElse(self):
		print 'Just did something else'

	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
