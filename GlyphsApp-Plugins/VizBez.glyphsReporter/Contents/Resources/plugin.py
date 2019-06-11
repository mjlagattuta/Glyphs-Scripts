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
import math
from GlyphsApp import *
from GlyphsApp.plugins import *

class VizBez(ReporterPlugin):

	def settings(self):
		self.menuName = Glyphs.localize({'en': u'VizBez'})

	def roundDotForPoint(self, thisPoint, markerWidth):
		"""
		from Show Angled Handles by MekkaBlue
		Returns a circle with thisRadius around thisPoint.
		"""
		myRect = NSRect( ( thisPoint[0] - markerWidth * 0.5, thisPoint[1] - markerWidth * 0.5 ), ( markerWidth, markerWidth ) )
		return NSBezierPath.bezierPathWithOvalInRect_(myRect)


	def nodeColor(self, nodePrev, node, nodeNext, angleTolerance=1.0):
		def getDelta(node, node2, previous):
			if previous == True:
				dx = node[0] - node2[0]
				dy = node[1] - node2[1]
			else:
				dx = node2[0] - node[0]
				dy = node2[1] - node[1]

			return [dx, dy]


		deltaPrev = getDelta(node, nodePrev, True)
		deltaNext = getDelta(node, nodeNext, False)

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

		if diff >= (angleTolerance * 2):
			redValue = 1.0
			greenValue = 0.0
		elif diff < angleTolerance:
			redValue = (diff % angleTolerance) / angleTolerance
			greenValue = 1.0
		else:
			redValue = 1.0
			greenValue = 1.0 - ((diff % angleTolerance) / angleTolerance)

		return (redValue, greenValue)
	 
	def drawBezier(self, resolution, points, scale):
		def pointOnBezier(t, points):
			n = len(points) - 1

			def C(n, i):
				#      n!
				# —————————————
				# i! * (n - i)!
				def factorial(num):
					factor = 1
					for i in range (num, 0, -1):
						factor *= i
					return factor
				return factorial(n) / (factorial(i) * factorial(n - i))
				# return math.factorial(n) / (math.factorial(i) * math.factorial(n - i))

			# faster calculation for orders 1–5
			if n == 1:
				C0 = (1-t)
				C1 = t

				P0 = points[0]
				P1 = points[1]

				x = C0 * P0.x + C1 * P1.x
				y = C0 * P0.y + C1 * P1.y

				location = (x, y)
			elif n == 2:
				C0 = (1-t) * (1-t)
				C1 = 2 * (1-t) * t
				C2 = t * t

				P0 = points[0]
				P1 = points[1]
				P2 = points[2]

				x = C0 * P0.x + C1 * P1.x + C2 * P2.x
				y = C0 * P0.y + C1 * P1.y + C2 * P2.y

				location = (x, y)
			elif n == 3:
				C0 = (1-t) * (1-t) * (1-t)
				C1 = 3 * (1-t) * (1-t) * t
				C2 = 3 * (1-t) * t * t
				C3 = t * t * t
				
				P0 = points[0]
				P1 = points[1]
				P2 = points[2]
				P3 = points[3]

				x = C0 * P0.x + C1 * P1.x + C2 * P2.x + C3 * P3.x
				y = C0 * P0.y + C1 * P1.y + C2 * P2.y + C3 * P3.y

				location = (x, y)
			elif n == 4:
				C0 = (1-t) * (1-t) * (1-t) * (1-t)
				C1 = 4 * (1-t) * (1-t) * (1-t) * t
				C2 = 6 * (1-t) * (1-t) * t * t
				C3 = 4 * (1-t) * t * t * t
				C4 = t * t * t * t
				
				P0 = points[0]
				P1 = points[1]
				P2 = points[2]
				P3 = points[3]
				P4 = points[4]

				x = C0 * P0.x + C1 * P1.x + C2 * P2.x + C3 * P3.x + C4 * P4.x
				y = C0 * P0.y + C1 * P1.y + C2 * P2.y + C3 * P3.y + C4 * P4.y

				location = (x, y)

			elif n == 5:
				C0 = (1-t) * (1-t) * (1-t) * (1-t) * (1-t)
				C1 = 5 * (1-t) * (1-t) * (1-t) * (1-t) * t
				C2 = 10 * (1-t) * (1-t) * (1-t) * t * t
				C3 = 10 * (1-t) * (1-t) * t * t * t
				C4 = 5 * (1-t) * t * t * t * t
				C5 = t * t * t * t * t
				
				P0 = points[0]
				P1 = points[1]
				P2 = points[2]
				P3 = points[3]
				P4 = points[4]
				P5 = points[5]

				x = C0 * P0.x + C1 * P1.x + C2 * P2.x + C3 * P3.x + C4 * P4.x + C5 * P5.x
				y = C0 * P0.y + C1 * P1.y + C2 * P2.y + C3 * P3.y + C4 * P4.y + C5 * P5.y

				location = (x, y)
			else: # if order is greater than 4 then calculate constants
				x = 0
				y = 0
				for i in range(n + 1):
					Ci = C(n, i) * ((1 - t)**(n - i)) * (t**i)
					P = points[i]
					x += (Ci * P.x)
					y += (Ci * P.y)

				location = (x, y)

			return location

		p = NSBezierPath.bezierPath()
		p.moveToPoint_(points[0].position)

		steps = []

		for i in range(resolution + 1):
			t = (1.0 / resolution) * i
			point = pointOnBezier(t, points)
			p.lineToPoint_(point)
			steps.append(point)

		NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.0, 0.0, 1.0).set()
		p.setLineWidth_(1.2 / scale)
		p.stroke()
		return steps
		
	def background(self, layer):
		scale = Glyphs.font.currentTab.scale
		nodeScale = 8.0 / scale
		pathSteps = []
		angleTolerance = 0.1
		resolution = 10 + int(100.0 * scale)

		for path in layer.paths:
			# boundScale = (path.bounds.size.width + path.bounds.size.height) / 2000
			# resolution = 10 + int(100.0 * scale * boundScale)
			# print resolution
			points = []
			for node in path.nodes:
				points.append(node)
			pathSteps.append(self.drawBezier(resolution, points, scale))

		storeNodes = []

		for i in range(resolution + 1):
			l = NSBezierPath.bezierPath()
			for j in range(len(pathSteps)):
				point = pathSteps[j][i]
				if j == 0:
					l.moveToPoint_(point)
				else:
					l.lineToPoint_(point)
					if j < (len(pathSteps) - 1):
						n = NSBezierPath.bezierPath()
						color = self.nodeColor(pathSteps[j - 1][i], point, pathSteps[j + 1][i], angleTolerance=angleTolerance)
						print j, color
						n.appendBezierPath_(self.roundDotForPoint(point, nodeScale))
						storeNodes.append( (n, NSColor.colorWithCalibratedRed_green_blue_alpha_(color[0] ,color[1] , 0.0, 1.0)) )
			NSColor.colorWithCalibratedRed_green_blue_alpha_(0.0, 0.0, 1.0, 0.5).set()
			l.setLineWidth_(0.0)
			l.stroke()

		for node, color in storeNodes:
			color.set()
			node.fill()

	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
