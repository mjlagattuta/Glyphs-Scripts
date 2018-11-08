# Modifies control points of the selected path to match the speed of the two adjacent paths
# For use on cubic curves
import math

font = Glyphs.font

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
    
    
    
def getInterpolatedPoint(t, pathOne, pathTwo, startPercent, endPercent):    
    pointOne = GSNode()
    pointTwo = GSNode()
    pointThree = GSNode()
    
    pointOne.x = pointOnBezier(t, pathOne)[0]
    pointOne.y = pointOnBezier(t, pathOne)[1]
        
    pointTwo.x = pointOnBezier(t, pathTwo)[0]
    pointTwo.y = pointOnBezier(t, pathTwo)[1]
    
    thisDist = dist(pointOne, pointTwo)
    angle = math.atan2(pointTwo.y - pointOne.y, pointTwo.x - pointOne.x)
    
    thisPercent = startPercent + ((endPercent - startPercent) * t)
    
    pointThree.x = reverseDist((thisDist * thisPercent), angle)[0] + pointOne.x
    pointThree.y = reverseDist((thisDist * thisPercent), angle)[1] + pointOne.y
    
    return (pointThree.x, pointThree.y)
    


def dist(p0, p1):
    return math.sqrt((p0.x - p1.x)**2 + (p0.y - p1.y)**2)
    
    
    
def reverseDist(distance, angle):
    x = distance * math.cos(angle)
    y = distance * math.sin(angle)
    return (x, y)
    
    
    
def getPolyline(path, resolution):
    points = []
    for i in range(resolution + 1):
        t = i / float(resolution)
    
        point = pointOnBezier(t, path)
    
        points.append(point)
    return points
    
    
    
def calcPolyline(pathOne, pathTwo, pathThree, resolution):
    points = []
    
    oneStart = pathOne.nodes[0]
    oneEnd = pathOne.nodes[-1]
    
    twoStart = pathTwo.nodes[0]
    twoEnd = pathTwo.nodes[-1]
    
    threeStart = pathThree.nodes[0]
    threeEnd = pathThree.nodes[-1]
    
    startPercent = dist(oneStart, threeStart) / dist(oneStart, twoStart)
    endPercent = dist(oneEnd, threeEnd) / dist(oneEnd, twoEnd)
    
    points.append((threeStart.x, threeStart.y))
    
    for i in range(resolution - 1):
        t = (i + 1) / float(resolution)
    
        point = getInterpolatedPoint(t, pathOne, pathTwo, startPercent, endPercent)
    
        points.append(point)

    points.append((threeEnd.x, threeEnd.y))
    
    return points
    
    
    
def moveHandles(points):
    xLen = (points[-1][0] - points[0][0])
    xMid = (points[0][0] + points[-1][0]) / 2
    xBez25 = points[1][0]
    xBez50 = points[2][0]
    xBez75 = points[3][0]
    
    yLen = (points[-1][1] - points[0][1])
    yMid = (points[0][1] + points[-1][1]) / 2
    yBez25 = points[1][1]
    yBez50 = points[2][1]
    yBez75 = points[3][1]
    
    xCalc = round(xMid - (1.333 * (xMid - xBez50)))
    yCalc = round(yMid - (1.333 * (yMid - yBez50)))
        
    xCalc1 = (    xCalc - ( ( (xLen / 3.0) + 3.555 * ((xBez75 - xBez25) - (xLen / 2.0)) ) / 2)    )
    yCalc1 = (    yCalc - ( ( (yLen / 3.0) + 3.555 * ((yBez75 - yBez25) - (yLen / 2.0)) ) / 2)    )
        
    xCalc2 = (    xCalc + ( ( (xLen / 3.0) + 3.555 * ((xBez75 - xBez25) - (xLen / 2.0)) ) / 2)    )
    yCalc2 = (    yCalc + ( ( (yLen / 3.0) + 3.555 * ((yBez75 - yBez25) - (yLen / 2.0)) ) / 2)    )
    
    return [(xCalc1, yCalc1), (xCalc2, yCalc2)]

    
def tuneCurve(path, currentPolyline, plottedPolyline, count):
    deltas = []
    if len(currentPolyline) != len(plottedPolyline):
        print "ERROR polylines are not of the same resolution"
    else:
        for i in range(len(currentPolyline)):
            xDelta = currentPolyline[i][0] - plottedPolyline[i][0]
            yDelta = currentPolyline[i][1] - plottedPolyline[i][1]
            
            deltas.append((xDelta, yDelta))
    
    xAvg = 0.0
    yAvg = 0.0
    
    for delta in deltas:
        xAvg = xAvg + delta[0]
        yAvg = yAvg + delta[1]
    
    xAvg = xAvg / float(len(deltas))
    yAvg = yAvg / float(len(deltas))
    
    if abs(xAvg) < 0.2 and abs(yAvg) < 0.2:
        print "Average Deviation Below 0.2: %f,  %f" % (xAvg, yAvg)
    else:
        if count < 100:         
            path.nodes[1].x = path.nodes[1].x - round(xAvg)
            path.nodes[1].y = path.nodes[1].y - round(yAvg)
            path.nodes[2].x = path.nodes[2].x - round(xAvg)
            path.nodes[2].y = path.nodes[2].y - round(yAvg)
            
            count = count + 1
        
            currentPolyline = getPolyline(path, 40)
            tuneCurve(path, currentPolyline, plottedPolyline, count)
        else:
            print "Maximum adjustment depth reached  |  Average deviation: %f, %f" % (xAvg, yAvg)
            
            
    
def main():
    i = 0
    for path in Font.selectedLayers[0].paths:
        if path.selected == True:
            pathThree = path
            break
        else:
            i = i + 1
            
    try:
        pathThree = pathThree
    except:
        print "No path selected"
        return
            
    pathOne = Font.selectedLayers[0].paths[i - 1]
    pathTwo = Font.selectedLayers[0].paths[i + 1]
    
    handleArray = moveHandles(calcPolyline(pathOne, pathTwo, pathThree, 4))
    
    pathThree.nodes[1].x = handleArray[0][0]
    pathThree.nodes[1].y = handleArray[0][1]
    pathThree.nodes[2].x = handleArray[1][0]
    pathThree.nodes[2].y = handleArray[1][1]
    
    count = 0
    
    tuneCurve(pathThree, getPolyline(pathThree, 40), calcPolyline(pathOne, pathTwo, pathThree, 40), count)
    

#——————————————— End Defs ———————————————


    
main()
    
