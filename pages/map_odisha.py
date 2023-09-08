import ipywidgets as widgets
import plotly.express as px
import psycopg2
import plotly.express as px
import numpy as np 
import pandas as pd
import itertools
import plotly.graph_objects as go
import dash
from dash import Dash, dcc, Input, Output, html
from plotly.express import data
import matplotlib.pyplot as plt
from datetime import datetime
import dash_bootstrap_components as dbc
from dash import html
import base64
import visdcc
import plotly.express as px
import folium
from folium import GeoJson
from pages import main, queries1
# from app import *

def get_connection():
    try:
        return psycopg2.connect(
            database="odisha_uat_local",
            user="enterprisedb",
            password="enterprisedb",
            host="10.226.17.97",
            port=5444)

    except:
        return False
  
conn = get_connection()
  
if conn:
    print("Connection to the PostgreSQL established successfully")
else:
    print("Connection to the PostgreSQL encountered an error")
  
curr = conn.cursor()



# df_map=pd.read_sql_query('''SELECT
#     COUNT
#         ("ahiscl"."hrgt_episode_dtl"."hrgnum_puk") as count ,
#     "ahiscl"."gblt_hospital_mst_copy1"."latitude" AS latitude,
#     "ahiscl"."gblt_hospital_mst_copy1"."longitude" AS longitude,
#     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
#     "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name" 
# FROM
#     "ahiscl"."hrgt_episode_dtl",
#     "ahiscl"."gblt_hospital_mst_copy1" 
# WHERE
#  "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code" = "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" AND 
#      "ahiscl"."gblt_hospital_mst_copy1"."gnum_isvalid" = 1 
#     AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_state_code" = 21  
# GROUP BY
#     "ahiscl"."gblt_hospital_mst_copy1"."latitude",
#     "ahiscl"."gblt_hospital_mst_copy1"."longitude",
#     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
#     "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name"
#         ''',conn)



# coordinates=(20.9517, 85.0985)
# geo=r"Admin2.json"
# file=open(geo,encoding="utf8")
# text=file.read()

# orissa_map=folium.Map(location=coordinates,zoom_start=8)
# orissa_map=folium.Map(location=coordinates,zoom_start=7,min_zoom=7,max_zoom=7,zoom_control=False,scrollWheelZoom=False,
#                dragging=False)
# GeoJson(text).add_to(orissa_map)
# orissa_map.save('maplocation.html')


# locations=df_map[['latitude','longitude']]
# locationlist=locations.values.tolist()
# print(locationlist[0])

# for point in range(0,len(locationlist)):    #for making pointers
#     folium.Marker(location=locationlist[point],tooltip=(df_map['gstr_hospital_name'][point], 'Registrations:', df_map['count'][point])).add_to(orissa_map)
# orissa_map.save('maplocation.html')


# dataframe containing records of hospital types from gblt_hospital_type_mst
df_hospital_type=pd.read_sql_query(queries1.qr_name_id, conn)
df_hospital_typesorted=df_hospital_type.sort_values(by="hosp_name")
# df_hospital_namesorted=main.df_mydropdown.sort_values(by="gstr_hospital_name")



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)



test_png = 'C:/Users/HP/Desktop/CDAC/eswasthya_dashboard/logo4.png'
test_base64 = base64.b64encode(open(test_png, 'rb').read()).decode('ascii')

# tabs_styles = {
#     'height': '58px'
# }
# tab_style = {
#     'borderBottom': '1px solid #d6d6d6',
#     'padding': '6px',
#     'fontWeight': 'bold'
# }

# tab_selected_style = {
#     'borderTop': '1px solid #d6d6d6',
#     'borderBottom': '1px solid #d6d6d6',
#     'backgroundColor': '#119DFF',
#     'color': 'white',
#     'padding': '6px'
# }
# # x={"label": k, "value": i} 
# for (k,i) in zip(list(df_hospital_type.hosp_name.unique()),list(df_hospital_type.hosp_id.unique())):
#     print(k,i)

layout=html.Div([
    html.Div([
    dcc.Interval(id='my_interval',interval=60000, n_intervals=0)
    ]),
    

    dbc.Navbar([
    dbc.Container(
        [
        dbc.Col([
            dbc.Row(
                [
                   
                        dbc.Nav(
                            [
                                dbc.Col([
                                    html.Div([dcc.RadioItems(id='my_checklist',
                                options=[
                                    {"label": html.Div([k],style={"padding-right": "20px", "display":"inline-block"}), "value": i} for (k,i) in zip(list(df_hospital_typesorted.hosp_name.unique()),list(df_hospital_typesorted.hosp_id.unique()))
                                    ], value=1)]
                                    )],align="center",className=' p-4 vh-15'),
                                    #  style={'text-align':'center'}
# , style="padding-right: 15px;"
                                dbc.Row([
                                dbc.Col(
                                    dbc.Button(
                                            "Hospital Wise Statistics", color="primary", className="ms-1 ",href='/'),className='p-1',
                                            width="auto",align="center"),
                                
                                # dbc.Col(
                                #     dbc.Button(
                                #             "OPD Count", color="primary", className="ms-1 ",href='/opd'),className='p-1',
                                #             width="auto",align="center"),
                                dbc.Col(
                                    dbc.Button(
                                            "Total Counts", color="primary", className="ms-1 ",href='/total'),className='p-1',
                                            width="auto",align="center"),

                                dbc.Col(
                                    dbc.Button(
                                            "Configuration", color="primary", className="ms-1",href='/map_odisha'  ),className='p-1',
                                            width="auto",align="center")],className="p-3")
                            
                            ],
                            # make sure nav takes up the full width for auto
                            # margin to get applied
                            className="w-100 justify-content-center",
                        ),
                        
                ],
                # the row should expand to fill the available horizontal space
                className="flex-grow-1 justify-content-center ml-4",
            )],className=" navbar justify-content-center h-100 p-0"),
        ],
        fluid=True,className='h-100',
    )],className='justify-content-center p-0',color="light"),

    # dbc.Container([
    #         dbc.Row(
    #         dbc.Col(
    #                 html.Div(
    #                     dcc.Checklist(id='my_checklist',
    #                     options=[
    #                         {'label': k, 'value': i} for k in list(df_hospital_type.hosp_name.unique()) AND for i in list(df_hospital_type.hosp_id.unique()),
    #                     ],
    #                     style={'color': 'LightGreen', 'font-size': 20},
    #                     value=['MCH'])
    # )
    # )
    #     )
    # ])

    # dbc.Container([
    # dbc.Col([
    #     dbc.Row(
    #     dbc.Col([             

    #       ,
        
    # ],className='row justify-content-center p-0'))],className='row p-1')]),

    # dbc.Container([
    # dbc.Col([
    #     dbc.Row(
    #     dbc.Col([             #for drop-down

    #     dbc.Col(html.H6("Search name :",className='text-dark'), style={"text-align":"right"}, className="col-sm-2 mt-2"),
    #       dbc.Col( [dcc.Dropdown(id='my_dropdown2',
    #     options=[
    #         {'label': k, 'value': k} for k in list(df_hospital_namesorted.gstr_hospital_name.unique())

    #     ], 
    #     multi=False,
    #     clearable=False)],className="col-sm-5"),
        
    # ],className='row justify-content-center'))],className='row p-3 mt-2 ')],className='justify-content-center'),

    # dbc.Container([
    # dbc.Col([
    #     dbc.Row(
    #     dbc.Col([             
    #       dbc.Col( [dcc.RadioItems(df_hospital_type.hosp_name.unique(), df_hospital_type.hosp_id.unique(),id='my_checklist'
    #     )],className="col-sm-10"),
    # ],className='row justify-content-center'))],className='row p-3 mt-4 ')]),

    # html.Div([

    #     html.Div([

    #         dbc.Col([
    #         html.Iframe(id='map', srcDoc=None,width='100%',height='500')

    #         ],className='card shadow-lg rounded justify-content-center')],className='justify-content-center')],
    #     className='container-fluid d-flex flex-column p-5',style={"backgroundColor": "#F7F7F9"}),
        html.Div([
            dbc.Col([
                 dbc.Row([
                dbc.Col([
                html.Div([
                                    dbc.Col( [dcc.Dropdown(id='my_dropdown2', multi=False,clearable=False)],  align="center", className='pt-3')
                                ], className=' col-sm-4 mb-3'),
            ], className="mt-2")
            ]),
                dbc.Row([
            #         dbc.Col([
            #             dbc.Row([
                            
            #         dbc.Col([ 
            #             html.Iframe(id='map', srcDoc=None,width='100%',height='500')
            #         ]),
            #     ],className='row justify-content-center')
            # ],className='col-sm-8 pt-3 '),
        dbc.Col([
            

                dbc.Row([
                dbc.Col([
                            html.Div([
                                
                                            dcc.Tabs(id="hosp-data-tabs", value='tab1-hardware', 
                                            children=[
                                                dcc.Tab(label='Hardware', value='tab1-hardware'),
                                                dcc.Tab(label='Networking', value='tab2-networking'),
                                                dcc.Tab(label='Software', value='tab3-software'),
                                                dcc.Tab(label='Manpower', value='tab4-manpower')
                                                ], colors={"border":"darkgrey",
                                                    "background":"lightgrey"}),
                                                dbc.Row(id='hosp-data-display'
                                                #     html.Div([
                                                #     dcc.Graph(id='desktops'),
                                                #     ], className='col-sm-4'),
                                                # html.Div([dcc.Graph(id='printer')
                                                #     ], className='col-sm-4'),
                                                # html.Div([
                                                #     dcc.Graph(id='ups')
                                                # ], className='col-sm-4')
                                                )
                                                
                                                
                                                # html.Div([html.H5("Desktop")],className='mt-3'),
                                                # html.Div([
                                                # dbc.Col([html.H6("Required",style={"display": "inline-block", "margin-right":"10px"}),
                                                # dbc.Progress(id='Required', value=25, color="warning",className="mb-2",style={"width":"200px"})
                                                # ],className='d-flex mt-3')
                                                # ]),
                                                # html.Div([
                                                # dbc.Col([html.H6("Tendered",style={"display": "inline-block", "margin-right":"10px"}),
                                                # dbc.Progress(id='Tendered',value=50, color="info", className="mb-2",style={"width":"200px"})
                                                # ],className='d-flex')
                                                # ]),
                                                # html.Div([
                                                # dbc.Col([html.H6("Procured",style={"display": "inline-block", "margin-right":"10px"}),
                                                # dbc.Progress(id='Procured',value=75, color="info", className="mb-2",style={"width":"200px"})
                                                # ],className='d-flex')
                                                # ]),
                                                # html.Div([
                                                # dbc.Col([html.H6("Delivered",style={"display": "inline-block", "margin-right":"10px"}),
                                                # dbc.Progress(id='Delivered',value=100, color="info", className="mb-2",style={"width":"200px"})
                                                # ],className='d-flex')
                                                # ]),
                                                #  html.Div([
                                                # dbc.Col([html.H6("Comissioned",style={"display": "inline-block", "margin-right":"10px"}),
                                                # dbc.Progress(id='Comissioned',value=100, color="success",style={"width":"200px"})
                                                # ],className='d-flex')
                                                # ]),
                                                ])
                                            ],
                                            className='col-lg-12 vh-25 ',width="auto")])
            ],className='pt-3')],


        className='d-flex flex-row justify-content-center',style={"border-radius":"20px"})

        ],className='row justify-content-center')


    ],className='container-fluid justify-content-center ')
        
        ],className='d-flex flex-column')

    # html.Div([

    #     html.Div([

    #         dbc.Col([
    #         html.Iframe(id='map2', srcDoc=None,width='100%',height='500')

    #         ],className='card shadow-lg rounded justify-content-center')],className='justify-content-center')],
    #     className='container-fluid d-flex flex-column p-5',style={"backgroundColor": "#F7F7F9"})],className='d-flex flex-column')



