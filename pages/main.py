import plotly.express as px
import psycopg2
import plotly.express as px
import numpy as np 
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import Dash, dcc, Input, Output
from plotly.express import data
import matplotlib.pyplot as plt
from datetime import datetime
import dash_bootstrap_components as dbc
from dash import html
import base64
import visdcc
import plotly.express as px
import folium

def get_connection():
    try:
        return psycopg2.connect(
            database="",
            user="",
            password="",
            host="",
            port=)

    except:
        return False
  
conn = get_connection()
  
if conn:
    print("Connection to the PostgreSQL established successfully")
else:
    print("Connection to the PostgreSQL encountered an error")

  
curr = conn.cursor()

df_mydropdown= pd.read_sql_query(
        '''                                          
SELECT
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name" 
FROM
    "ahiscl"."gblt_hospital_mst" 
WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21   
GROUP BY
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name"''', conn) 




app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, 'https://codepen.io/chriddyp/pen/bWLwgP.css'],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

test_png = '../../logo4.png'
test_base64 = base64.b64encode(open(test_png, 'rb').read()).decode('ascii')


layout=html.Div([

    
    dbc.Navbar([
    dbc.Container(      #same as div
        [

            dbc.Row(    #in grid view divide
                [
                            dbc.Col([
                               
                                html.P(className="fa fa-envelope mt-2",style={"color":"white"}),
                                html.P(["xxxxxx@gmail.com"],className='m-1',style={"color":"white"})],className='col-sm-6 d-flex flex-row'),
                                
                            dbc.Col([
                                
                                html.P(className="fa fa-mobile mt-2",style={"color":"white"}),
                                html.P(["0674- 2391536"],className='m-1',style={"color":"white"})],className='col-sm-6 d-flex flex-row justify-content-end ')
                                
         
                ],
                
                className="flex-grow-1 flex-row w-100 ",
            ),
        ],
        fluid=True,
    )],className='justify-content-center p-0 h-0',color="primary"),
    



    dbc.Navbar([
    dbc.Container(
        [
        dbc.Col([
            html.A(
                dbc.Row([
                   dbc.Col([html.Img(src='data:image/png;base64,{}'.format(test_base64),className=" img-fluid h-100 ")],className='col-sm-12 d-none d-md-block   ',style={"height":"5rem"}),
                    
                ])
            ),
            dbc.Row(
                [
                   
                        dbc.Nav(
                            [
                                dbc.Col(html.H6(['ସ୍ୱାସ୍ଥ୍ୟଓ ପରିବାର କଲ୍ୟାଣ ବିଭାଗ', html.Br(), 'Department of Health & Family Welfare', html.Br(), 'GOVERNMENT OF ODISHA']
                                    ,className='p-3 h-50 d-none d-md-block  ',style={"color":"black","font-size":"1vw"}),
                                
                                    className="me-auto pl-4  ",   #margin-end
                                ),
                                dbc.Row([
                                dbc.Col(
                                    dbc.Button(
                                            "Hospital Wise Statistics", color="primary", className="ms-1 ",active=True ),className='p-1',
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



    html.Div([

html.Div([
    dcc.Interval(id='my_interval',interval=60000, n_intervals=0)
    ]),




dbc.Container([
    dbc.Col([
        dbc.Row(
        dbc.Col([             #for drop-down

        dbc.Col(html.H5("Hospital Name :",className='text-dark fw-bold'),className="col-sm-2"),
          dbc.Col( [dcc.Dropdown(id='my_dropdown',
        options=[
            {'label': k, 'value': k} for k in list(df_mydropdown.gstr_hospital_name.unique())

        ],
        value= 'Capital Hospital, Bhubaneshwar', 
        multi=False,
        clearable=False)],className="col-sm-10"),
        
    ],className='row justify-content-center'))],className='row p-3 mt-4 ')],className='justify-content-center'),


html.Div([
    dbc.Col([
    dbc.Row([


        dbc.Col([

            dbc.Row([

                dbc.Row([

                dbc.Col([
                                    dbc.Col([
                                        dbc.Col([html.H5("Today's Counts:",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            ],className='d-flex flex-row')],
                                        
                
                                      className='card shadow-lg p-3 rounded ')],className='col-lg-12 p-2 ')],className='row justify-content-center'),
                dbc.Row([

                dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("OPD Count",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-hospital-user fa-2x ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='today_opd_count',className='card-text text-left '),dcc.Graph(id="today_opd",style={ 'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"#EEEDF4"})],className='col-lg-6 p-2 vh-50'),
                dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("Admission Count",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-heartbeat fa-2x ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='today_adm_count',className='card-text text-left '),dcc.Graph(id="today_adm",style={ 'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"white"})],className='col-lg-6 p-2 vh-50'),
                dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("Emergency Count",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-medkit fa-2x ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='today_emg_count',className='card-text text-left '),dcc.Graph(id="today_emg",style={ 'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"white"})],className='col-lg-6 p-2 vh-50'),
                dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("Reports",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-file-medical fa-2x ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='today_report_count',className='card-text text-left '),dcc.Graph(id="today_report",style={ 'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded  ',style={"backgroundColor":"#EEEDF4"})],className='col-lg-6 p-2 vh-50')],className='row justify-content-center'),
                ],className='row justify-content-center')



                
            ],className='col-sm-6 p-3 justify-content-center'),


        dbc.Col([
            dbc.Row([

                dbc.Row([

                dbc.Col([
                                    dbc.Col([
                                        dbc.Col([html.H5("Total Counts:",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            ],className='d-flex flex-row')],
                                        
                                       className='card shadow-lg p-3 rounded ')],className='col-lg-12 p-2 vh-25 ')],className='row justify-content-center'),
                dbc.Row([

               dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("Total OPD",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-hospital-user fa-2x ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='opd_count',className='card-text text-left '),dcc.Graph(id="graph_opd",style={ 'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"#EEEDF4"})],className='col-lg-6 p-2 vh-50'),
                dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("Total Admission",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-heartbeat fa-2x ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='adm_count',className='card-text text-left '),dcc.Graph(id="graph_adm",style={ 'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"white"})],className='col-lg-6 p-2 vh-50'),
                dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("Total Emergency",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-medkit fa-2x ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='emg_count',className='card-text text-left '),dcc.Graph(id="graph_emg",style={'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded border-bottom" ',style={"backgroundColor":"white"})],className='col-lg-6 p-2 vh-50 border-bottom"'),
                dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("Total Patient Report",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-file-medical fa-2x ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='report_count',className='card-text text-left '),dcc.Graph(id="graph_reports",style={'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"#EEEDF4"})],className='col-lg-6 p-2 vh-50')]),
                ],className='row justify-content-center')



            ],className='col-sm-6 p-3 justify-content-center')],


        className='card d-flex flex-row justify-content-center',style={"border-radius":"20px"})

        ],className='row justify-content-center')


    ],className='container-fluid p-3 justify-content-center '),

html.Div(
    [
        dbc.Row(
            [
                dbc.Col([
                            dbc.Col([html.H6("Today's Department Count",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                           
                                        dcc.Graph(id="graph_department")],className='card shadow-lg p-5 justify-content-center ',style={"border-radius":"20px"})],className='col-sm-12 pb-2')

                        
               
            ]
        ),

    ],className='row p-2 justify-content-center'),




          


html.Div([
        dbc.Col([
                dbc.Col(
                    dbc.Col([
                         dbc.Col([
                            dbc.Col([html.H6("Current Month Date Wise OPD Count",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                           
                                        dcc.Graph(id="graph_datewise_opdcount")])],className='col-sm-12 p-5 pb-2'),

                        
                    dbc.Col(html.Div([dcc.Dropdown(id='my_dropdown2',
                            options=[
                                   {'label':'Bar Graph','value':'Bar Graph'},
                                   
                                   {'label':'Pie Graph','value':'Pie Graph'},
                                   {'label':'Donut Graph','value':'Donut Graph'},
                                   # {'label':'Donut Graph','value':'Semi-Donut Graph'},
                                   {'label':'Area Graph','value':'Area Graph'},
                                   # {'label':'Line Graph','value':'Line Graph'}

                                 
                                ],
                                value= 'Bar Graph', 
                                multi=False,
                                clearable=False)],className="w-25 row2"),
                    className='card-text p-3')],
                className='card shadow-lg p-2',style={"border-radius":"20px"}),
        className='col-sm-12')],
className='row p-2 justify-content-center',style={"border-radius":"20px"})],className='container-fluid justify-content-center'),



    html.Div(
        [
            dbc.Col([
                    dbc.Col(
                        dbc.Col([
                            dbc.Col([
                            dbc.Col([html.H6("Current Month Date Wise Casuality Count",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                           
                                        dcc.Graph(id="graph_datewise_casualitycount")])],className='col-sm-12 p-5 pb-2'),

                        dbc.Col(html.Div([dcc.Dropdown(id='my_dropdown3',
                                options=[
                                       {'label':'Bar Graph','value':'Bar Graph'},
                                       
                                       {'label':'Pie Graph','value':'Pie Graph'},
                                       {'label':'Donut Graph','value':'Donut Graph'},
                                       # {'label':'Semi-Dount Graph','value':'Semi-Donut Graph'},
                                       {'label':'Area Graph','value':'Area Graph'},
                                       # {'label':'Line Graph','value':'Line Graph'}

                                     
                                    ],
                                    value= 'Bar Graph', 
                                    multi=False,
                                    clearable=False)],className="w-25 row2"),
                        className='card-text p-3')],
                    className='card shadow-lg p-2',style={"border-radius":"20px"}),
            className='col-sm-12')],
    className='row p-2 justify-content-center mt-2',style={"border-radius":"20px"})
            ],className='container-fluid justify-content-center'),



    html.Div(
        [

            dbc.Row(
                [
                    dbc.Col([
                            dbc.Col([html.H6("Month Wise OPD Count",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                           
                                        dcc.Graph(id="graph_month_opdcount")],className='card shadow-lg p-5 justify-content-center ',style={"border-radius":"20px"})],className='col-sm-6 pb-2'),

                        dbc.Col([
                            dbc.Col([html.H6("Month Wise OPD Count (Gender Wise)",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                           
                                        dcc.Graph(id="graph_month_opdgender")],className='card shadow-lg p-5 justify-content-center ',style={"border-radius":"20px"})],className='col-sm-6 pb-2'),
                                          
                ]
            ),

        ],className='row p-2 justify-content-center mt-2'),



    html.Div(
        [

            dbc.Row(
                [
                    dbc.Col([
                            dbc.Col([html.H6("Month Wise Casuality Count",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                           
                                        dcc.Graph(id="graph_month_casualitycount")],className='card shadow-lg p-5 justify-content-center ',style={"border-radius":"20px"})],className='col-sm-6 pb-2'),

                        dbc.Col([
                            dbc.Col([html.H6("Month Wise Casuality Count (Gender Wise)",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                           
                                        dcc.Graph(id="graph_month_casualitygender")],className='card shadow-lg p-5 justify-content-center ',style={"border-radius":"20px"})],className='col-sm-6 pb-2'),
                                          
                ]
            ),

        ],className='row p-2 justify-content-center')
    ],className='container-fluid d-flex flex-column',style={"backgroundColor": "#F7F7F9"})],className='d-flex flex-column')

