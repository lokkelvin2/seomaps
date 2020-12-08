# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 17:06:51 2020

@author: Seo
"""


import os
import folium as fo
import numpy as np

class SMaps:
    def __init__(self, tiles="http://localhost:8080/styles/osm_liberty/{z}/{x}/{y}.png"):
        self.tilesource = tiles
        self.map = fo.Map(tiles=self.tilesource,attr="OSM/OMT")
        self.htmlfile = "foliumplot.html"
        
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
    
    smap.plot()