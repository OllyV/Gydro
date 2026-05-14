

import numpy as np

class GeometryCalculationHelper:
    
    @staticmethod
    def geometryToPoints(iface, geom):
        dx = iface.mapCanvas().layers()[0].rasterUnitsPerPixelX()
        dist = np.arange(0, geom.length(), dx)
        pts = [geom.interpolate(d).asPoint() for d in dist]
        return pts
    
    @staticmethod
    def geometryToDepths(iface, geom):
        pts = GeometryCalculationHelper.geometryToPoints(iface, geom)
        provider = iface.activeLayer().dataProvider()
        depth = np.array([provider.sample(p, 1)[0] for p in pts])
        
        return depth
    
    @staticmethod
    def deepestPointOfGeometry(iface, geom):
        pts = GeometryCalculationHelper.geometryToPoints(iface, geom)
        provider = iface.activeLayer().dataProvider()

        depPoints  = [pts[0]]
        depthValue = provider.sample(pts[0], 1)[0]

        for p in pts:
            depth = provider.sample(p, 1)[0]
            if depth < depthValue:
                depPoints = [p]
                depthValue = depth
            elif depth == depthValue:
                depPoints.append(p)

        return depPoints[len(depPoints) // 2 - 1]
