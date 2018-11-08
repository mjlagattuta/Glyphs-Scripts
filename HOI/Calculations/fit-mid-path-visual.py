# from __future__ import print_function
import math
from numpy import *

""" 
    An implementation of volkerps fit curve methods in glyphs app for visual fitting of curves based on a polyline
    https://github.com/volkerp/fitCurves
"""

# ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

# evaluates cubic bezier at t, return point
def q(ctrlPoly, t):
    return (1.0-t)**3 * ctrlPoly[0] + 3*(1.0-t)**2 * t * ctrlPoly[1] + 3*(1.0-t)* t**2 * ctrlPoly[2] + t**3 * ctrlPoly[3]


# evaluates cubic bezier first derivative at t, return point
def qprime(ctrlPoly, t):
    return 3*(1.0-t)**2 * (ctrlPoly[1]-ctrlPoly[0]) + 6*(1.0-t) * t * (ctrlPoly[2]-ctrlPoly[1]) + 3*t**2 * (ctrlPoly[3]-ctrlPoly[2])


# evaluates cubic bezier second derivative at t, return point
def qprimeprime(ctrlPoly, t):
    return 6*(1.0-t) * (ctrlPoly[2]-2*ctrlPoly[1]+ctrlPoly[0]) + 6*(t) * (ctrlPoly[3]-2*ctrlPoly[2]+ctrlPoly[1])


# ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————


# Fit one (ore more) Bezier curves to a set of points
def fitCurve(points, maxError):
    leftTangent = normalize(points[1] - points[0])
    rightTangent = normalize(points[-2] - points[-1])
    return fitCubic(points, leftTangent, rightTangent, maxError)


def fitCubic(points, leftTangent, rightTangent, error):
    # Use heuristic if region only has two points in it
    if (len(points) == 2):
        dist = linalg.norm(points[0] - points[1]) / 3.0
        bezCurve = [points[0], points[0] + leftTangent * dist, points[1] + rightTangent * dist, points[1]]
        return [bezCurve]

    # Parameterize points, and attempt to fit curve
    u = chordLengthParameterize(points)
    bezCurve = generateBezier(points, u, leftTangent, rightTangent)
    # Find max deviation of points to fitted curve
    maxError, splitPoint = computeMaxError(points, bezCurve, u)
    if maxError < error:
        return [bezCurve]

    # If error not too large, try some reparameterization and iteration
    if maxError < error**2:
        for i in range(20):
            uPrime = reparameterize(bezCurve, points, u)
            bezCurve = generateBezier(points, uPrime, leftTangent, rightTangent)
            maxError, splitPoint = computeMaxError(points, bezCurve, uPrime)
            if maxError < error:
                return [bezCurve]
            u = uPrime

    # Fitting failed -- split at max error point and fit recursively
    beziers = []
    centerTangent = normalize(points[splitPoint-1] - points[splitPoint+1])
    beziers += fitCubic(points[:splitPoint+1], leftTangent, centerTangent, error)
    beziers += fitCubic(points[splitPoint:], -centerTangent, rightTangent, error)

    return beziers


def generateBezier(points, parameters, leftTangent, rightTangent):
    bezCurve = [points[0], None, None, points[-1]]

    # compute the A's
    A = zeros((len(parameters), 2, 2))
    for i, u in enumerate(parameters):
        A[i][0] = leftTangent  * 3*(1-u)**2 * u
        A[i][1] = rightTangent * 3*(1-u)    * u**2

    # Create the C and X matrices
    C = zeros((2, 2))
    X = zeros(2)

    for i, (point, u) in enumerate(zip(points, parameters)):
        C[0][0] += dot(A[i][0], A[i][0])
        C[0][1] += dot(A[i][0], A[i][1])
        C[1][0] += dot(A[i][0], A[i][1])
        C[1][1] += dot(A[i][1], A[i][1])

        tmp = point - q([points[0], points[0], points[-1], points[-1]], u)

        X[0] += dot(A[i][0], tmp)
        X[1] += dot(A[i][1], tmp)

    # Compute the determinants of C and X
    det_C0_C1 = C[0][0] * C[1][1] - C[1][0] * C[0][1]
    det_C0_X  = C[0][0] * X[1] - C[1][0] * X[0]
    det_X_C1  = X[0] * C[1][1] - X[1] * C[0][1]

    # Finally, derive alpha values
    alpha_l = 0.0 if det_C0_C1 == 0 else det_X_C1 / det_C0_C1
    alpha_r = 0.0 if det_C0_C1 == 0 else det_C0_X / det_C0_C1

    # If alpha negative, use the Wu/Barsky heuristic (see text) */
    # (if alpha is 0, you get coincident control points that lead to
    # divide by zero in any subsequent NewtonRaphsonRootFind() call. */
    segLength = linalg.norm(points[0] - points[-1])
    epsilon = 1.0e-6 * segLength
    if alpha_l < epsilon or alpha_r < epsilon:
        # fall back on standard (probably inaccurate) formula, and subdivide further if needed.
        bezCurve[1] = bezCurve[0] + leftTangent * (segLength / 3.0)
        bezCurve[2] = bezCurve[3] + rightTangent * (segLength / 3.0)

    else:
        # First and last control points of the Bezier curve are
        # positioned exactly at the first and last data points
        # Control points 1 and 2 are positioned an alpha distance out
        # on the tangent vectors, left and right, respectively
        bezCurve[1] = bezCurve[0] + leftTangent * alpha_l
        bezCurve[2] = bezCurve[3] + rightTangent * alpha_r

    return bezCurve


def reparameterize(bezier, points, parameters):
    return [newtonRaphsonRootFind(bezier, point, u) for point, u in zip(points, parameters)]


def newtonRaphsonRootFind(bez, point, u):
    """
       Newton's root finding algorithm calculates f(x)=0 by reiterating
       x_n+1 = x_n - f(x_n)/f'(x_n)

       We are trying to find curve parameter u for some point p that minimizes
       the distance from that point to the curve. Distance point to curve is d=q(u)-p.
       At minimum distance the point is perpendicular to the curve.
       We are solving
       f = q(u)-p * q'(u) = 0
       with
       f' = q'(u) * q'(u) + q(u)-p * q''(u)

       gives
       u_n+1 = u_n - |q(u_n)-p * q'(u_n)| / |q'(u_n)**2 + q(u_n)-p * q''(u_n)|
    """
    d = q(bez, u)-point
    numerator = (d * qprime(bez, u)).sum()
    denominator = (qprime(bez, u)**2 + d * qprimeprime(bez, u)).sum()

    if denominator == 0.0:
        return u
    else:
        return u - numerator/denominator


def chordLengthParameterize(points):
    u = [0.0]
    for i in range(1, len(points)):
        u.append(u[i-1] + linalg.norm(points[i] - points[i-1]))

    for i, _ in enumerate(u):
        u[i] = u[i] / u[-1]

    return u


def computeMaxError(points, bez, parameters):
    maxDist = 0.0
    splitPoint = len(points)/2
    for i, (point, u) in enumerate(zip(points, parameters)):
        dist = linalg.norm(q(bez, u)-point)**2
        if dist > maxDist:
            maxDist = dist
            splitPoint = i

    return maxDist, splitPoint


def normalize(v):
    return v / linalg.norm(v)
    
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
    


def dist(p0, p1):
    return math.sqrt((p0.x - p1.x)**2 + (p0.y - p1.y)**2)
    
def reverseDist(distance, angle):
    x = distance * cos(angle)
    y = distance * sin(angle)
    return(x, y)
    
font = Glyphs.font

newPath = GSPath()
font.selectedLayers[0].paths.append(newPath)

firstStart = font.selectedLayers[0].paths[0].nodes[0]
firstEnd = font.selectedLayers[0].paths[0].nodes[3]

midStart = font.selectedLayers[0].paths[1].nodes[0]
midEnd = font.selectedLayers[0].paths[1].nodes[3]

lastStart = font.selectedLayers[0].paths[2].nodes[0]
lastEnd = font.selectedLayers[0].paths[2].nodes[3]

del font.selectedLayers[0].paths[1]

startPercent = dist(firstStart, midStart) / dist(firstStart, lastStart)
endPercent = dist(firstEnd, midEnd) / dist(firstEnd, lastEnd)

if startPercent > endPercent:
    minPercent = endPercent
else:
    minPercent = startPercent
    
points = []

for i in range(40 + 1):
        t = i / 40.0
        pointOne = GSNode()
        pointTwo = GSNode()
        pointOne.x = pointOnBezier(t, font.selectedLayers[0].paths[0])[0]
        pointOne.y = pointOnBezier(t, font.selectedLayers[0].paths[0])[1]
        
        pointTwo.x = pointOnBezier(t, font.selectedLayers[0].paths[1])[0]
        pointTwo.y = pointOnBezier(t, font.selectedLayers[0].paths[1])[1]
        
        fullDist = dist(pointOne, pointTwo)
        angle = math.atan2(pointTwo.y - pointOne.y, pointTwo.x - pointOne.x)
        thisPercent = startPercent + ((endPercent - startPercent) * t)
        
        
        pointMid = GSNode()
        pointMid.x = reverseDist((fullDist * thisPercent), angle)[0] + pointOne.x
        pointMid.y = reverseDist((fullDist * thisPercent), angle)[1] + pointOne.y
        
        points.append((pointMid.x, pointMid.y))
    
        # This draws the points
        font.selectedLayers[0].paths[2].nodes.append(pointMid)
        
        
xMid = (font.selectedLayers[0].paths[2].nodes[0].x + font.selectedLayers[0].paths[2].nodes[-1].x) / 2
yMid = (font.selectedLayers[0].paths[2].nodes[0].y + font.selectedLayers[0].paths[2].nodes[-1].y) / 2
xHandlePos = round(xMid - (1.333 * (xMid - font.selectedLayers[0].paths[2].nodes[2].x)))
yHandlePos =  round(yMid - (1.333 * (yMid - font.selectedLayers[0].paths[2].nodes[2].y)))



        
        
        
pointsFit = array([[p[0], p[1]] for p in points])


error = 0
while len(fitCurve(pointsFit, error)) > 1:
    error = error + 1
    
finalCurve = fitCurve(pointsFit, error)
    
print finalCurve

fittedPath = GSPath()
del font.selectedLayers[0].paths[2]
font.selectedLayers[0].paths.append(fittedPath)

fittedNode1 = GSNode()
fittedNode1.type = "line"
fittedNode1.x = finalCurve[0][0][0]
fittedNode1.y = finalCurve[0][0][1]

fittedNode2 = GSNode()
fittedNode2.type = "offcurve"
fittedNode2.x = finalCurve[0][1][0]
fittedNode2.y = finalCurve[0][1][1]

fittedNode3 = GSNode()
fittedNode3.type = "offcurve"
fittedNode3.x = finalCurve[0][2][0]
fittedNode3.y = finalCurve[0][2][1]

fittedNode4 = GSNode()
fittedNode4.type = "curve"
fittedNode4.x = finalCurve[0][3][0]
fittedNode4.y = finalCurve[0][3][1]

font.selectedLayers[0].paths[2].nodes.append(fittedNode1)
font.selectedLayers[0].paths[2].nodes.append(fittedNode2)
font.selectedLayers[0].paths[2].nodes.append(fittedNode3)
font.selectedLayers[0].paths[2].nodes.append(fittedNode4)

correctOrder = GSPath()
correctOrder.nodes.append(font.selectedLayers[0].paths[1].nodes[0])
correctOrder.nodes.append(font.selectedLayers[0].paths[1].nodes[1])
correctOrder.nodes.append(font.selectedLayers[0].paths[1].nodes[2])
correctOrder.nodes.append(font.selectedLayers[0].paths[1].nodes[3])
del font.selectedLayers[0].paths[1]
font.selectedLayers[0].paths.append(correctOrder)