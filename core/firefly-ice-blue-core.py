import rhinoscriptsyntax as rs
import math
from datetime import datetime

class PathXY:
    
    def __init__(self):
        self.firstPoint = None
        self.currentPoint = None
        self.curves = []
        self.z = 0
    
    def BeginPath(self):
        self.firstPoint = None
        self.currentPoint = None
        self.curves = []
    
    def MoveTo(self, a, b):
        self.currentPoint = (a, b, self.z)
        if self.firstPoint is None:
            self.firstPoint = self.currentPoint
    
    def LineTo(self, a, b):
        p = (a, b, self.z)
        if p == self.currentPoint:
            return
        self.curves.append(rs.AddLine(self.currentPoint, p))
        self.currentPoint = p
    
    def Fillet(self, radius):
        curve0 = self.curves.pop()
        curve1 = self.curves.pop()
        curve = rs.AddFilletCurve(curve0, curve1, radius, self.currentPoint, self.currentPoint)
        rs.DeleteObject(curve0)
        rs.DeleteObject(curve1)
        self.curves.append(curve)
    
    def ClosePath(self):
        self.curves.append(rs.AddLine(self.currentPoint, self.firstPoint))
    
    def Join(self):
        if len(self.curves) > 1:
            self.curves = rs.JoinCurves(self.curves, True)

class Path:

    def __init__(self):
        self.firstPoint = None
        self.currentPoint = None
        self.curves = []
        self.axis = ((0, 0, 0), (0, 0, 1))

    def BeginPath(self):
        self.firstPoint = None
        self.currentPoint = None
        self.curves = []
    
    def MoveTo(self, a, b):
        self.currentPoint = (a, 0, b)
        if self.firstPoint is None:
            self.firstPoint = self.currentPoint

    def LineTo(self, a, b):
        p = (a, 0, b)
        if p == self.currentPoint:
            return
        self.curves.append(rs.AddLine(self.currentPoint, p))
        self.currentPoint = p

    def Fillet(self, radius):
        curve0 = self.curves.pop()
        curve1 = self.curves.pop()
        curve = rs.AddFilletCurve(curve0, curve1, radius, self.currentPoint, self.currentPoint)
        rs.DeleteObject(curve0)
        rs.DeleteObject(curve1)
        self.curves.append(curve)

    def CutInFillet(self, radius):
        curve1 = self.curves.pop()
        curve0 = self.curves.pop()
        curve = rs.AddFilletCurve(curve0, curve1, radius, self.currentPoint, self.currentPoint)
        fillet = rs.CurveFilletPoints(curve0, curve1, radius)
        p0 = fillet[0]
        p1 = fillet[1]
        pc = fillet[2]
        self.curves.append(rs.AddLine(rs.CurveStartPoint(curve0), p0))
        self.curves.append(curve)
        self.curves.append(rs.AddLine(p1, rs.CurveEndPoint(curve1)))
        rs.DeleteObject(curve0)
        rs.DeleteObject(curve1)
    
    def ArcTo(self, a, b, r, s):
        p = (a, 0, b)
        if p == self.currentPoint:
            return
        self.curves.append(rs.AddArc3Pt(self.currentPoint, p, (r, 0, s)))
        self.currentPoint = p

    def ClosePath(self):
        self.curves.append(rs.AddLine(self.currentPoint, self.firstPoint))

    def Join(self):
        if len(self.curves) > 1:
            self.curves = rs.JoinCurves(self.curves, True)

    def Revolve(self):
        self.Join()
        curve = self.curves[0]
    	surface = rs.AddRevSrf(curve, self.axis)
    	rs.DeleteObject(curve)
        self.curves = []
        return surface

    def CreateCircularSurface(self, b, radius):
        plane = rs.MovePlane(rs.WorldXYPlane(), (0, 0, b))
        circle = rs.AddCircle(plane, radius)
        surface = rs.AddPlanarSrf([circle])
        rs.DeleteObject(circle)
        return surface

    def RevolveSolid(self, first=True, last=True):
        self.Join()
        surfaces = []
        curve = self.curves[0]
    	surfaces.append(rs.AddRevSrf(curve, self.axis))
    	rs.DeleteObject(curve)
        self.curves = []
        if first:
            surfaces.append(self.CreateCircularSurface(self.firstPoint[2], self.firstPoint[0]))
        if last:
            surfaces.append(self.CreateCircularSurface(self.currentPoint[2], self.currentPoint[0]))
        return rs.JoinSurfaces(surfaces, True)

class FireflyIceBlue:

    def __init__(self):
        self.coreInnerRadius = 18.4
        self.coreShellWidth = 1.1
        self.coreShellHeight = 7.05
        self.coreTopExtension = 0.7
        self.coreTopOverlap = 0.8
        self.coreSpacerLedgeWidth = 0.6
        self.coreSpacerLedgeHeight = 0.9
        self.coreSpacerOuterHeight = 0.8
        self.coreSpacerInnerHeight = 1.0
        self.coreSpacerHeight = 0.8;
        self.coreSpacerCapWidth = 2.2
        self.coreCoverSlopeDepth = 0.2
        self.coreCoverSlopeHeight = 0.3
        self.coreCoverSpace = 0.4
        self.coreCoverExtension = 0.5
        self.corePressNub = 0.2
        self.corePressDepth = 0.2
        self.corePressHeight = 0.5
        self.pcbTopClearance = 1.0
        self.pcbThickness = 0.9
        self.postHeight = 4.0
        self.postSupportRadius = 1.8
        self.postRadius = 0.8
        self.postMateInnerRadius = 0.5
        self.postMateOuterRadius = 1.2
        self.postPoints = [(11.557, 29.21), (22.479, 29.21), (13.716, 2.032)]
        self.ledPoints = [(2.7, 11.8), (2, 14.4), (1.8, 17), (2, 19.6), (2.7, 22.2), (17, 31.6)]
        self.alignmentAngles = [0, 135, 225]
        self.usbPcbEdge = 16.5
        self.usbLowerEdge = 0.45
        self.usbUpperEdge = 3.0
        self.batteryWidth = 20.7
        self.batteryHeight = 25.6
        self.batteryThickness = 3.2
        self.batterySwell = 0.4
        self.draftAngle = 1.5
        self.draftMinimumAngle = 1.5
        self.tolerance = 0.05
        self.fourPartDesign = False

        self.coreShell = None
        self.coreBack = None
        self.coreSpacer = None
        self.coreTop = None

        self.root = "/Users/denis/sandbox/denisbohm/firefly-ice-mechanical/core/"

    def CreateLayer(self, name, color, surface):
        rs.AddLayer(name, color)
        rs.ObjectLayer(surface, name)
        if not rs.IsPolysurfaceClosed(surface):
            rs.MessageBox(name + " is not a closed polysurface")

    def ImportObject(self, file):
        rs.Command("_-Insert _File=_Yes " + self.root + file + ".3dm B 0,0,0 1 0 _Enter")
        object = rs.SelectedObjects()[0]
        rs.UnselectAllObjects()
        object = rs.ExplodeBlockInstance(object)[0]
        return object

    def Cut(self, polysurface, holes):
        for hole in holes:
            new = rs.SplitBrep(polysurface, hole, True)
            polysurface = next(x for x in new if rs.IsPolysurface(x))
            for n in new:
                if n is not polysurface:
                    rs.DeleteObject(n)
        return rs.JoinSurfaces([polysurface] + holes, True)
    
    def SplitAndKeep(self, object, cutting, index, axis=1):
        objects = rs.SplitBrep(object, cutting, True)
        # sort split object parts by centroid y
        meta = [(i, rs.SurfaceAreaCentroid(objects[i])[0][axis]) for i in range(len(objects))]
        meta.sort(key=lambda iy: iy[1])
        # delete other parts
        try:
            exclusion = set(index)
        except TypeError:
            exclusion = set()
            exclusion.add(index)
        results = []
        for i in range(len(meta)):
            object = objects[meta[i][0]]
            if i not in exclusion:
                rs.DeleteObject(object)
            else:
                results.append(object)
        return results[0] if len(results) == 1 else results
    
    def SplitAndKeepLargest(self, object, cutting):
        objects = rs.SplitBrep(object, cutting, True)
        # sort split object parts by surface area
        meta = [(i, rs.SurfaceArea(objects[i])[0]) for i in range(len(objects))]
        meta.sort(key=lambda iy: iy[1])
        # delete other parts
        for i in range(len(meta) - 1):
            object = objects[meta[i][0]]
            rs.DeleteObject(object)
        return objects[meta[len(meta) - 1][0]]
    
    def Keep(self, curves, index, axis=1):
        meta = [(i, rs.CurveMidPoint(curves[i])[axis]) for i in range(len(curves))]
        meta.sort(key=lambda iy: iy[1])
        for i in range(len(meta)):
            if i != index:
                rs.DeleteObject(curves[meta[i][0]])
        return curves[meta[index][0]]

    def CreateKeyCurve(self, r, z0, d=0, close=False):
        a = 0.15 - d / r
        x = r * math.sin(a)
        y = r * math.cos(a)
        points = []
        # yr = 18.1
        yr = self.coreInnerRadius - self.coreSpacerLedgeWidth + 0.4
        points.append((-x, -y, z0))
        points.append((-1.5, -yr - d, z0))
        points.append((-0.8, -yr + 0.3 - d, z0))
        points.append((0.8, -yr + 0.3 - d, z0))
        points.append((1.5, -yr - d, z0))
        points.append((x, -y, z0))
        start_tangent = (y / r, -x / r, 0)
        end_tangent = (y / r, x / r, 0)
        degree = 3
        knotstyle = 0
        curve = rs.AddInterpCurve(points, degree, knotstyle, start_tangent, end_tangent)
        if close:
            arc = rs.AddArc3Pt((-x, -y, z0), (x, -y, z0), (0, -r, z0))
            curve = rs.JoinCurves([curve, arc], True)
        return curve
        
    def CreateKey(self, z0, z1):
        r = self.coreInnerRadius
        d = self.GetDraftDistance(z0, z1)
        curve0 = self.CreateKeyCurve(r, z0, d)
        curve1 = self.CreateKeyCurve(r, z1)
        surface = rs.AddLoftSrf([curve0, curve1])
        rs.DeleteObjects([curve0, curve1])
        curve0 = self.CreateKeyCurve(r, z0, d, True)
        top = rs.AddPlanarSrf([curve0])
        rs.DeleteObject(curve0)
        surface = rs.JoinSurfaces([surface, top], True)
        return surface
    
    def CreateKeyHole(self, z0, z1):
        r = self.coreInnerRadius - self.tolerance
        d = self.GetDraftDistance(z0, z1)
        curve0 = self.CreateKeyCurve(r, z0)
        curve1 = self.CreateKeyCurve(r - self.GetDraftDistance(z0, z1), z1, -d)
        surface = rs.AddLoftSrf([curve0, curve1])
        rs.DeleteObjects([curve0, curve1])
        return surface
    
    def CreateCoreShell(self):
        x1 = self.coreInnerRadius
        x0 = x1 - self.coreSpacerLedgeWidth
        x2 = x1 + self.corePressDepth
        x3 = x1 + self.coreCoverSlopeDepth
        x4 = x1 + self.coreShellWidth
        y0 = 0
        y1 = y0 + self.coreCoverSlopeHeight
        y2 = y1 + self.coreCoverSpace
        y3 = y2 + self.corePressHeight
        y5 = y0 + self.coreShellHeight
        y4 = y5 - self.coreSpacerLedgeHeight
        path = Path()
        path.MoveTo(x3, y0)
        path.LineTo(x4, y0)
        path.LineTo(x4 - self.GetDraftDistance(y0, y5), y5)
        path.CutInFillet(0.2)
        path.LineTo(x0, y5)
        path.CutInFillet(0.2)
        path.LineTo(x0, y4)
        path.LineTo(x1, y4)
        path.LineTo(x1, y3)
        path.LineTo(x2, y3)
        path.LineTo(x2, y2)
        path.LineTo(x1, y2)
        path.LineTo(x1, y1)
        path.ClosePath()
        polysurface = path.Revolve()
        
        # cut the press fit slots required for making molds
        curve = rs.AddLine((x2, 0, y0), (x2, 0, y2))
        cut1 = rs.AddRevSrf(curve, ((0, 0, 0), (0, 0, 1)), -15, 15)
    	rs.DeleteObject(curve)
        box = rs.BoundingBox(cut1)
        xa = box[0][0]
        ya = box[0][1]
        xb = box[3][0]
        yb = box[3][1]
        cut2 = rs.MirrorObject(cut1, (0, -1, 0), (0, 1, 0), True)
        side1 = self.CreateRect([(xa, ya, y0), (xa, ya, y2), (-xa, ya, y2), (-xa, ya, y0)])
        side1s = self.SplitAndKeep(side1, polysurface, [0, 2], 0)
        side2 = self.CreateRect([(xb, yb, y0), (xb, yb, y2), (-xb, yb, y2), (-xb, yb, y0)])
        side2s = self.SplitAndKeep(side2, polysurface, [0, 2], 0)
        cut1 = rs.JoinSurfaces([cut1, side1s[1], side2s[1]], True)
        cut2 = rs.JoinSurfaces([cut2, side1s[0], side2s[0]], True)
        polysurface = self.SplitAndKeep(polysurface, cut1, 0, 0)
        polysurface = self.SplitAndKeep(polysurface, cut2, 1, 0)
        polysurface = rs.JoinSurfaces([polysurface, cut1, cut2], True)

        # cut the USB opening
        zb = self.coreShellHeight - self.coreSpacerLedgeHeight - self.pcbTopClearance - self.pcbThickness
        usb = self.ImportObject("usb-opening")
        rs.MoveObject(usb, (0, 0, zb - 1.3))
        usb = self.SplitAndKeep(usb, polysurface, 1)
        polysurface = self.Cut(polysurface, [usb])

        # add "keyed" areas to shell for aligning spacer
        for a in self.alignmentAngles:
            key = self.CreateKey(y4 - self.coreSpacerInnerHeight, y4)
            rs.RotateObject(key, (0, 0, 0), a)
            polysurface = self.SplitAndKeepLargest(polysurface, key)
            polysurface = rs.JoinSurfaces([key, polysurface], True)

        self.coreShell = polysurface
        self.CreateLayer("shell", 0xff0000, self.coreShell)

    def CreateCurve(self, points):
        curves = []
        for i in range(len(points) - 1):
            curves.append(rs.AddLine(points[i], points[i + 1]))
        curves.append(rs.AddLine(points[len(points) - 1], points[0]))
        return rs.JoinCurves(curves, True)
    
    def CreateRect(self, points):
        curve = self.CreateCurve(points)
        rect = rs.AddPlanarSrf([curve])[0]
        rs.DeleteObject(curve)
        return rect
    
    def GetDraftDistance(self, z0, z1):
        return math.sin(self.draftAngle * (math.pi / 180)) * (z1 - z0)
    
    def GetDraftMinimumDistance(self, z0, z1):
        return math.sin(self.draftMinimumAngle * (math.pi / 180)) * (z1 - z0)
    
    def CreateLoftAndCap(self, curve0, curve1):
        sides = rs.AddLoftSrf([curve0, curve1])
        top = rs.AddPlanarSrf([curve1])
        surface = rs.JoinSurfaces([sides, top], True)
        rs.DeleteObjects([curve0, curve1])
        return surface

    def CreateRoundedRectangle(self, x0, y0, x1, y1, z0, r=0.5):
        xa = x0 - r
        xz = x1 + r
        ya = y0 + r
        yz = y1 - r
        path = PathXY()
        path.z = z0
        path.MoveTo(x0, y0)
        path.LineTo(x1, y0)
        path.LineTo(xz, y0)
        path.LineTo(xz, ya)
        path.Fillet(r)
        path.LineTo(xz, yz)
        path.LineTo(xz, y1)
        path.LineTo(x1, y1)
        path.Fillet(r)
        path.LineTo(x0, y1)
        path.LineTo(xa, y1)
        path.LineTo(xa, yz)
        path.Fillet(r)
        path.LineTo(xa, ya)
        path.LineTo(xa, y0)
        path.LineTo(x0, y0)
        path.Fillet(r)
        path.Join()
        return path.curves[0]
        
    def CreateRoundedRectangleCutUp(self, x0, y0, x1, y1, z0, z1):
        curve1 = self.CreateRoundedRectangle(x0, y0, x1, y1, z1)
        d = self.GetDraftDistance(z0, z1)
        curve0 = self.CreateRoundedRectangle(x0 - d, y0 - d, x1 + d, y1 + d, z0)
        return self.CreateLoftAndCap(curve0, curve1)

    def CreateRoundedRectangleCutDown(self, x0, y0, x1, y1, z0, z1):
        curve0 = self.CreateRoundedRectangle(x0, y0, x1, y1, z0)
        d = self.GetDraftDistance(z0, z1)
        curve1 = self.CreateRoundedRectangle(x0 - d, y0 - d, x1 + d, y1 + d, z1)
        return self.CreateLoftAndCap(curve1, curve0)
    
    def CreateRoundCutDown(self, x, y, r, z0, z1):
        curve0 = rs.AddCircle3Pt((x - r, y, z0), (x + r, y, z0), (x, y + r, z0))
        r0 = r + self.GetDraftDistance(z0, z1)
        curve1 = rs.AddCircle3Pt((x - r0, y, z1), (x + r0, y, z1), (x, y + r0, z1))
        return self.CreateLoftAndCap(curve1, curve0)

    def CreateArc(self, a0, a1, r0, r1, z0):
        aa = (a0 + a1) / 2
        pa = (r0 * math.cos(aa), r0 * math.sin(aa), z0)
        pb = (r1 * math.cos(aa), r1 * math.sin(aa), z0)
        p0 = (r0 * math.cos(a0), r0 * math.sin(a0), z0)
        p1 = (r0 * math.cos(a1), r0 * math.sin(a1), z0)
        p2 = (r1 * math.cos(a1), r1 * math.sin(a1), z0)
        p3 = (r1 * math.cos(a0), r1 * math.sin(a0), z0)
        return rs.JoinCurves([rs.AddArc3Pt(p0, p1, pa), rs.AddLine(p1, p2), rs.AddArc3Pt(p2, p3, pb), rs.AddLine(p3, p0)], True)
    
    def CreateSupportArc(self, a0, a1, r0, r1, z0, z1):
        curve0 = self.CreateArc(a0, a1, r0, r1, z0)
        d = self.GetDraftDistance(z0, z1)
        ad = d / r0
        curve1 = self.CreateArc(a0 + ad, a1 - ad, r0 + d, r1 - d, z1)
        return self.CreateLoftAndCap(curve0, curve1)

    def CreatePost(self):
        y0 = 0
        y1 = y0 - self.pcbTopClearance
        y2 = y1 - self.pcbThickness
        y4 = -self.postHeight
        y3 = y4 + 0.2
        
        x2 = self.postMateInnerRadius
        x1 = x2 - self.GetDraftMinimumDistance(y3, y2)
        x0 = x1 - 0.1
        x4 = self.postRadius
        x3 = x4 - self.GetDraftDistance(y2, y1)
        x6 = self.postSupportRadius
        x5 = x6 - self.GetDraftDistance(y1, y0)
        
        path = Path()
        path.MoveTo(x0, y4)
        path.LineTo(x1, y3)
        path.LineTo(x2, y2)
        path.LineTo(x3, y2)
        path.LineTo(x4, y1)
        path.LineTo(x5, y1)
        path.LineTo(x6, y0)
        post = path.Revolve()
        cap = path.CreateCircularSurface(y4, x0)
        return rs.JoinSurfaces([post, cap], True)
    
    def CreatePostHole(self):
        y0 = 0
        y2 = self.coreShellHeight - self.coreSpacerLedgeHeight - self.pcbTopClearance - self.pcbThickness - (self.coreCoverSlopeHeight + self.coreCoverSpace + self.corePressHeight)
        y1 = y2 - self.postHeight - 0.5 + self.pcbThickness + self.pcbTopClearance
        
        x1 = self.postMateInnerRadius + self.tolerance
        x0 = x1 - self.GetDraftMinimumDistance(y1, y2)
        x3 = self.postMateOuterRadius
        x2 = x3 - self.GetDraftDistance(y0, y2)
        
        path = Path()
        path.MoveTo(x0, y1)
        path.LineTo(x1, y2)
        path.LineTo(x2, y2)
        path.LineTo(x3, y0)
        post = path.Revolve()
        cap = path.CreateCircularSurface(y1, x0)
        return rs.JoinSurfaces([post, cap], True)

    def CreateCoreBack(self):
        tolerance = 0.06
        x0 = self.coreInnerRadius - tolerance
        xn = x0 + self.corePressNub
        x1 = x0 + self.corePressDepth
        x2 = x0 + self.coreCoverSlopeDepth
        xc = x2 - self.coreCoverExtension
        y1 = 0
        y0 = y1 - self.coreCoverExtension
        y2 = y1 + self.coreCoverSlopeHeight
        y3 = y2 + self.coreCoverSpace
        y6 = y3 + self.corePressHeight
        y4 = y3 + self.corePressNub
        y5 = y6 - self.corePressNub
        y7 = self.coreShellHeight - self.coreSpacerLedgeHeight - self.pcbTopClearance - self.pcbThickness
        y8 = y7 - self.postHeight - 0.1 + self.pcbThickness + self.pcbTopClearance
        path = Path()
        path.MoveTo(xc, y0)
        path.LineTo(x2, y0)
        path.LineTo(x2, y1)
        path.Fillet(self.coreCoverExtension)
        path.LineTo(x0, y2)
        path.LineTo(x0, y3)
        path.LineTo(xn, y3)
        path.LineTo(xn, y4)
        path.Fillet(self.corePressNub);
        path.LineTo(xn, y5)
        path.LineTo(xn, y6)
        path.LineTo(x0, y6)
        path.Fillet(self.corePressNub);
        polysurface = path.RevolveSolid()
        
        posts = []
        for point in self.postPoints:
            post = self.CreatePostHole()
            x = -17 + point[0]
            y = -17 + point[1]
            rs.MoveObject(post, (x, y, y6))
            posts.append(post)
        polysurface = self.Cut(polysurface, posts)
    
        xb = self.batteryHeight / 2
        yb = (self.postPoints[0][1] - 17) - self.postMateOuterRadius - 0.2
        xa = -xb
        ya = yb - self.batteryWidth
        inset = self.CreateRoundedRectangleCutDown(xa, ya, xb, yb, y7 - self.batteryThickness - self.batterySwell, y6)
        polysurface = self.Cut(polysurface, [inset])

        cap = self.ImportObject("usb-cap")
        rs.MoveObject(cap, (0, self.usbPcbEdge, y6))
        circle = rs.AddCircle3Pt((0, x0, y6), (-x0, 0, y6), (x0, 0, y6))
        tube = rs.ExtrudeCurveStraight(circle, (0, 0, y6), (0, 0, y7 + 0.45))
        rs.DeleteObject(circle)
        cap = self.SplitAndKeep(cap, tube, 0)
        ends = self.SplitAndKeep(tube, cap, [0, 3], 0)
        cap = rs.JoinSurfaces(ends + [cap], True)
        cap = self.SplitAndKeep(cap, polysurface, 4)
        z1 = y6
        z0 = z1 - 0.4
        b1 = self.CreateRoundCutDown(-2.4, self.usbPcbEdge - 0.9, 1.2, z0, z1)
        b2 = self.CreateRoundCutDown(2.4, self.usbPcbEdge - 0.9, 1.2, z0, z1)
        polysurface = self.Cut(polysurface, [cap, b1, b2])
        
        # supports to prevent squishing between top/spacer and back
        sections = [(-20, 20), (180 - 20, 180 + 20), (180 + 45, 180 + 65), (360 - 65, 360 - 45)]
        for section in sections:
            a0 = section[0] * math.pi / 180
            a1 = section[1] * math.pi / 180
            r1 = self.coreInnerRadius - tolerance
            r0 = r1 - 1.4
            support = self.CreateSupportArc(a0, a1, r0, r1, y6, y7)
            polysurface = self.Cut(polysurface, [support])

        self.coreBack = polysurface
        self.CreateLayer("back", 0x0000ff, self.coreBack)

    def CreateEdgeSupport(self, edge, circle):
        edgeParameters = []
        circleParameters = []
        intersections = rs.CurveCurveIntersection(edge, circle)
        for intersection in intersections:
            edgeParameters.append(intersection[5])
            circleParameters.append(intersection[7])
        edgeCurves = rs.SplitCurve(edge, edgeParameters, True)
        edge = self.Keep(edgeCurves, 1, 0)
        circleCurves = rs.SplitCurve(circle, circleParameters, True)
        arc = self.Keep(circleCurves, 2)
        return rs.JoinCurves([edge, arc], True)

    def CreateRadial(self, x0, x1, d, z):
        return rs.JoinCurves([
            rs.AddLine((x0, -d, z), (x1, -d, z)),
            rs.AddArc3Pt((x1, -d, z), (x1, d, z), (x1 + d, 0, z)),
            rs.AddLine((x1, d, z), (x0, d, z)),
            rs.AddArc3Pt((x0, d, z), (x0, -d, z), (x0 - d, 0, z))], True)

    def CreateRadialBar(self, a, r0, r1, w, z0, z1, cap=False):
        x0 = r0
        y0 = -w / 2
        x1 = r1
        y1 = w / 2
        r = w / 2
        d = self.GetDraftDistance(z0, z1)
        curve0 = self.CreateRadial(x0 + d, x1 - d, r - d, z0)
        curve1 = self.CreateRadial(x0, x1, r, z1)
        slot = rs.AddLoftSrf([curve0, curve1])
        if cap:
            slot = rs.JoinSurfaces([slot, rs.AddPlanarSrf([curve0])], True)
        rs.DeleteObjects([curve0, curve1])
        slot = rs.RotateObject(slot, (0, 0, 0), a, (0, 0, 1))
        return slot

    def CreateULine(self, x0, x1, y0, y1, z):
        r = 0.5
        sp4 = r - math.sin(math.pi / 4) * r
        return rs.JoinCurves([
            rs.AddLine((x0, y1, z), (x0, y0 + r, z)),
            rs.AddArc3Pt((x0, y0 + r, z), (x0 + r, y0, z), (x0 + sp4, y0 + sp4, z)),
            rs.AddLine((x0 + r, y0, z), (x1 - r, y0, z)),
            rs.AddArc3Pt((x1 - r, y0, z), (x1, y0 + r, z), (x1 - sp4, y0 + sp4, z)),
            rs.AddLine((x1, y0 + r, z), (x1, y1, z))],
            True)

    def CreateCoreSpacer(self):
        x2 = self.coreInnerRadius - self.tolerance
        x1 = x2 - self.coreSpacerLedgeWidth - self.coreTopOverlap
        x0 = x2 - self.coreSpacerCapWidth
        y1 = self.coreShellHeight - self.coreSpacerLedgeHeight
        y3 = y1 + self.coreSpacerOuterHeight
        y4 = y3 + self.coreTopExtension + self.coreSpacerLedgeHeight - self.coreSpacerOuterHeight
        y0 = y1 - self.coreSpacerInnerHeight
        y2 = y3 - self.coreSpacerHeight
        path = Path()
        path.MoveTo(x0, y2)
        path.LineTo(x0 + self.GetDraftDistance(y0, y2), y0)
        path.LineTo(x2, y0)
        path.LineTo(x2 - self.GetDraftDistance(y0, y1), y1)
        path.LineTo(x1, y1)
        path.LineTo(x1, y3)
        polysurface = path.RevolveSolid()

        if self.fourPartDesign:
            slots = []
            for i in range(4):
                a = 180 - 15 + 10 * i
                r = 17 - 1.8
                r0 = r - 0.8
                r1 = r + 0.8
                slot = self.CreateRadialBar(a, r0, r1, 0.8, y2, y3)
                slots.append(slot)
            polysurface = self.Cut(polysurface, slots)
            
            bumps = []
            for point in self.ledPoints:
                path = Path()
                path.MoveTo(0.4, y4)
                path.LineTo(0.7, y3)
                bump = path.RevolveSolid(True, False)
                x = -17 + point[0]
                y = -17 + point[1]
                rs.MoveObject(bump, (x, y, 0))
                bumps.append(bump)
            polysurface = self.Cut(polysurface, bumps)
        else:
            holes = []
            for point in self.ledPoints:
                path = Path()
                path.MoveTo(0.4, y3)
                path.LineTo(0.7, y2)
                hole = path.Revolve()
                x = -17 + point[0]
                y = -17 + point[1]
                rs.MoveObject(hole, (x, y, 0))
                holes.append(hole)
            polysurface = self.Cut(polysurface, holes)

            barriers = []
            for i in range(6):
                a = 180 - 25 + 10 * i
                r = 17 - 1.8
                r0 = r - (0.8 - self.tolerance)
                r1 = r + 1.3
                barrier = self.CreateRadialBar(a, r0, r1, 1.0, y2 - self.pcbTopClearance + 0.3, y2, True)
                barrier = self.SplitAndKeepLargest(barrier, polysurface)
                barriers.append(barrier)
            polysurface = self.Cut(polysurface, barriers)

        posts = []
        for point in self.postPoints:
            post = self.CreatePost()
            x = -17 + point[0]
            y = -17 + point[1]
            rs.MoveObject(post, (x, y, y2))
            if y < 0:
                post = self.SplitAndKeep(post, polysurface, 2)
            posts.append(post)
        polysurface = self.Cut(polysurface, posts)
    
        # shell alignment key holes
        for a in self.alignmentAngles:
            hole = self.CreateKeyHole(y0, y1)
            rs.RotateObject(hole, (0, 0, 0), a)
            polysurface = self.SplitAndKeepLargest(polysurface, hole)
            polysurface = rs.JoinSurfaces([polysurface, hole], True)
    
        # support ledge for USB connector
        z1 = y0
        z0 = y0 - self.pcbThickness + self.usbLowerEdge
        d = self.GetDraftDistance(z0, z1)
        r1 = x2
        r0 = r1 - d
        circle0 = rs.AddCircle3Pt((-r0, 0, z0), (r0, 0, z0), (0, r0, z0))
        edge0 = self.CreateULine(-6, +6, self.usbPcbEdge + d, self.usbPcbEdge + d + 3, z0)
        curve0 = self.CreateEdgeSupport(edge0, circle0)
        circle1 = rs.AddCircle3Pt((-r1, 0, z1), (r1, 0, z1), (0, r1, z1))
        edge1 = self.CreateULine(-6, +6, self.usbPcbEdge, self.usbPcbEdge + 3, z1)
        curve1 = self.CreateEdgeSupport(edge1, circle1)
        support = self.CreateLoftAndCap(curve1, curve0)
        polysurface = self.Cut(polysurface, [support])
    
        # antenna is 1.2 mm max height, make core-out for 0.2 mm
        x = 19.558 - 17
        y = 2.921 - 17
        xa = x - 4.3 / 2
        ya = y - 2.2 / 2
        xb = x + 4.3 / 2
        yb = y + 2.2 / 2
        inset = self.CreateRoundedRectangleCutUp(xa, ya, xb, yb, y2, y2 + 0.2)
        polysurface = self.Cut(polysurface, [inset])
    
        self.coreSpacer = polysurface
        self.CreateLayer("spacer", 0x00ff00, self.coreSpacer)

    def CreateCoreTop(self):
        x1 = self.coreInnerRadius - self.coreSpacerLedgeWidth - self.tolerance
        xm = x1 - self.coreTopOverlap
        x0 = x1 - self.coreTopExtension
        y0 = self.coreShellHeight - self.coreSpacerLedgeHeight + self.coreSpacerOuterHeight
        ym = y0 - self.coreSpacerOuterHeight
        y1 = self.coreShellHeight
        y2 = y1 + self.coreTopExtension
        path = Path()
        path.MoveTo(xm, y0)
        path.LineTo(xm, ym)
        path.LineTo(x1, ym)
        path.LineTo(x1, y1)
        path.LineTo(x1, y2)
        path.LineTo(x0, y2)
        path.Fillet(self.coreTopExtension)
        polysurface = path.RevolveSolid()
        
        if self.fourPartDesign:
            plugs = []
            for i in range(4):
                a = 180 - 15 + 10 * i
                r = 17 - 1.8
                r0 = r - (0.8 - self.tolerance)
                r1 = r + (0.8 - self.tolerance)
                plug = self.CreateRadialBar(a, r0, r1, 0.8 - 2 * self.tolerance, y0 - self.coreSpacerHeight - 0.6, y0, True)
                plugs.append(plug)
            polysurface = self.Cut(polysurface, plugs)
            
            holes = []
            for point in self.ledPoints:
                path = Path()
                path.MoveTo(0.4, y2)
                path.LineTo(0.7, y0)
                hole = path.Revolve()
                x = -17 + point[0]
                y = -17 + point[1]
                rs.MoveObject(hole, (x, y, 0))
                holes.append(hole)
            polysurface = self.Cut(polysurface, holes)

        self.coreSpacer = polysurface
        self.CreateLayer("top", 0xffffff, polysurface)

    def Width(self, object):
        box = rs.BoundingBox(object)
        p0 = box[0]
        p6 = box[6]
        return p6[0] - p0[0]
    
    def Create(self):
        now = datetime.now()
        rs.Notes("Firefly Ice Blue Core Revision 1.6 WIP " + now.strftime('%Y-%m-%d %H:%M:%S') + "\n" +
                 "\n" +
                 "Changes Since 1.5 WIP\n" +
                 "- bring clear down over the side of the spacer to reduce chance of separation\n" +
                 "\n" +
                 "Changes Since 1.4 WIP\n" +
                 "- added tolerance to post hole for post pin fit\n" +
                 "\n" +
                 "Changes Since 1.3 WIP\n" +
                 "- back to co-molded clear top and black spacer\n" +
                 "\n" +
                 "Changes Since 1.2 WIP\n" +
                 "- spacer is now clear and top is now colored\n" +
                 "- added light barriers between close LEDS\n" +
                 "\n" +
                 "Changes Since 1.1 WIP\n" +
                 "- start adding draft\n" +
                 "- add anti-squish supports to back\n" +
                 "- add core cutout for antenna clearance\n" +
                 "- increase size of USB opening for plug retention feature clearance\n" +
                 "- make shape of shell alignment key / hole millable\n")
        self.CreateCoreTop()
        self.CreateCoreSpacer()
        self.CreateCoreShell()
        self.CreateCoreBack()

if __name__ == '__main__':
    fireflyIceBlue = FireflyIceBlue()
    fireflyIceBlue.Create()
