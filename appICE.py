import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, no_update
import dash_leaflet as dl
import json
#Locales
import auxiliarLeafltet

from auxiliarJS import info, classes, colorscale, style, style_handle, on_each_feature, defStyle
#Procesos
import pandas as pd
import geopandas as gpd
import numpy as np
import re

##Primeras ejecuciones 
df_estatal = pd.read_csv('Datos/CSVs/estatal.csv')
df_estatal.columns = [col.replace('.', '') for col in df_estatal.columns]
new_names = []
for name in df_estatal.columns:
    if name.endswith('A'):
        new_names.append(name[:-1] + '-I')
    elif name.endswith('B'):
        new_names.append(name[:-1] + '-II')
    else:
        new_names.append(name)
df_estatal.columns = new_names
#print(df_estatal.columns)
# Store the columns of the DataFrame into a list
columns_list = df_estatal.columns.tolist()
# Print the list of columns to check

lista_de_opciones_personal = [col for col in columns_list if 'Personal' in col]
lista_de_opciones_unidades = [col for col in columns_list if 'Unidades' in col]
gdf_shapefile=gpd.read_file('Datos/geojson_hgo.geojson')
gdf_shapefile= gdf_shapefile.sort_values(by='CVEGEO')
gdf_shapefile=gdf_shapefile.reset_index()
df_estatal['NOM_MUN'] = gdf_shapefile['NOM_MUN']

map_default=auxiliarLeafltet.generateMapFromElection(lista_de_opciones_personal[-1],df_estatal,gdf_shapefile)
df_industrial=pd.read_csv("Datos/CSVs/Balassa_Modificado_Historico/Balassa_Mod_Nivel_Municipio_por_Grupos_2024B.csv")
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/customICE.css'])
####Lista de ids
#unidad_medida
#opcion_denue_semestre
#nav1-link
#nav2-link
#geojson
#store-map
#store-hist
#hideout_geojson
radio_items_original=[
                {'label': 'Promedio de personal', 'value': 'personal', },
                {'label': 'Unidades económicas', 'value': 'unidades',}]
radio_items_personal=[
                {'label': 'Promedio de personal', 'value': 'personal'},]


with open('Datos/Explicaciones breves.txt', encoding='utf-8') as f:
    explicaciones_breves = json.load(f)
accordion =  dbc.Accordion(
    [
        dbc.AccordionItem(###############     ICE
        [
            html.P(explicaciones_breves.get('Complejidad Económica','')),html.Button("Ver más...", style={'marginTop': 'auto'})
        ],
        title="Índice de Complejidad Económica de Entidades Goegráficas",
        style={'display':'block'},
        id='accordion-ice',item_id="1"
        ),
        dbc.AccordionItem(
        [
            html.P(explicaciones_breves.get('Afinidad contra Complejidad de Producto','')),
            html.Button("Ver más...", style={'marginTop': 'auto'})
        ],
        title="Afinidad vs. Complejidad de Productos",
        style={'display':'none'},
        id='accordion-afinidad',item_id="2"
        ),
        dbc.AccordionItem(
        [html.P(explicaciones_breves.get('Diversidad vs Ubicuidad',''))],
        title="Diversidad vs. Ubiquidad",
        style={'display':'none'},
        id='accordion-diversidad',item_id="3"
        ),
        dbc.AccordionItem(
        [ 
            
            dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Header")),
            ],
            id="modal-xl-espacio-prod",
            size="xl",
            is_open=False,
            ),
            html.P(explicaciones_breves.get('Conexión de Municipios',''))
            ,dbc.Button("Ver Espacio de Productos", id="open-xl", n_clicks=0, disabled=True, color="danger"),
            
        ],
        title="Espacio de Entidades",
        style={'display':'none'},
        id='accordion-espacio-prod',item_id="4"
        ),
    ],active_item=["1","2","3","4"]
    )
sidebar = html.Div(
    [
        html.H2("Visualizador geográfico"),
        html.Hr(),
        html.P("Índice de Complejidad Económica", className="lead"),
        html.Hr(),
        html.P("Unidad de medida:", className="lead", style={'fontSize': 'smaller'}),
        dcc.RadioItems(
            options=radio_items_original, value='personal', id='unidad_medida'),
        html.Hr(),
        html.P("Selecciona una edición del Directorio Estadístico Nacional de Unidades Económicas", className="lead", style={'fontSize': 'smaller'}),
        dcc.Dropdown(options=lista_de_opciones_personal, value=lista_de_opciones_personal[-1], id='opcion_denue_semestre'),
        html.Div(accordion, style={"margin-top": "auto"})  # Esto empuja el acordeón hacia abajo
    ],
    style={
        "height": "100vh",
        "display": "flex",
        "flex-direction": "column",
        "padding-left": "1vw",
        "padding-top": "2vw",
        "background-color": "#f8f9fa",
    },
)

##Dependiendo de la unidad de medida, se cambia el dropdown

geojson_fijo=dl.GeoJSON(
        data=map_default,
        style=style_handle,
        onEachFeature=on_each_feature,
        hideout=dict(selected=[47], classes=classes, colorscale=colorscale, style=style, colorProp="Area"),
        id="geojson",
        options=dict(interactive=False),
    )
content = html.Div(
    id="page-content",
    children=[dl.Map(id="map-container",
        center=[gdf_shapefile.geometry.centroid.y.mean(), gdf_shapefile.geometry.centroid.x.mean()],
        zoom=8,
        children=[dl.TileLayer(), 
                  geojson_fijo,info
                  ],
        style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block", 'opacity': 1,'z-index':'3'},
        className=''
    )],
    style={'width': '100%', 'height': '50vh'}
)

interior_alt_content=dcc.Graph(id='interior-alt-content',figure={},style={'height':'91.5vh', 'background-color':'lightgray'},
                                 config={'scrollZoom': True})
alt_content = html.Div(
    id="alt-content",
    children=interior_alt_content,
    style={'display':'none'}
)
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("ICE", href="#", id="nav1-link", className="nav-link active",n_clicks=0)),
        dbc.NavItem(dbc.NavLink("Afinidad", href="#", id="nav2-link", className="nav-link",n_clicks=0)),
        
    ],
    brand="",
    brand_href="#",
    color="primary",
    dark=True,
    style={'height':'5.5vh'},
    
)

app.layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col(sidebar, width=3, style={"height": "100vh"},xs=12,sm=12,md=3,lg=3,xl=3,xxl=3),
            dbc.Col(
                [navbar,
                    content,
                    alt_content,

                    dcc.Store(id="store-map", data=map_default),
                    dcc.Store(id="hideout_geojson", data=dict(selected=[], classes=classes, colorscale=colorscale, style=style, colorProp="Area")),
                ],
                width=9,
                style={
                    "padding-top": "1.5vh",
                    "padding-bottom": "1.5vh",
                    "padding-left": "2vw",
                    "padding-right": "2vw",
                       }  # Agrega espacio a la derecha y padding interno
            ,xs=12,sm=12,md=9,lg=9,xl=9,xxl=9),
        ], className="g-0"),
    ],
    fluid=True,
    style={'height':'100vh','padding':'0'}
)

                ####################  Puras Callbacks  ####################
####################        NAV
##Este es el que cambia el contenido dependiendo del click sobre el nav
#Recibe click sobre el navbar 
#Dependiendo del click, oculta lo necesario. 
@app.callback(
    [
        Output("page-content", "style"),
        Output("alt-content", "style"),
        Output("nav1-link", 'className'),
        Output("nav2-link", 'className'),

    ],
    [
        Input("nav1-link", "n_clicks"),
        Input("nav2-link", "n_clicks"),
        State("nav1-link", "className"),
        State("nav2-link", "className"),
    ],
    prevent_initial_call=True,
)
def render_content(nav_1_click, nav_2_click,n1a,n2a):##Se puede mejorar. Se actualizan innecesariamente las classNames cuando se da click en un nav ya activo
    nav_clicked=re.search(r'\d+', dash.callback_context.triggered[0]['prop_id']).group()
    nav_actived=[n1a,n2a]##En tiempo pasado
    if("active" in nav_actived[int(nav_clicked)-1]):##Así evito una re-carga al dar click redundante
        return no_update, no_update,no_update,no_update
    vacio=defStyle('none')
    block=defStyle('block')
    if 'nav1-link.n_clicks' in dash.callback_context.triggered[0]['prop_id']:
        #Nav 2 activo
        no_vacio=defStyle('map')
        
        return no_vacio, vacio,'nav-link active', 'nav-link'

    if 'nav2-link.n_clicks' in dash.callback_context.triggered[0]['prop_id']:
        #Nav 2 activo
        no_vacio=defStyle('nav2')
        
        return vacio, no_vacio, 'nav-link', 'nav-link active'


##Este es el que se actualiza el contenido dependiendo de la eleccion del año. 
#Recibe la eleccion del año, el estado de los navs, y el hideout del geojson fijo
#Actualiza el geojson fijo (solo su data porque ahí trae Area que es el color)
#Además, revisa el estado de las navs y dependiendo de la activa, actualiza su respectiva visualización
@app.callback(
        Output("geojson", "data", allow_duplicate=True),#Actualizaria el mapa geojson 
        Input('opcion_denue_semestre', 'value'),
    prevent_initial_call=True
)
def update_map_nav1(eleccion_año):
    #Vamos a renderear el contenido necesario.
    map_default = auxiliarLeafltet.generateMapFromElection(eleccion_año, df_estatal, gdf_shapefile)

        
    return map_default
    

if __name__ == "__main__":
    app.run_server(debug=True)
