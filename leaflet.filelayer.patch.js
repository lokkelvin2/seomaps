// original http://github.com/makinacorpus/Leaflet.FileLayer
//
//
// modified to use geojson-vt in L.vectorGrid.slicer
//
(function (window){
    var FileLayerLoad = L.Control.extend({
        statics: {
            TITLE: 'Load local file (GeoJSON)',
            LABEL: '&#8965;' // projective U+2305
        },
        options: {
        },
        _map2 : null,
        _layer_control: null,
        _debugbox: null,

        initialize: function (map,layer_control,debugbox,options) {
            this._map2 = map; // Overwriting this._map leads to error 
            this._layer_control = layer_control;
            this._debugbox = debugbox;
            L.Util.setOptions(this, options);
        },

        onAdd: function (map) {
            this._map2 = map;
            return this._initContainer();
        },

        _initContainer: function () {
            var readfiles  = this._readFiles;
            var map = this._map2;
            var layer_control = this._layer_control;
            var debugbox = this._debugbox;
            // Create a button, and bind click on hidden file input
            var fileInput;
            var zoomName = 'leaflet-control-filelayer leaflet-control-zoom';
            var barName = 'leaflet-bar';
            var partName = barName + '-part';
            var container = L.DomUtil.create('div', zoomName + ' ' + barName);
            var link = L.DomUtil.create('a', zoomName + '-in ' + partName, container);
            link.innerHTML = L.Control.FileLayerLoad.LABEL;
            link.href = '#';
            link.title = L.Control.FileLayerLoad.TITLE;

            // Create an invisible file input
            fileInput = L.DomUtil.create('input', 'hidden', container);
            fileInput.type = 'file';
            fileInput.multiple = 'multiple';
            fileInput.accept = '.geojson';
            fileInput.style.display = 'none';
            // Load on file change
            fileInput.addEventListener('change', function () {
                readfiles(this.files,map,layer_control,debugbox);
                // reset so that the user can upload the same file again if they want to
                this.value = '';
            }, false);

            L.DomEvent.disableClickPropagation(container);
            L.DomEvent.on(link, 'click', function (e) {
                fileInput.click();
                e.preventDefault();
            });
            return container;
        },

        _readFiles: function(files,map,layer_control,debugbox){

            function humanFileSize(size) {
            var i = Math.floor(Math.log(size) / Math.log(1024));
            return Math.round(100 * (size / Math.pow(1024, i))) / 100 + ' ' + ['B', 'kB', 'MB', 'GB'][i];
            }
            // console.log('Dropped onto map')
            var reader = new FileReader();

            reader.readAsText(files[0]);
            reader.fileName = files[0].name.toString();
            reader.map = map;
            reader.layer_control = layer_control;
            debugbox.innerHTML += "<br/>";
            debugbox.innerHTML += "<br/>Loading... " + files[0].name.toString();
            var start = new Date().getTime();
            reader.onload = (function(thefile){
                return function (event) {
                    var elapsed = new Date().setTime(new Date().getTime() - start);
                    debugbox.innerHTML += " took " + elapsed + "ms";
                    try {
                        debugbox.innerHTML += "<br/>&nbsp;Parsing... " + humanFileSize(event.target.result.length);
                        start = new Date().getTime();
                        var data;
                        data = JSON.parse(event.target.result);
                        var vectorGridGeojsonvt = L.vectorGrid.slicer(data, {
                            rendererFactory: L.svg.tile,
                            vectorTileLayerStyles: {
                                sliced: function(properties, zoom) {
                                    return {
                                        fillColor: 'red',
                                        fillOpacity: 0.2,
                                        stroke: true,
                                        fill: true,
                                        color: 'red',
                                        opacity: 1.0,
                                        weight: 1,
                                    };
                                },
                            },
                            // geojson-vt options
                            maxZoom: 24,  // max zoom to preserve detail on; can't be higher than 24
                            tolerance: 3, // simplification tolerance (higher means simpler)
                            extent: 4096, // tile extent (both width and height)
                            buffer: 64,   // tile buffer on each side
                            debug: 0,     // logging level (0 to disable, 1 or 2)
                            lineMetrics: false, // whether to enable line metrics tracking for LineString/MultiLineString features
                            promoteId: null,    // name of a feature property to promote to feature.id. Cannot be used with `generateId`
                            generateId: false,  // whether to generate feature ids. Cannot be used with `promoteId`
                            indexMaxZoom: 5,       // max zoom in the initial tile index
                            indexMaxPoints: 100000 // max number of points per tile in the index
                        }).addTo(event.target.map);
                        
                        
                        //add it to a control
                        event.target.layer_control.addOverlay(vectorGridGeojsonvt, event.target.fileName);
                        elapsed = new Date().setTime(new Date().getTime() - start);
                        debugbox.innerHTML += " took " + elapsed + "ms";

                    } catch (err) {
                        debugbox.innerHTML += "<br/>&nbsp;Error: " + err;
                    }


                };
            })();
        }
    });
    L.Control.FileLayerLoad = FileLayerLoad;
    L.Control.fileLayerLoad = function (map,layercontrol,options) {
        return new L.Control.FileLayerLoad(map,layercontrol,options);
    };
}(window));