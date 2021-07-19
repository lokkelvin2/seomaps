# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 17:06:51 2020

@author: Seo
"""


import os
import folium as fo
import folium.plugins as fop
import re
import bs4
from foliumpatch import LayerControlJS
import numpy as np

class SMaps:
    def __init__(self, tiles="http://localhost:8080/styles/osm_liberty/{z}/{x}/{y}.png"):
        
        # first we repoint to local sources
        self.setLocalScripts()
        
        # init the rest
        self.tilesource = tiles
        self.map = fo.Map(tiles=self.tilesource,attr="OSM/OMT")
        self.htmlfile = "foliumplot.html"
        
        # let's standardise adding the mouse position, no harm here
        self.addMousePosition()
        
        # add some holders for feature groups?
        self.antPathLayers = []
        
        # add indices for geojsons
        self.geojsonIdx = 0
        self.gjIdxForMouseover = []
        
    def setLocalScripts(self):
        '''One method to set all of them locally.'''
        
        for i in range(len(fo.folium._default_js)):
            if fo.folium._default_js[i][0] == 'leaflet':
                fo.folium._default_js[i] = ('leaflet', './Leaflet/dist/leaflet.js')
            elif fo.folium._default_js[i][0] == 'awesome_markers':
                fo.folium._default_js[i] = ('awesome_markers', './Leaflet.awesome-markers/dist/leaflet.awesome-markers.js')
            elif fo.folium._default_js[i][0] == 'jquery':
                fo.folium._default_js[i] = ('jquery', './jquery/dist/jquery.min.js')
            elif fo.folium._default_js[i][0] == 'bootstrap':
                fo.folium._default_js[i] = ('bootstrap', './bootstrap/dist/js/bootstrap.min.js')
            
        for i in range(len(fo.folium._default_css)):
            if fo.folium._default_css[i][0] == 'leaflet_css':
                fo.folium._default_css[i] = ('leaflet_css', './Leaflet/dist/leaflet.css')
            elif fo.folium._default_css[i][0] == 'awesome_markers_css':
                fo.folium._default_css[i] = ('awesome_markers_css', './Leaflet.awesome-markers/dist/leaflet.awesome-markers.css')
            elif fo.folium._default_css[i][0] == 'awesome_markers_font_css':
                fo.folium._default_css[i] = ('awesome_markers_font_css', './Font-Awesome/css/font-awesome.min.css')
            elif fo.folium._default_css[i][0] == 'bootstrap_css':
                fo.folium._default_css[i] = ('bootstrap_css', './bootstrap/dist/css/bootstrap.min.css')
            elif fo.folium._default_css[i][0] == 'bootstrap_theme_css':
                fo.folium._default_css[i] = ('bootstrap_theme_css', './bootstrap/dist/css/bootstrap-theme.min.css')
            elif fo.folium._default_css[i][0] == 'awesome_rotate_css':
                fo.folium._default_css[i] = ('awesome_rotate_css', './folium/folium/templates/leaflet.awesome.rotate.css')
        
    def setHtmlFile(self,txt):
        self.htmlfile = txt
    
    def replaceLocalPlugins(self):
        '''Since it's so difficult to replace the js/css for plugins, just going to directly edit the html.'''
        
        # load the file
        f = open(self.htmlfile, "r")
        lines = f.readlines()
        f.close()
        
        for i in range(len(lines)):
            line = lines[i]
            
            # mousePosition
            if re.search('MousePosition.min.js', line) is not None or re.search('MousePosition.js', line) is not None:
                lines[i] = re.sub('<script src=.+?>', '<script src="./Leaflet.MousePosition/src/L.Control.MousePosition.js">', line)
            elif re.search('MousePosition.min.css', line) is not None or re.search('MousePosition.css', line) is not None:
                lines[i] = re.sub('href=".+?"', 'href="./Leaflet.MousePosition/src/L.Control.MousePosition.css"', line)
            elif re.search('leaflet-ant-path', line) is not None:
                lines[i] = re.sub('<script src=.+?>', '<script src="./unpkg_modules/leaflet-ant-path-1.1.2.js">', line)
            elif re.search('leaflet-measure.+?js', line) is not None:
                lines[i] = re.sub('<script src=.+?>', '<script src="./unpkg_modules/leaflet-measure-2.1.7.js">', line)
            elif re.search('leaflet-measure.+?css', line) is not None:
                lines[i] = re.sub('href=".+?"', 'href="./unpkg_modules/leaflet-measure-2.1.7.css"', line)
                
                
        
        # testing retrieval of labels
        gjptLabel = smap.retrieveGeoJsonLabel(lines,0)
        gjPolyLabel = smap.retrieveGeoJsonLabel(lines,1)
        
        
        
        # rewrite the file
        f = open(self.htmlfile, "w")
        f.writelines(lines)
        f.close()
        
    def plot(self, addMeasure=True):
        # add the layer control
        layer_control_obj = LayerControlJS()
        layer_control_obj.add_to(self.map)
        
        if addMeasure:
            fop.MeasureControl(position='topleft', primary_length_unit='meters', secondary_length_unit='kilometers', primary_area_unit='sqmeters').add_to(self.map)
        
        self.map.save(self.htmlfile)
        self.replaceLocalPlugins()
        # add fileloader
        self.addFileLoader(layer_control_obj) 
        # os.system(self.htmlfile)
        
    def addLines(self, lines, popups=None, tooltips=None):
        '''
        Expects list of lines. Each line is a numpy array of Nx2, with col 0: lat, col 1: lon.
        '''
        
        for line in lines:
            fo.vector_layers.PolyLine(line, color='#ff0000', dash_array="5").add_to(self.map)
                                      
    def addAntPaths(self, lines, popups=None, tooltips=None, labels=None):
        '''
        Expects list of lines. Each line is a numpy array of Nx2, with col 0: lat, col 1: lon.
        '''
        
        # if the extras are none then they are all none
        if popups is None:
            popups = [None for i in lines]
        if tooltips is None:
            tooltips = [None for i in lines]
        if labels is None:
            labels = ['Trajectory ' + str(i+1) for i in range(len(lines))]
        
        for i in range(len(lines)):
            line = lines[i]
            popup = popups[i]
            tooltip = tooltips[i]
            antpath = fop.AntPath(line, popup, tooltip)
            
            # make a new feature group
            fg = fo.FeatureGroup(labels[i])
            antpath.add_to(fg)
            self.antPathLayers.append(fg)
            
            # add the feature group to the map
            self.antPathLayers[-1].add_to(self.map)
            
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
            
            
            marker = fo.Marker(point.tolist(), popup, tooltip)
            marker.add_to(self.map)
    
    def buildGeoJsonFeaturePoint(self, point):
        revpt = list(point)
        revpt.reverse()
        
        gj = {'type': 'Feature'}
        gj['geometry'] = {'type': "Point", 'coordinates': revpt} # geojson is lon,lat
        gj['properties'] = {'geojsonIdx': self.geojsonIdx}
        self.geojsonIdx = self.geojsonIdx + 1
        
        return gj
        
    
    def addGeoJsonPoint(self, point):
        gj = self.buildGeoJsonFeaturePoint(point)
        
        fo.GeoJson(gj).add_to(self.map)
        
    def buildGeoJsonFeaturePolygon(self, vertices):
        revVert = np.flip(vertices, axis=1).tolist()
        
        gj = {'type': 'Feature'}
        gj['geometry'] = {'type': 'Polygon', 'coordinates': [revVert]} # for some reason geojson requires triple list
        gj['properties'] = {'geojsonIdx': self.geojsonIdx}
        self.geojsonIdx = self.geojsonIdx + 1
        
        return gj
        
    def addGeoJsonPolygon(self, vertices):
        gj = self.buildGeoJsonFeaturePolygon(vertices)
        
        fo.GeoJson(gj).add_to(self.map)
        
    def retrieveGeoJsonLabel(self,lines,idx):
        gjLabel = None
        
        for i in range(len(lines)):
            line = lines[i]
            
            if re.search('geojsonIdx.+?'+str(idx), line) is not None:
                rr = re.search('geo_json_.+_', line)
                gjLabel = rr.group()[9:-1]
                break
        
        return gjLabel
    
    def addPolygonMouseoverForPoint(self, pointlabel, polylabel):
        '''
        mouseover: function(e) {
			geo_json_dd5411019a494db3b87c995304634410.addTo(map_29637f6b5aa54837b050253ea47f7a65);
		},
		mouseout: function(e) {
			geo_json_dd5411019a494db3b87c995304634410.removeFrom(map_29637f6b5aa54837b050253ea47f7a65);
		}
        '''
    
    def addFileLoader(self,layer_control_obj):
        with open(self.htmlfile) as fp:
            soup = bs4.BeautifulSoup(fp, 'html.parser')
        # using HTML drag and drop DOM events https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API
        # using geojson-vt in L.vectorGrid.slicer because it is much faster
        # uses less javascript making code more portable
        soup.body.insert(len(soup.body)-1,bs4.BeautifulSoup("""<div id="DebugBox" style="position: absolute;bottom:0px;height:10%;width:100%;background-color: white; border-color: black; border-width:10px; padding:5px; opacity:0.9;overflow: auto"> <b>Debugging box </div>""",'html.parser'))
        minifiedjs = """var dropArea=document.getElementById('"""+self.map.get_name()+"""'),debugBox=document.getElementById("DebugBox");dropArea.ondragover=function(){return!1},dropArea.ondragend=function(){return!1},dropArea.ondrop=function(e){console.log("Dropped onto map");var r=new FileReader;r.readAsText(e.dataTransfer.files[0]),r.fileName=e.dataTransfer.files[0].name.toString(),debugBox.innerHTML+="<br/>",debugBox.innerHTML+="<br/>Loading... "+e.dataTransfer.files[0].name.toString();var t=(new Date).getTime();return r.onload=function(e){var r,n,o=(new Date).setTime((new Date).getTime()-t);debugBox.innerHTML+=" took "+o+"ms";try{var a;debugBox.innerHTML+="<br/>&nbsp;Parsing... "+(r=e.target.result.length,n=Math.floor(Math.log(r)/Math.log(1024)),Math.round(r/Math.pow(1024,n)*100)/100+" "+["B","kB","MB","GB"][n]),t=(new Date).getTime(),a=JSON.parse(e.target.result);var i=L.vectorGrid.slicer(a,{rendererFactory:L.canvas.tile,vectorTileLayerStyles:{sliced:function(e,r){return{fillColor:"red",fillOpacity:.2,stroke:!0,fill:!0,color:"red",opacity:1,weight:1} } },maxZoom:24,tolerance:3,extent:4096,buffer:64,debug:0,lineMetrics:!1,promoteId:null,generateId:!1,indexMaxZoom:5,indexMaxPoints:1e5}).addTo("""+self.map.get_name()+""");"""+layer_control_obj.get_name()+"_obj"+""".addOverlay(i,e.target.fileName),o=(new Date).setTime((new Date).getTime()-t),debugBox.innerHTML+=" took "+o+"ms"}catch(e){debugBox.innerHTML+="<br/>&nbsp;Error: "+e} },e.preventDefault(),!1};"""
        soup.find_all('script')[-1].append(minifiedjs)

        with open(self.htmlfile, 'w') as fp:
            fp.write(str(soup))
       
        
#%% Derived class for vector tiles
class SVecMaps(SMaps):
    def __init__(self, tiles="http://localhost:8080/data/v3/{z}/{x}/{y}.pbf"):
        super().__init__(tiles)
        
        self.htmlfile = "foliumplotvector.html"
        
    def convertProtobufLayer(self):
        # open the file (use beautifulsoup now!)
        with open(self.htmlfile) as fp:
            soup = bs4.BeautifulSoup(fp, 'html.parser')
        
        # insert the script for vector grid
        soup.head.append(soup.new_tag("script", src="./unpkg_modules/Leaflet.VectorGrid.bundled.min.js"))
        
        # insert patch script which includes the basic style and options
        soup.head.append(soup.new_tag("script", src="./vectorPatch.js"))
        
        # extract the main script
        mainscript = soup.find_all('script')[-1]
        # regex replace the tileLayer call to protobuf
        aa = re.sub("L.tileLayer\(", "L.vectorGrid.protobuf(", mainscript.contents[0]) # the \ in the pattern is required
        
        # now find the protobuf call again and replace the argument with the options object
        eidx = re.search('protobuf\(', aa).end()
        bb = aa[eidx:]
        r = re.search("\{.{20,}\}",bb)
        front = aa[:eidx+r.start()]
        back = aa[eidx+r.end():]
        final = front + "openmaptilesVectorTileOptions" + back
        
        # make a new tag and set the string
        newmainscript = soup.new_tag('script')
        newmainscript.string = final
        # replace the script
        mainscript.replace_with(newmainscript)

        # write back
        with open(self.htmlfile, 'w') as fp:
            fp.write(str(soup))
        
    # Remake the plot function
    def plot(self, addMeasure=True):
        # add the layer control
        layer_control_obj = LayerControlJS()
        layer_control_obj.add_to(self.map)
        
        if addMeasure:
            fop.MeasureControl(position='topleft', primary_length_unit='meters', secondary_length_unit='kilometers', primary_area_unit='sqmeters').add_to(self.map)
        
        self.map.save(self.htmlfile)
        self.replaceLocalPlugins()
        # Call the protobuf layer replacement instead
        self.convertProtobufLayer()
        # add fileloader
        self.addFileLoader(layer_control_obj) 
        # os.system(self.htmlfile)
   
#%%
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
    
    # add antpaths?
    antline1 = np.array([[1.315529, 103.875046],
                         [1.347760, 103.900075],
                         [1.399575, 103.875046]])

    smap.addAntPaths([antline1])
    
    # add a marker as a geojson instead now
    gjpt = np.array([1.334816, 103.697205])
    smap.addGeoJsonPoint(gjpt)
    
    # add a triangle
    gjvert = np.array([[gjpt[0] + 1e-2, gjpt[1] + 1e-2],
              [gjpt[0] - 1e-2, gjpt[1]],
              [gjpt[0], gjpt[1] - 1e-2],
              [gjpt[0] + 1e-2, gjpt[1] + 1e-2]])
    smap.addGeoJsonPolygon(gjvert)
    
    
    # smap.plot()
    
    ## test vector version
    svmap = SVecMaps()
    
    svmap.plot()