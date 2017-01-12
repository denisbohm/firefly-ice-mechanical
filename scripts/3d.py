import rhinoscriptsyntax as rs

boardThickness = 1.6

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

    def ArcTo(self, a, b, xm, ym):
        p = (a, b, self.z)
        if p == self.currentPoint:
            return
        self.curves.append(rs.AddArc3Pt(self.currentPoint, p, (xm, ym, self.z)))
        self.currentPoint = p

    def Fillet(self, radius):
        curve0 = self.curves.pop()
        curve1 = self.curves.pop()
        curve = rs.AddFilletCurve(curve0, curve1, radius, self.currentPoint, self.currentPoint)
        rs.DeleteObject(curve0)
        rs.DeleteObject(curve1)
        self.curves.append(curve)

    def ClosePath(self):
        if self.currentPoint != self.firstPoint:
            self.curves.append(rs.AddLine(self.currentPoint, self.firstPoint))

    def Join(self):
        if len(self.curves) > 1:
            self.curves = rs.JoinCurves(self.curves, True)

def CreateRoundedRectangle(x0, y0, x1, y1, z0, r=0.5):
    if r == 0.0:
        path = PathXY()
        path.z = z0
        path.MoveTo(x0, y0)
        path.LineTo(x0, y1)
        path.LineTo(x1, y1)
        path.LineTo(x1, y0)
        path.ClosePath()
        path.Join()
        return path.curves[0]

    xa = x0 + r
    xz = x1 - r
    ya = y0 + r
    yz = y1 - r
    path = PathXY()
    path.z = z0
    path.MoveTo(x0, ya)
    path.LineTo(x0, yz)
    path.LineTo(x0, y1)
    path.LineTo(xa, y1)
    path.Fillet(r)
    path.LineTo(xz, y1)
    path.LineTo(x1, y1)
    path.LineTo(x1, yz)
    path.Fillet(r)
    path.LineTo(x1, ya)
    path.LineTo(x1, y0)
    path.LineTo(xz, y0)
    path.Fillet(r)
    path.LineTo(xa, y0)
    path.LineTo(x0, y0)
    path.LineTo(x0, ya)
    path.Fillet(r)
    path.Join()
    return path.curves[0]

def PlaceInstance(file, x, y, mirror, rotate):
    rs.Command("_-Insert _File=_Yes /Users/denis/sandbox/denisbohm/firefly-ice-mechanical/scripts/packages/" + file + ".3dm B 0,0,0 1 0 _Enter")
    objects = rs.SelectedObjects()
    if not len(objects):
        return None
    object = objects[0]
    rs.UnselectAllObjects()
    rs.RotateObject(object, (0, 0, 0), rotate)
    if mirror:
        rs.RotateObject(object, (0, 0, 0), 180, (0, 1, 0))
        rs.MoveObject(object, (0, 0, -boardThickness))
    rs.MoveObject(object, (x, y, 0))
    return object

def ColorAndMove(object, layer):
    index = rs.AddMaterialToObject(object)
    if layer == 1:
        rs.MaterialColor(index, (255, 0, 0))
    if layer == 16:
        rs.MaterialColor(index, (0, 0, 255))
        rs.MoveObject(object, (0, 0, -boardThickness - 0.1))

def PlaceCircle(x, y, radius, layer):
    if (layer != 1) and (layer != 16):
        return None
    object = rs.AddCylinder((x, y, 0), 0.1, radius)
    ColorAndMove(object, layer)
    return object

def PlaceSmd(x, y, w, h, r, layer):
    f = min(w, h) * r * 0.5
    curve = CreateRoundedRectangle(x - w / 2.0, y - h / 2.0, x + w / 2.0, y + h / 2.0, 0.0, f)
    extrusion = rs.ExtrudeCurveStraight(curve, (0, 0, 0), (0, 0, 0.1))
    top = rs.AddPlanarSrf([curve])
    bot = rs.CopyObject(top, (0, 0, 0.1))
    object = rs.JoinSurfaces([top, extrusion, bot], True)
    rs.DeleteObjects([curve])
    ColorAndMove(object, layer)
    return object

def PlacePad(x, y, w, h, r, layer):
    f = min(w, h) * r * 0.5
    curve = CreateRoundedRectangle(x - w / 2.0, y - h / 2.0, x + w / 2.0, y + h / 2.0, 0.0, f)
    extrusion = rs.ExtrudeCurveStraight(curve, (0, 0, 0), (0, 0, 0.1))
    top = rs.AddPlanarSrf([curve])
    bot = rs.CopyObject(top, (0, 0, 0.1))
    object = rs.JoinSurfaces([top, extrusion, bot], True)
    rs.DeleteObjects([curve])
    ColorAndMove(object, layer)
    return object

def PlaceRing(x, y, r0, r1, layer):
    if (layer != 1) and (layer != 16):
        return None
    c0 = rs.AddCircle((x, y, 0), r0)
    c1 = rs.AddCircle((x, y, 0), r1)
    e0 = rs.ExtrudeCurveStraight(c0, (0, 0, 0), (0, 0, 0.1))
    e1 = rs.ExtrudeCurveStraight(c1, (0, 0, 0), (0, 0, 0.1))
    curves = [c0, c1]
    top = rs.AddPlanarSrf(curves)
    bot = rs.CopyObject(top, (0, 0, 0.1))
    object = rs.JoinSurfaces([top, e0, e1, bot], True)
    rs.DeleteObjects(curves)
    ColorAndMove(object, layer)
    return object

def PlacePolygon(points, layer):
    if (layer != 1) and (layer != 16):
        return None
    path = PathXY()
    first = True
    for point in points:
        if first:
            first = False
            path.MoveTo(point[0], point[1])
            if len(point) >= 9:
                path.ArcTo(point[3], point[4], point[6], point[7])
        else:
            if len(point) >= 9:
                path.LineTo(point[0], point[1])
                path.ArcTo(point[3], point[4], point[6], point[7])
            else:
                path.LineTo(point[0], point[1])
    path.ClosePath()
    path.Join()
    curve = path.curves[0]
#    curve = rs.AddPolyline(points)
    extrusion = rs.ExtrudeCurveStraight(curve, (0, 0, 0), (0, 0, 0.1))
    top = rs.AddPlanarSrf([curve])
    bot = rs.CopyObject(top, (0, 0, 0.1))
    object = rs.JoinSurfaces([top, extrusion, bot], True)
    rs.DeleteObject(curve)
    ColorAndMove(object, layer)
    return object

def PlacePCB(curves):
    curves = rs.JoinCurves(curves, True)
    surface = rs.AddPlanarSrf(curves)
    other = rs.CopyObject(surface, (0, 0, -boardThickness))
    surfaces = [surface, other]
    for curve in curves:
        surfaces.append(rs.ExtrudeCurveStraight(curve, (0, 0, 0), (0, 0, -boardThickness)))
    rs.DeleteObjects(curves)
    surface = rs.JoinSurfaces(surfaces, True)
    index = rs.AddMaterialToObject(surface)
    rs.MaterialColor(index, (20, 150, 20))
    return surface

