import ipywidgets as widgets
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

df_year=pd.read_sql_query(''' SELECT DISTINCT to_char( "ahiscl"."hrgt_patient_dtl"."gdt_entry_date", 'yyyy' ) AS year FROM "ahiscl"."hrgt_patient_dtl" GROUP BY
                       to_char( "ahiscl"."hrgt_patient_dtl".gdt_entry_date, 'DD' )  ,"ahiscl"."hrgt_patient_dtl"."gdt_entry_date"
                ORDER BY 
                       year DESC''',conn)





app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

test_png = 'C:/Users/HP/Desktop/CDAC/eswasthya_dashboard/logo4.png'
test_base64 = base64.b64encode(open(test_png, 'rb').read()).decode('ascii')

layout=html.Div([

    
    dbc.Navbar([
    dbc.Container(
        [

            dbc.Row(
                [
                    dbc.Col([
                               
                        html.P(className="fa fa-envelope mt-2",style={"color":"white"}),
                        html.P(["dhsodisha@gmail.com"],className='m-1',style={"color":"white"})],className='col-sm-6 d-flex flex-row'),
                                
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
                                
                                    className="me-auto pl-4  ",
                                ),
                                dbc.Row([
                                dbc.Col(
                                    dbc.Button(
                                            "Hospital Wise Statistics", color="primary", className="ms-1 ", href='/'),className='p-1',
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
    dcc.Interval(id='my_interval',interval=60000,n_intervals=0)
    ]),



dbc.Container([
    dbc.Col([
        dbc.Col([

        dbc.Col(html.H5("Year :",className='text-dark'),className="col-sm-2 text-end "),
          dbc.Col( [dcc.Dropdown(id='my_dropdown',
        options=[
            {'label': k, 'value': k} for k in list(df_year.year.unique())

        ],
        value= '2022', 
        multi=False,
        clearable=False)],className="col-sm-10 w-25 "),
        
    ],className='row justify-content-end')],className='row p-3 mt-4 ')],className='justify-content-center'),

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
                                        html.H5(id='today_total_opd',className='card-text text-left '),dcc.Graph(id="today_opd_graph",style={ 'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"#EEEDF4"})],className='col-lg-6 p-2 vh-50'),
                dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("Admission Count",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-heartbeat fa-2x ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='today_total_adm',className='card-text text-left '),dcc.Graph(id="today_adm_graph",style={ 'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"white"})],className='col-lg-6 p-2 vh-50'),
                dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("Emergency Count",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-medkit fa-2x ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='today_total_emg',className='card-text text-left '),dcc.Graph(id="today_emg_graph",style={ 'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"white"})],className='col-lg-6 p-2 vh-50'),
                dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("Reports",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-file-medical fa-2x  ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='today_total_report',className='card-text text-left '),dcc.Graph(id="today_reportgraph",style={ 'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"#EEEDF4"})],className='col-lg-6 p-2 vh-50')],className='row justify-content-center'),
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
                                        html.H5(id='total_opd_count',className='card-text text-left '),dcc.Graph(id="total_graph_opd",style={ 'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"#EEEDF4"})],className='col-lg-6 p-2 vh-50'),
                dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("Total Admission",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-heartbeat fa-2x ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='total_adm_count',className='card-text text-left '),dcc.Graph(id="total_graph_adm",style={ 'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"white"})],className='col-lg-6 p-2 vh-50'),
                dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("Total Emergency",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-medkit fa-2x ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='total_emg_count',className='card-text text-left '),dcc.Graph(id="total_graph_emg",style={'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"white"})],className='col-lg-6 p-2 vh-50 '),
                dbc.Col([
                    dbc.Col([
                        dbc.Col([html.H6("Total Report",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                            html.Div(className="fa fa-file-medical fa-2x ms-auto ")],className='d-flex flex-row'),
                                        html.H5(id='total_report_count',className='card-text text-left '),dcc.Graph(id="total_graph_report",style={'height': '30vh'})],
                                            
                                        className='card shadow-lg p-3 rounded ',style={"backgroundColor":"#EEEDF4"})],className='col-lg-6 p-2 vh-50')]),
                ],className='row justify-content-center')



            ],className='col-sm-6 p-3 justify-content-center')],


        className='card d-flex flex-row justify-content-center',style={"border-radius":"20px"})

        ],className='row justify-content-center')


    ],className='row p-3 mt-1 justify-content-center '),

    html.Div(
        [

            dbc.Row(
                [
                    
                        dbc.Col([
                            dbc.Col([html.H6("Month Wise OPD Count",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                           
                                        dcc.Graph(id="total_month_opdcount")],className='card shadow-lg p-5 justify-content-center ',style={"border-radius":"20px"})],className='col-sm-6 pb-2'),

                        dbc.Col([
                            dbc.Col([html.H6("Month Wise OPD Count (Gender Wise)",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                           
                                        dcc.Graph(id="total_month_opdgender")],className='card shadow-lg p-5 justify-content-center ',style={"border-radius":"20px"})],className='col-sm-6 pb-2'),
                                            
                ]
            ),

        ],className='row p-2 justify-content-center mt-2'),



    html.Div(
        [

            dbc.Row(
                [
                     dbc.Col([
                            dbc.Col([html.H6("Month Wise Casuality Count",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                           
                                        dcc.Graph(id="total_month_casualitycount")],className='card shadow-lg p-5 justify-content-center ',style={"border-radius":"20px"})],className='col-sm-6 pb-2'),

                        dbc.Col([
                            dbc.Col([html.H6("Month Wise Casuality Count (Gender Wise)",className='card-title text-left fw-bold ',style={"color":"cc1818"}),
                                           
                                        dcc.Graph(id="total_month_casualitygender")],className='card shadow-lg p-5 justify-content-center ',style={"border-radius":"20px"})],className='col-sm-6 pb-2'),
                                            
                ]
            ),

        ],className='row p-2 justify-content-center')
    ],className='container-fluid d-flex flex-column ',style={"backgroundColor": "#F7F7F9"})],className='d-flex flex-column')












#     from datetime import datetime

# currentMonth = datetime.now().month
# print(currentMonth)
 # AND EXTRACT ( MONTH FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) = EXTRACT ( MONTH FROM now( ) ) 

 # rgb(244, 243, 239)
 # last year and thi year bar graphs