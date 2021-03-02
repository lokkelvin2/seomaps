# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 17:06:51 2020

@author: Seo
"""


import os
import folium as fo
import folium.plugins as fop

import numpy as np

class SMaps:
    def __init__(self, tiles="http://localhost:8080/styles/osm_liberty/{z}/{x}/{y}.png"):
        self.tilesource = tiles
        self.map = fo.Map(tiles=self.tilesource,attr="OSM/OMT")
        self.htmlfile = "foliumplot.html"
        
        # let's standardise adding the mouse position, no harm here
        self.addMousePosition()
        
    def setHtmlFile(self,txt):
        self.htmlfile = txt
    
    def plot(self):
        self.map.save(self.htmlfile)
        os.system(self.htmlfile)
        
    def addLines(self, lines, popups=None, tooltips=None):
        '''
        Expects list of lines. Each line is a numpy array of Nx2, with col 0: lat, col 1: lon.
        '''
        
        for line in lines:
            fo.vector_layers.PolyLine(line, color='#ff0000', dash_array="5").add_to(self.map)
        
    def addMousePosition(self):
        fmtr = "function(num) {return L.Util.formatNum(num, 6) + ' º ';};"
        fop.MousePosition(position='topright', separator=' | ', prefix="Mouse:",
                      lat_formatter=fmtr, lng_formatter=fmtr).add_to(self.map)
        
    def addMarkers(self, points, popups=None, tooltips=None, coordTooltips=True, coordPopups=True):
        '''
        Expects list of points. Each point is a numpy array of length 2, with [lat, lon].
        '''
        
        # if the extras are none then they are all none
        if popups is None:
            popups = [None for i in points]
        if tooltips is None:
            tooltips = [None for i in points]
        
        for i in range(len(points)):
            point = points[i]
            
            if coordPopups:
                popup = "{:.6f}".format(point[0]) + ", " + "{:.6f}".format(point[1])
            else:
                popup = popups[i]
            if coordTooltips:
                tooltip = "{:.6f}".format(point[0]) + ", " + "{:.6f}".format(point[1])
            else:
                tooltip = tooltips[i]
                        
            fo.Marker(point, popup, tooltip).add_to(self.map)
        
if __name__ == "__main__":
    print("Running this as a test script!")
    smap = SMaps()
    
    print("Source of tiles is at " + smap.tilesource)
    
    # add some sample lines
    line1 = np.array([[2.0,103.0],
                      [1.0,102.0],
                      [2.0,101.0]])
    line2 = np.array([[5.0,103.0],
                      [4.0,102.0],
                      [5.0,101.0]])
    lines = [line1,line2]
    
    smap.addLines(lines)
    
    # add some markers
    point1 = np.array([1.350627, 103.944896])
    point2 = np.array([1.350991, 103.944896])
    points = [point1, point2]
    popups = ['Home', 'Across Home']
    tooltips = ['Home Tooltip', 'Across Home Tooltip']
    smap.addMarkers(points, popups, tooltips, coordTooltips=False, coordPopups=False)
    
    smap.plot()