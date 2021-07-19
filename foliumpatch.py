from jinja2 import Template
from folium.map import LayerControl

class LayerControlJS(LayerControl):
    '''
    Patch folium's LayerControl to add a javascript object handle to L.control.layers;
    Object handle used in SMaps.addFileLoader;
    '''

    _template = Template("""
        {% macro script(this,kwargs) %}
            var {{ this.get_name() }} = {
                base_layers : {
                    {%- for key, val in this.base_layers.items() %}
                    {{ key|tojson }} : {{val}},
                    {%- endfor %}
                },
                overlays :  {
                    {%- for key, val in this.overlays.items() %}
                    {{ key|tojson }} : {{val}},
                    {%- endfor %}
                },
            };
            var {{ this.get_name() }}_obj = L.control.layers(
                {{ this.get_name() }}.base_layers,
                {{ this.get_name() }}.overlays,
                {{ this.options|tojson }}
            ).addTo({{this._parent.get_name()}});

            {%- for val in this.layers_untoggle.values() %}
            {{ val }}.remove();
            {%- endfor %}
        {% endmacro %}
        """)

    def __init__(self, position='topright', collapsed=True, autoZIndex=True,
                 **kwargs):
        super(LayerControlJS, self).__init__(position, collapsed, autoZIndex,
                 **kwargs)
        self._name = 'LayerControlJS'
        
