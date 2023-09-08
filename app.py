#import all the dependencies
import dash
from dash import Dash, dcc, html, Input, Output, callback, ctx, dash_table
from pages import main,total_count,map_odisha

import plotly.express as px
import psycopg2

import numpy as np 
import pandas as pd
import plotly.graph_objects as go

from plotly.express import data
import matplotlib.pyplot as plt

import dash_bootstrap_components as dbc

import base64   #use to encode image
import folium   #for map
import folium.plugins
from folium.plugins import Search
from folium.plugins import MarkerCluster


#connection----

def get_connection():
    try:
        return psycopg2.connect(        #for connection with postgresql
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
    
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}]
    # ], external_scripts=[
    #     'https://ajax.googleapis.com/ajax/libs/jquery/3.6.1/jquery.min.js',
    #     {'src': 'C:/Users/HP/Desktop/CDAC/eswasthya_dashboard/custom-script.js'}
    # ]
)

test_png = 'C:/Users/HP/Desktop/CDAC/eswasthya_dashboard/logo4.png'
test_base64 = base64.b64encode(open(test_png, 'rb').read()).decode('ascii')

app.title="Eswasthya dashboard"
server = app.server

app.layout = html.Div([ #Dash core Component Module
    dcc.Location(id='url', refresh=False), #update the URL without refreshing the page
    html.Div(id='page-content')
])


@callback(Output('page-content', 'children'),   #childrn is a property used for html components
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return main.layout
    elif pathname == '/map_odisha':
        return map_odisha.layout
    elif pathname == '/total':
        return total_count.layout
    else:
        return '404'

# checklistmap1=pd.read_sql_query(f'''SELECT
#         COUNT
#         ("ahiscl"."hrgt_episode_dtl"."hrgnum_puk") as count ,
#         "ahiscl"."gblt_hospital_mst_copy1"."latitude" AS latitude,
#         "ahiscl"."gblt_hospital_mst_copy1"."longitude" AS longitude,
#         "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
#         "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name",
#         "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_type"
#         FROM
#         "ahiscl"."hrgt_episode_dtl",
#         "ahiscl"."gblt_hospital_mst_copy1" 
#         WHERE
#         "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code" = "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" AND 
#         "ahiscl"."gblt_hospital_mst_copy1"."gnum_isvalid" = 1 
#         AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_state_code" = 21 
#         AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_type" =1
#         GROUP BY
#         "ahiscl"."gblt_hospital_mst_copy1"."latitude",
#         "ahiscl"."gblt_hospital_mst_copy1"."longitude",
#         "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
#         "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name" ''',conn)

# drop_options2=checklistmap1[['gstr_hospital_name','gnum_hospital_type']]
# # a=drop_options2.set_index('gstr_hospital_name').T.to_dict('list')
# # print(a)
# # print(type(a))
# a=dict(drop_options2.values)
# print(a)

#****************************************************HOSPITAL WISE STATISTICS***********************************************************

#callback and sql query for today's opd count in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='today_opd_count', component_property='children'),    #todat opd count in hospital wise statistics 
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph(selected_hospital_name,n_intervals):

    today_opd_count_df=pd.read_sql_query('''              
                    
    SELECT "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
   COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_opd
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <>134 AND trunc("ahiscl"."hrgt_patient_dtl"."gdt_entry_date") = trunc(sysdate)
    
    GROUP BY "ahiscl"."gblt_hospital_mst"."gstr_hospital_name", "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
    
    
      union
            
        select "ahiscl"."gblt_hospital_mst"."gnum_hospital_code", "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",0 from "ahiscl"."gblt_hospital_mst" where "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" not in(
                
                SELECT "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
        
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl"
    WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <>134 AND trunc("ahiscl"."hrgt_patient_dtl"."gdt_entry_date") = trunc(sysdate)
    
    GROUP BY  "ahiscl"."gblt_hospital_mst"."gnum_hospital_code")
            ''',conn)

    df_filtered = today_opd_count_df[today_opd_count_df['gstr_hospital_name'] == selected_hospital_name]
    # print(df_filtered['count_opd'])

    return (df_filtered['count_opd'])

#callback and sql query for today's emg count in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='today_emg_count', component_property='children'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph(selected_hospital_name,n_intervals):

    today_emg_count_df=pd.read_sql_query('''
                      
                    
    SELECT "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
   COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_emg
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" =134 AND trunc("ahiscl"."hrgt_patient_dtl"."gdt_entry_date") = trunc(sysdate)
    
    GROUP BY "ahiscl"."gblt_hospital_mst"."gstr_hospital_name", "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
    
    
      union
            
        select "ahiscl"."gblt_hospital_mst"."gnum_hospital_code", "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",0 from "ahiscl"."gblt_hospital_mst" where "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" not in(
                
                SELECT "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
        
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" =134 AND trunc("ahiscl"."hrgt_patient_dtl"."gdt_entry_date") = trunc(sysdate)
    
    GROUP BY  "ahiscl"."gblt_hospital_mst"."gnum_hospital_code")
        
    ''',conn)


    df_filtered = today_emg_count_df[today_emg_count_df['gstr_hospital_name'] == selected_hospital_name]

    return (df_filtered['count_emg'])

#callback and sql query for today's adm count in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='today_adm_count', component_property='children'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph(selected_hospital_name,n_intervals):

    today_adm_count_df=pd.read_sql_query('''
            
        SELECT 
            "ahiscl"."gblt_hospital_mst"."gstr_hospital_name" ,count ( "ahiscl"."hipt_patadmission_dtl".hipnum_admno ) as count_adm
        FROM
            "ahiscl"."hipt_patadmission_dtl",
            "ahiscl"."gblt_hospital_mst" 
        WHERE
            "ahiscl"."gblt_hospital_mst".gnum_hospital_code = "ahiscl"."hipt_patadmission_dtl".gnum_hospital_code AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 AND "ahiscl"."hipt_patadmission_dtl"."gnum_isvalid" = 1 
            AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
            AND trunc( "ahiscl"."hipt_patadmission_dtl".hipdt_admdatetime ) = trunc( sysdate ) 
        GROUP BY
            
            "ahiscl"."gblt_hospital_mst"."gstr_hospital_name" union
                    
                select  "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",0 from "ahiscl"."gblt_hospital_mst" where "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" not in ( SELECT "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
            
        FROM
            "ahiscl"."hipt_patadmission_dtl",
            "ahiscl"."gblt_hospital_mst" 
        WHERE
            "ahiscl"."gblt_hospital_mst".gnum_hospital_code = "ahiscl"."hipt_patadmission_dtl".gnum_hospital_code AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 AND "ahiscl"."hipt_patadmission_dtl"."gnum_isvalid" = 1 
            AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
            AND trunc( "ahiscl"."hipt_patadmission_dtl".hipdt_admdatetime ) = trunc( sysdate ) 
        GROUP BY 
            "ahiscl"."gblt_hospital_mst"."gnum_hospital_code")
    ''',conn)
    df_filtered = today_adm_count_df[today_adm_count_df['gstr_hospital_name'] == selected_hospital_name]
    # print(df_filtered)

    return (df_filtered['count_adm'])

#callback and sql query for today's report count in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='today_report_count', component_property='children'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph(selected_hospital_name,n_intervals):


    today_report_count_df=pd.read_sql_query('''
            
        
SELECT COUNT
    (  COALESCE ( "ahiscl"."hivt_requisition_dtl"."hivtnum_req_dno", 0 ) ) AS count_reports,
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" 
FROM
    "ahiscl"."gblt_hospital_mst",
    "ahiscl"."hivt_requisition_dtl" 
WHERE
    "ahiscl"."hivt_requisition_dtl"."hivnum_reqdtl_status" IN ( 14, 26, 13 ) 
    AND trunc( "ahiscl"."hivt_requisition_dtl"."hivt_entry_date" ) = trunc( sysdate ) 
    AND "ahiscl"."hivt_requisition_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" 
GROUP BY
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
                ''',conn)

    df_filtered = today_report_count_df[today_report_count_df['gstr_hospital_name'] == selected_hospital_name]
    # print(df_filtered)

    if len(df_filtered['count_reports']):
        return (df_filtered['count_reports'])

    if not len(df_filtered['count_reports']):
        return("0")


    

#callback and sql query for today's opd graph in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='today_opd', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph(selected_hospital_name,n_intervals):


#query for hospital name*****************
    df_all = pd.read_sql_query(                    
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


#query for today's opd graph *****************************

    today_opd_graph=pd.read_sql_query('''                   
    SELECT
        
         "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name", "ahiscl"."hrgt_patient_dtl"."gstr_gender_code"  AS gender,
                COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_opd
       
        
    FROM
    "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_patient_dtl" ,"ahiscl"."hrgt_episode_dtl"
    WHERE
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <>134 AND trunc("ahiscl"."hrgt_patient_dtl"."gdt_entry_date") = trunc(sysdate)
        
    GROUP BY
        
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ,"ahiscl"."hrgt_patient_dtl"."gstr_gender_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name"''',conn)

    frames_today_opd=[df_all,today_opd_graph]

    df_today_opd=pd.concat(frames_today_opd)
    
    dff_today_opd_graph = df_today_opd[df_today_opd['gstr_hospital_name'] == selected_hospital_name]

   #code for graph/no data found 

    if len(dff_today_opd_graph['count_opd']) > 1:
        fig = px.pie(dff_today_opd_graph, values="count_opd", names="gender",color='gender',color_discrete_map={'M':'#f8ed62',
                                 'F':'#dab600',
                                 'T':'#EEDC82'}, height=200,hole=0.3)

        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if len(dff_today_opd_graph['count_opd']) == 1:
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    

    return(fig)

#callback and sql query for today's adm graph in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='today_adm', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph(selected_hospital_name,n_intervals):

    df_all = pd.read_sql_query(
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
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name" ''', conn)


    today_adm_graph=pd.read_sql_query('''
                   SELECT COUNT
            ( "ahiscl"."hipt_patadmission_dtl".hipnum_admno ) as count_adm,
            "ahiscl"."hipt_patadmission_dtl"."hrgstr_sex" AS gender,
            "ahiscl"."gblt_hospital_mst"."gstr_hospital_name" 
        FROM
            "ahiscl"."hipt_patadmission_dtl",
            "ahiscl"."gblt_hospital_mst" 
        WHERE
            "ahiscl"."gblt_hospital_mst".gnum_hospital_code = "ahiscl"."hipt_patadmission_dtl".gnum_hospital_code AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 AND "ahiscl"."hipt_patadmission_dtl"."gnum_isvalid" = 1 
            AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
            AND trunc( "ahiscl"."hipt_patadmission_dtl".hipdt_admdatetime ) = trunc( sysdate ) 
        GROUP BY
            "ahiscl"."hipt_patadmission_dtl"."hrgstr_sex",
            "ahiscl"."gblt_hospital_mst"."gstr_hospital_name"
         ''',conn)

            
    frames_today_adm=[df_all,today_adm_graph]

    df_today_adm=pd.concat(frames_today_adm)

    
    dff_today_adm_graph = df_today_adm[df_today_adm['gstr_hospital_name'] == selected_hospital_name]
    # print(dff_emg)

    if len(dff_today_adm_graph['count_adm']) > 1:
        fig = px.pie(dff_today_adm_graph, values="count_adm",color='gender',color_discrete_map={'M':'#E1C16E',
                                 'F':'#6E260E',
                                 'T':'#E97451'}, names="gender", height=200,hole=0.3)

        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if len(dff_today_adm_graph['count_adm']) == 1:
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    

    return(fig)

#callback and sql query for today's emg graph in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='today_emg', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,n_intervals):

    df_all = pd.read_sql_query(
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


    today_emg_graph=pd.read_sql_query('''
   SELECT
        
         "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name", "ahiscl"."hrgt_patient_dtl"."gstr_gender_code"  AS gender,
                COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_emg
       
        
    FROM
    "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_patient_dtl" ,"ahiscl"."hrgt_episode_dtl"
    WHERE
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" =134 AND trunc("ahiscl"."hrgt_patient_dtl"."gdt_entry_date") = trunc(sysdate)
        
    GROUP BY
        
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ,"ahiscl"."hrgt_patient_dtl"."gstr_gender_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name"
     ''',conn)

    frames_today_emg=[df_all,today_emg_graph]

    df_today_emg=pd.concat(frames_today_emg)
        
    dff_today_emg_graph = df_today_emg[df_today_emg['gstr_hospital_name'] == selected_hospital_name]
    # print(dff_emg)

    if len(dff_today_emg_graph['count_emg']) > 1:
        fig = px.pie(dff_today_emg_graph, values="count_emg", names="gender",color='gender',color_discrete_map={'M':'#CA3435',
                              'F':'#FEBAAD',
                                 'T':'#E97451'}, height=200,hole=0.3)

        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if len(dff_today_emg_graph['count_emg']) == 1:
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    

    return(fig)


#callback and sql query for today's report graph in hospital wise statistics-------------------------------------------


@app.callback(Output(component_id='today_report', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,n_intervals):
    df_all = pd.read_sql_query(
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
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name" ''', conn)


    today_report_graph=pd.read_sql_query('''

    SELECT COUNT
        ( * ) AS count_reports,
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hivt_requisition_dtl" 
    WHERE 
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" = "ahiscl"."hivt_requisition_dtl"."gnum_hospital_code" AND
    "ahiscl"."hivt_requisition_dtl"."hivnum_reqdtl_status" IN ( 14, 26 ) AND trunc("ahiscl"."hivt_requisition_dtl"."hivt_entry_date") = trunc(sysdate)
    GROUP BY
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"

    UNION
    SELECT COUNT
        ( * ) AS count_reports,
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" 
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hivt_requisition_dtl" 
    WHERE 
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" = "ahiscl"."hivt_requisition_dtl"."gnum_hospital_code" AND
    "ahiscl"."hivt_requisition_dtl"."hivnum_reqdtl_status" IN ( 13)  AND trunc("ahiscl"."hivt_requisition_dtl"."hivt_entry_date") = trunc(sysdate)
    GROUP BY
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" 
                
                
     ''',conn)

    frames_today_report=[df_all,today_report_graph]

    df_today_report=pd.concat(frames_today_report)

    
    dff_today_report_graph = df_today_report[df_today_report['gstr_hospital_name'] == selected_hospital_name]
    # print(dff_emg)
    colors=['#FBE870','#CF9FFF']

    if len(dff_today_report_graph['count_reports']) > 1:
        fig = px.pie(dff_today_report_graph, values="count_reports", names="count_reports", height=200,hole=0.3)

        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})
        fig.update_traces(
                  marker=dict(colors=colors))

    if len(dff_today_report_graph['count_reports']) == 1:
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    

    return(fig)

#callback and sql query for total opd count in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='opd_count', component_property='children'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,n_intervalss):


    df_opd_count=pd.read_sql_query('''
          
        SELECT "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
   COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_opd
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <>134
    
    GROUP BY "ahiscl"."gblt_hospital_mst"."gstr_hospital_name", "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
    
    
      union
            
        select "ahiscl"."gblt_hospital_mst"."gnum_hospital_code", "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",0 from "ahiscl"."gblt_hospital_mst" where "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" not in(
                
                SELECT "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
        
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <>134
    
    GROUP BY  "ahiscl"."gblt_hospital_mst"."gnum_hospital_code")''',conn)

   
    df_filtered = df_opd_count[df_opd_count['gstr_hospital_name'] == selected_hospital_name]
    

    return (df_filtered.count_opd)

#callback and sql query for total emg count in hospital wise statistics-------------------------------------------
 
@app.callback(Output(component_id='emg_count', component_property='children'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,n_intervals):

    df_emg_count=pd.read_sql_query('''SELECT "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
   COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_emg
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" =134
    
    GROUP BY "ahiscl"."gblt_hospital_mst"."gstr_hospital_name", "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
    
    
      union
            
        select "ahiscl"."gblt_hospital_mst"."gnum_hospital_code", "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",0 from "ahiscl"."gblt_hospital_mst" where "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" not in(
                
                SELECT "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
        
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" = 134
    
    GROUP BY  "ahiscl"."gblt_hospital_mst"."gnum_hospital_code")''',conn)
       
    df_filtered = df_emg_count[df_emg_count['gstr_hospital_name'] == selected_hospital_name]


    
   
    # return (df_filtered)
    return (df_filtered.count_emg)

#callback and sql query for total adm count in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='adm_count', component_property='children'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,n_intervals):

    df_adm_count=pd.read_sql_query('''
   
        SELECT 

            "ahiscl"."gblt_hospital_mst"."gstr_hospital_name" ,COUNT
            ( "ahiscl"."hipt_patadmission_dtl".hipnum_admno ) as count_adm
        FROM
            "ahiscl"."hipt_patadmission_dtl",
            "ahiscl"."gblt_hospital_mst" 
        WHERE
            "ahiscl"."gblt_hospital_mst".gnum_hospital_code = "ahiscl"."hipt_patadmission_dtl".gnum_hospital_code  AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 AND "ahiscl"."hipt_patadmission_dtl"."gnum_isvalid" = 1 
            AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
        GROUP BY
            "ahiscl"."gblt_hospital_mst"."gstr_hospital_name"  union
                    
                select  "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",0 from "ahiscl"."gblt_hospital_mst" where "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" not in ( SELECT "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
            
        FROM
            "ahiscl"."hipt_patadmission_dtl",
            "ahiscl"."gblt_hospital_mst" 
        WHERE
            "ahiscl"."gblt_hospital_mst".gnum_hospital_code = "ahiscl"."hipt_patadmission_dtl".gnum_hospital_code  AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 AND "ahiscl"."hipt_patadmission_dtl"."gnum_isvalid" = 1 
            AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
        GROUP BY 
            "ahiscl"."gblt_hospital_mst"."gnum_hospital_code")
    ''',conn)
   
    df_filtered = df_adm_count[df_adm_count['gstr_hospital_name'] == selected_hospital_name]


    return (df_filtered.count_adm)

#callback and sql query for total report count in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='report_count', component_property='children'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,n_intervals):

    df_report_count=pd.read_sql_query('''
    SELECT
          
         "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
            
           COUNT(*) AS count_reports
    FROM "ahiscl"."gblt_hospital_mst",
    "ahiscl"."hivt_requisition_dtl" 

    WHERE
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" = "ahiscl"."hivt_requisition_dtl"."gnum_hospital_code" AND
    "ahiscl"."hivt_requisition_dtl"."hivnum_reqdtl_status" IN ( 14, 26,13 ) 
    GROUP BY"ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name"
                
                
                
                union
            
        select gnum_hospital_code , "gstr_hospital_name",0 from gblt_hospital_mst where gnum_hospital_code not in(
                
                SELECT
          
         "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
       
            
       
    FROM "ahiscl"."gblt_hospital_mst",
    "ahiscl"."hivt_requisition_dtl" 

    WHERE
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" = "ahiscl"."hivt_requisition_dtl"."gnum_hospital_code" AND
    "ahiscl"."hivt_requisition_dtl"."hivnum_reqdtl_status" IN ( 14, 26,13 )
    GROUP BY"ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name")''',conn)
   
    df_filtered = df_report_count[df_report_count['gstr_hospital_name'] == selected_hospital_name]


    return (df_filtered.count_reports)

#callback and sql query for total opd graph in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='graph_opd', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,n_intervals):


    df_all = pd.read_sql_query(
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
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name" ''', conn)

    df_opd_graph=pd.read_sql_query('''SELECT "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name", 
                "ahiscl"."hrgt_patient_dtl"."gstr_gender_code"  AS gender,
   COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_opd
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <>134
    
    GROUP BY "ahiscl"."gblt_hospital_mst"."gstr_hospital_name", "ahiscl"."gblt_hospital_mst"."gnum_hospital_code", "ahiscl"."hrgt_patient_dtl"."gstr_gender_code" 
        
    ''',conn)

    frames8=[df_all,df_opd_graph]
    df19=pd.concat(frames8)




    
    dff_opd= df19[df19['gstr_hospital_name'] == selected_hospital_name] 
    

    if len(dff_opd['count_opd']) > 1:
        fig=px.pie(dff_opd, values="count_opd", names="gender",color='gender',color_discrete_map={'M':'#008000',
                                 'F':'#93C572',
                                 'T':'#98FB98'}, height=200,hole=0.3)

        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if len(dff_opd['count_opd']) == 1:

        fig=go.Figure()
        fig.update_layout({
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    

    return(fig)

#callback and sql query for total adm graph in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='graph_adm', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,n_intervals):

    df_all = pd.read_sql_query(
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


    df_adm_graph=pd.read_sql_query('''
            
        SELECT COUNT
            ( "ahiscl"."hipt_patadmission_dtl".hipnum_admno ) as count_adm,
            "ahiscl"."hipt_patadmission_dtl"."hrgstr_sex" AS gender,
            "ahiscl"."gblt_hospital_mst"."gstr_hospital_name" 
        FROM
            "ahiscl"."hipt_patadmission_dtl",
            "ahiscl"."gblt_hospital_mst" 
        WHERE
            "ahiscl"."gblt_hospital_mst".gnum_hospital_code = "ahiscl"."hipt_patadmission_dtl".gnum_hospital_code AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 AND "ahiscl"."hipt_patadmission_dtl"."gnum_isvalid" = 1 
            AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
        GROUP BY
            "ahiscl"."hipt_patadmission_dtl"."hrgstr_sex",
            "ahiscl"."gblt_hospital_mst"."gstr_hospital_name"''',conn)

    frames_adm = [df_all,df_adm_graph]

    df_adm_concat=pd.concat(frames_adm)
    
    dff_adm = df_adm_concat[df_adm_concat['gstr_hospital_name'] == selected_hospital_name]


    if len(dff_adm['count_adm']) > 1:
        
        fig= px.pie(dff_adm, values="count_adm", names="gender",color='gender',color_discrete_map={'M':'#D2042D',
                                 'F':'#F88379',
                                 'T':'#FEBAAD'},height=200,hole=0.3)

        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if len(dff_adm['count_adm']) == 1:

        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found !",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]
    }),
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found !",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]
    })


    
    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    return(fig)

#callback and sql query for total emg graph in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='graph_emg', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,n_intervals):

    df_all = pd.read_sql_query(
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
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name" ''', conn)



    df_emg_graph=pd.read_sql_query('''
    SELECT "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name", 
                "ahiscl"."hrgt_patient_dtl"."gstr_gender_code"  AS gender,
   COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_emg
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21  
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" =134
    
    GROUP BY "ahiscl"."gblt_hospital_mst"."gstr_hospital_name", "ahiscl"."gblt_hospital_mst"."gnum_hospital_code", "ahiscl"."hrgt_patient_dtl"."gstr_gender_code" 
        
    ''',conn)

    frames_emg=[df_all,df_emg_graph]

    df_emg_concat=pd.concat(frames_emg)
    
    dff_emg = df_emg_concat[df_emg_concat['gstr_hospital_name'] == selected_hospital_name]
    # print(dff_emg)

    if len(dff_emg['count_emg']) > 1:
        fig = px.pie(dff_emg, values="count_emg", names="gender",color='gender',color_discrete_map={'M':'#C04000',
                                 'F':'#F4BB44',
                                 'T':'#FFD580'},height=200 ,hole=0.3)

        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if len(dff_emg['count_emg']) == 1:
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    

    return(fig)

#callback and sql query for total report graph in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='graph_reports', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,n_intervals):

    df_all = pd.read_sql_query(
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


    df_reports_graph=pd.read_sql_query('''
    SELECT COUNT
        ( * ) AS count_reports,
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hivt_requisition_dtl" 
    WHERE 
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" = "ahiscl"."hivt_requisition_dtl"."gnum_hospital_code" AND
    "ahiscl"."hivt_requisition_dtl"."hivnum_reqdtl_status" IN ( 14, 26 ) 
    GROUP BY
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"

    UNION
    SELECT COUNT
        ( * ) AS count_reports,
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" 
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hivt_requisition_dtl" 
    WHERE 
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" = "ahiscl"."hivt_requisition_dtl"."gnum_hospital_code" AND
    "ahiscl"."hivt_requisition_dtl"."hivnum_reqdtl_status" IN ( 13) 
    GROUP BY
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" 

    ''',conn)


    frames_df=[df_all,df_reports_graph]

    df_reports=pd.concat(frames_df)
    
    dff_reports = df_reports[df_reports['gstr_hospital_name'] == selected_hospital_name]
    colors = ['#5F9EA0','#0047AB']
    # print(dff_emg)

    if len(dff_reports['count_reports']) > 1:
        fig = px.pie(dff_reports, values="count_reports", names="count_reports", height=200,hole=0.3)

        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})
        fig.update_traces(
                  marker=dict(colors=colors))

    if len(dff_reports['count_reports']) == 1:
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    

    return(fig)

#callback and sql query for department graph in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='graph_department', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,n_intervals):


    df_all = pd.read_sql_query(
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

    df_department = pd.read_sql_query(
    '''SELECT COUNT
        ( * ) AS count,
        "ahiscl"."gblt_department_mst"."gstr_dept_name" AS department,
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
        "ahiscl"."hrgt_episode_dtl"."gnum_dept_code"
         
    FROM
        "ahiscl"."gblt_department_mst",
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl" 
    WHERE
        "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" = "ahiscl"."gblt_department_mst"."gnum_hospital_code" 
        AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" = "ahiscl"."gblt_department_mst"."gnum_dept_code" 
    GROUP BY
        "ahiscl"."gblt_department_mst"."gstr_dept_name","ahiscl"."gblt_hospital_mst"."gnum_hospital_code","ahiscl"."gblt_hospital_mst"."gstr_hospital_name","ahiscl"."hrgt_episode_dtl"."gnum_dept_code"''',conn)


    frames1 = [df_all,df_department]

    # frames = [df1,df2,df3]

    df = pd.concat(frames1)
   
    dff_department = df[df['gstr_hospital_name'] == selected_hospital_name]

  
    if len(dff_department['department']) > 1:
        fig=px.bar(dff_department, x="department", y="count", barmode="group",color="department",text="count",labels={
                             "department": "Department",
                             "count": " Count",
                             
                         })
        fig.update_layout({
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',})

    if len(dff_department['department']) == 1:    
        fig=go.Figure()
        fig.update_layout({
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "No data found!",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                     
                        "font": {
                            "size": 20
                        }
                    }
                ]})

    fig.update_traces(textfont_size=12, textangle=0, textposition="outside",width=0.8)
    fig.update_layout(uniformtext_minsize=8)

    
    return(fig)
       
#callback and sql query for date wise opd count in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='graph_datewise_opdcount', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input(component_id='my_dropdown2', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,selected_graph,n_intervals):

    df_all = pd.read_sql_query(
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




    df4= pd.read_sql_query('''   SELECT
            to_char( "ahiscl"."hrgt_episode_dtl".gdt_entry_date, 'DD-Mon-yyyy' ) AS months,
            "ahiscl"."gblt_hospital_mst"."gnum_hospital_code","ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
            COUNT ( "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" ) AS opd 
        FROM
            "ahiscl"."gblt_hospital_mst",
            "ahiscl"."hrgt_episode_dtl" 
        WHERE
            "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" = "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" 
            AND "ahiscl"."hrgt_episode_dtl"."gnum_isvalid" = 1 
            AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
            AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1 
            AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <> 134 
            AND to_char( trunc( hrgt_episode_dtl.gdt_entry_date ), 'Mon-yyyy' ) = to_char( sysdate, 'Mon-yyyy' )
        GROUP BY
            to_char( "ahiscl"."hrgt_episode_dtl".gdt_entry_date, 'DD-Mon-yyyy' ),
            "ahiscl"."gblt_hospital_mst"."gnum_hospital_code","ahiscl"."gblt_hospital_mst"."gstr_hospital_name"
                        
         ''',conn)


    frames_date_opd=[df_all,df4]

    df_date_opd=pd.concat(frames_date_opd)
    fig=go.Figure()
   
   
    dff_date_opd= df_date_opd[df_date_opd['gstr_hospital_name'] == selected_hospital_name] 
    # print(dff_date_opd)

    if len(dff_date_opd['opd']) > 1:
        fig=go.Figure()
        if(selected_graph) == 'Bar Graph':
            fig=px.bar(dff_date_opd, x="months", y="opd",color='opd',text='opd',labels={
                         "months": "Dates",
                         "opd": "Count"})
            fig.update_traces(textfont_size=10,  width=0.4,textposition="outside")
        
        if(selected_graph) == 'Pie Graph':
            fig = px.pie(dff_date_opd, values="opd", names="months")
            fig.update_traces(textfont_size=10,  textposition="outside")

        if(selected_graph) == 'Donut Graph':
            fig = px.pie(dff_date_opd, labels="months", values="opd",hole=0.3)

       
        if(selected_graph) == 'Area Graph':
            fig = px.area(dff_date_opd, x="months", y="opd")
        fig.update_layout({
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',})

    if len(dff_date_opd['opd'])==1:
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found !",
                "xref": "paper",
                "yref": "paper","showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]
        })
    # fig.update_traces(textfont_size=12,  textposition="outside")
    return(fig)

#callback and sql query for date wise casuality count in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='graph_datewise_casualitycount', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input(component_id='my_dropdown3', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,selected_graph,n_intervals):


    df_all = pd.read_sql_query(
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
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name"
    ''', conn)

    df5=pd.read_sql_query(''' SELECT
            to_char( "ahiscl"."hrgt_episode_dtl".gdt_entry_date, 'DD-Mon-yyyy' ) AS months,
            "ahiscl"."gblt_hospital_mst"."gnum_hospital_code","ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
            COUNT ( "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" ) AS opd 
        FROM
            "ahiscl"."gblt_hospital_mst",
            "ahiscl"."hrgt_episode_dtl" 
        WHERE
            "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" = "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" 
            AND "ahiscl"."hrgt_episode_dtl"."gnum_isvalid" = 1 
            AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
       
            AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" = 134 
            AND to_char( trunc( hrgt_episode_dtl.gdt_entry_date ), 'Mon-yyyy' ) = to_char( sysdate, 'Mon-yyyy' )
        GROUP BY
            to_char( "ahiscl"."hrgt_episode_dtl".gdt_entry_date, 'DD-Mon-yyyy' ),
            "ahiscl"."gblt_hospital_mst"."gnum_hospital_code","ahiscl"."gblt_hospital_mst"."gstr_hospital_name"
    ''',conn)


    frames3=[df_all,df5]

    df13=pd.concat(frames3)

    dff4= df13[df13['gstr_hospital_name'] == selected_hospital_name] 

    fig=go.Figure()

    # frames2 = [rows, dff]
    # dff_month=pd.concat(frames2)
    if len(dff4['opd']) > 1:

        

        if(selected_graph) == 'Bar Graph':
            fig=px.bar(dff4, x="months", y="opd",color='opd',text='opd',labels={
                         "months": "Dates",
                         "opd": " Count",
                         
                     })
            fig.update_traces(textfont_size=10,  width=0.4,textposition="outside")
        
        if(selected_graph) == 'Pie Graph':
            fig = px.pie(dff4, values="opd", names="months")
            fig.update_traces(textfont_size=10)

        if(selected_graph) == 'Donut Graph':
            fig = px.pie(dff4, labels="months", values="opd",hole=0.3)

        if(selected_graph) == 'Semi-Donut Graph':
            fig = px.pie(dff4, labels="months", values="opd",hole=0.3, rotation=90)

        if(selected_graph) == 'Area Graph':
            fig = px.area(dff4, x="months", y="opd")
            fig.update_traces(textfont_size=10)

        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if len(dff4['opd']) == 1:
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found !",
                "xref": "paper",
                "yref": "paper","showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]
        })

    # fig.update_traces(textfont_size=10, textposition="outside")

    return(fig)

#callback and sql query for months wise opd count in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='graph_month_opdcount', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,n_intervals):

    df_all = pd.read_sql_query(
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

    df_current_month_opd=pd.read_sql_query('''SELECT
    DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) AS months,
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
     COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_opd 
FROM
    "ahiscl"."gblt_hospital_mst",
    "ahiscl"."hrgt_patient_dtl" ,"ahiscl"."hrgt_episode_dtl"
WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <>134
    AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) = EXTRACT ( YEAR FROM now( ) ) 
GROUP BY
    DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ),
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name"
                ''',conn)


    frames4=[df_all,df_current_month_opd]

    df14=pd.concat(frames4)
       
    dff5 = df14[df14['gstr_hospital_name'] == selected_hospital_name]

    if len(dff5['count_opd']) > 1:
        fig=px.bar(dff5, x="months", y="count_opd", barmode="group",text="count_opd",color="count_opd",labels={
                     "months": "Months",
                     "count_opd": " Count",
                     
                 })
        # barchart1 = px.bar(filtered_df, x = "emg_count",y = "gstr_hospital_name", title="Hospital list")
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        })

    if len(dff5['count_opd']) == 1:
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found !",
                "xref": "paper",
                "yref": "paper","showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]
        })



    
    fig.update_traces(textfont_size=10, textangle=0, textposition="outside")


    return(fig)

#callback and sql query for months wise casuality count in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='graph_month_casualitycount', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,n_intervals):


    df_all = pd.read_sql_query(
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

    df7=pd.read_sql_query('''
           SELECT
    DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) AS months,
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
     COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_opd 
FROM
    "ahiscl"."gblt_hospital_mst",
    "ahiscl"."hrgt_patient_dtl" ,"ahiscl"."hrgt_episode_dtl"
WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" =134
    AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) = EXTRACT ( YEAR FROM now( ) ) 
GROUP BY
    DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ),
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name"
                ''',conn)

    frames5=[df_all,df7]

    df15=pd.concat(frames5)
   
    dff6 = df15[df15['gstr_hospital_name'] == selected_hospital_name]

    if len(dff6['count_opd']) > 1:
        fig=px.bar(dff6, x="months", y="count_opd", barmode="group",text="count_opd",color="count_opd",labels={
                     "months": "Months",
                     "count_opd": "Count",
                     
                 })
        # barchart1 = px.bar(filtered_df, x = "emg_count",y = "gstr_hospital_name", title="Hospital list")
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if len(dff6['count_opd']) == 1:
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found !",
                "xref": "paper",
                "yref": "paper","showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]
        })

    fig.update_traces(textfont_size=12, textangle=0, textposition="outside")

    return(fig)

#callback and sql query for months wise opd statistics in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='graph_month_opdgender', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,intervals):

    df_all = pd.read_sql_query(
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
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name" ''', conn)

    df8=pd.read_sql_query('''
        SELECT
    DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) AS months,
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
    "ahiscl"."hrgt_patient_dtl"."gstr_gender_code" AS gender,
    COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_opd
FROM
    "ahiscl"."gblt_hospital_mst",
    "ahiscl"."hrgt_patient_dtl" ,"ahiscl"."hrgt_episode_dtl"
WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <>134 
    AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) = EXTRACT ( YEAR FROM now( ) ) 
GROUP BY
    DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ),
    "ahiscl"."hrgt_patient_dtl"."gstr_gender_code",
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name"
    ''',conn)


    frames6=[df_all,df8]

    df16=pd.concat(frames6)
   
    dff10 = df16[df16['gstr_hospital_name'] == selected_hospital_name]
     
     #define go.Figure() whenever an error occurs

    if len(dff10['count_opd']) > 1:
        fig=px.bar(dff10, x="months", y="count_opd", barmode="group",text="count_opd",color="gender",labels={
                     "months": "Months",
                     "count_opd": "Count",
                     
                 })
        # barchart1 = px.bar(filtered_df, x = "emg_count",y = "gstr_hospital_name", title="Hospital list")
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if len(dff10['count_opd']) == 1:
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)', "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found !",
                "xref": "paper",
                "yref": "paper","showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]
        })



   
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside")


    return(fig)

#callback and sql query for months wise casuality statistics in hospital wise statistics-------------------------------------------

@app.callback(Output(component_id='graph_month_casualitygender', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_hospital_name,intervals):

    df_all = pd.read_sql_query(
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
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name" ''', conn)

    df9=pd.read_sql_query('''
        SELECT
    DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) AS months,
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name",
    "ahiscl"."hrgt_patient_dtl"."gstr_gender_code" AS gender,
    COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_opd
FROM
    "ahiscl"."gblt_hospital_mst",
    "ahiscl"."hrgt_patient_dtl" ,"ahiscl"."hrgt_episode_dtl"
WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" =134 
    AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) = EXTRACT ( YEAR FROM now( ) ) 
GROUP BY
    DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ),
    "ahiscl"."hrgt_patient_dtl"."gstr_gender_code",
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code",
    "ahiscl"."gblt_hospital_mst"."gstr_hospital_name"''',conn)

    frames7=[df_all,df9]

    df_casuality_stats=pd.concat(frames7)
       
    dff_month_casuality_stats =df_casuality_stats[df_casuality_stats['gstr_hospital_name'] == selected_hospital_name]
    # print(dff_month_casuality_stats)

    if len(dff_month_casuality_stats['count_opd']) > 1:
        fig=px.bar(dff_month_casuality_stats, x="months", y="count_opd", barmode="group",text="count_opd",color="gender",labels={
                     "months": "Months",
                     "count_opd": "Count",
                     
                     
                 })
        # barchart1 = px.bar(filtered_df, x = "emg_count",y = "gstr_hospital_name", title="Hospital list")
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if len(dff_month_casuality_stats['count_opd']) == 1:
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)', "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found !",
                "xref": "paper",
                "yref": "paper","showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]
        })



   
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside")


    return(fig)


#**********************************************************************************************************************************************


#**************************************************************OVERALL ODISHA HOSPITAL COUNTS***************************


#callback for todays opd count in total count page ---------------------------------------------------------

@app.callback(Output(component_id='today_total_opd', component_property='children'),
    [Input(component_id='my_dropdown',component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):


    today_total_opd=pd.read_sql_query(f'''
                  
        SELECT 
            COUNT(NULLIF("ahiscl"."hrgt_patient_dtl"."hrgnum_puk",0)) AS count_opd
        FROM
            "ahiscl"."hrgt_episode_dtl",
            "ahiscl"."gblt_hospital_mst",
            "ahiscl"."hrgt_patient_dtl" 
        WHERE
            "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk"

            AND trunc( "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) = trunc( sysdate )
                AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) ={selected_year}
            AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
            AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
            AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <> 134 AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1
            AND "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
          ''',conn)

    

    return (today_total_opd.count_opd)

#callback for todays admission count in total count page ---------------------------------------------------------

@app.callback(Output(component_id='today_total_adm', component_property='children'),
    [Input(component_id='my_dropdown',component_property='value')],
    
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):


    today_total_adm=pd.read_sql_query(f'''
          
     
     
        SELECT 
            COUNT(NULLIF("ahiscl"."hipt_patadmission_dtl"."hipnum_admno",0)) AS count_adm
        FROM
            "ahiscl"."hipt_patadmission_dtl",
            "ahiscl"."gblt_hospital_mst"
        WHERE
            
            trunc( "ahiscl"."hipt_patadmission_dtl"."hipdt_admdatetime" ) = trunc( sysdate )
            AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
            AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1     AND EXTRACT ( YEAR FROM "ahiscl"."hipt_patadmission_dtl"."hipdt_admdatetime" ) ={selected_year}

            AND "ahiscl"."hipt_patadmission_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
          ''',conn)

    

    return (today_total_adm.count_adm)

#callback for todays emergency count in total count page ---------------------------------------------------------

@app.callback(Output(component_id='today_total_emg', component_property='children'),
    [Input(component_id='my_dropdown',component_property='value')],
    
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):


    today_total_emg=pd.read_sql_query(f'''
          
        SELECT 
        COUNT(NULLIF("ahiscl"."hrgt_patient_dtl"."hrgnum_puk",0)) AS count_emg
    FROM
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
        "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk"
        AND trunc( "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) = trunc( sysdate )
        AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) ={selected_year}
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
        AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" = 134
        AND "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
      ''',conn)

    

    return (today_total_emg.count_emg)

#callback for todays report count in total count page ---------------------------------------------------------

@app.callback(Output(component_id='today_total_report', component_property='children'),
    [Input(component_id='my_dropdown',component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):


    today_total_report=pd.read_sql_query(f'''
          
        
        SELECT
            
            COUNT(NULLIF("ahiscl"."hivt_requisition_dtl"."hivtnum_req_dno",0)) AS count_reports
    FROM "ahiscl"."gblt_hospital_mst",
    "ahiscl"."hivt_requisition_dtl" 

    WHERE
        EXTRACT ( YEAR FROM "ahiscl"."hivt_requisition_dtl"."hivt_entry_date" ) ={selected_year} AND
    "ahiscl"."hivt_requisition_dtl"."hivnum_reqdtl_status" IN ( 14, 26,13 ) AND trunc("ahiscl"."hivt_requisition_dtl"."hivt_entry_date") = trunc(sysdate) AND "ahiscl"."hivt_requisition_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
                
                
               
  ''',conn)

    

    return (today_total_report.count_reports)

#callback for todays opd graph in total count page ---------------------------------------------------------

@app.callback(Output(component_id='today_opd_graph', component_property='figure'),
    [Input(component_id='my_dropdown',component_property='value')],
   
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):
   
    today_opd_graph=pd.read_sql_query(f'''
    
    
    SELECT
        "ahiscl"."hrgt_patient_dtl"."gstr_gender_code" AS gender,
        COUNT ( "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" ) AS count_opd 
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_patient_dtl",
        "ahiscl"."hrgt_episode_dtl" 
    WHERE
        "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
            AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) ={selected_year}
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
        AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
        AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1 
        AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <> 134 AND "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
        AND trunc( "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) = trunc( sysdate ) 
    GROUP BY
        "ahiscl"."hrgt_patient_dtl"."gstr_gender_code" 
    ''',conn)

   
    # print(today_opd_graph['count_opd'])


    if len(today_opd_graph['count_opd']):
        fig = px.pie(today_opd_graph, values="count_opd",color='gender',color_discrete_map={'M':'#f8ed62',
                                 'F':'#dab600',
                                 'T':'#EEDC82'}, names="gender", height=200,hole=0.3)

        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if not len(today_opd_graph['count_opd']) :
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))


    return(fig)

#callback for todays emergency graph in total count page ---------------------------------------------------------

@app.callback(Output(component_id='today_emg_graph', component_property='figure'),
    [Input(component_id='my_dropdown',component_property='value')],
   
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):
   
    today_emg_graph=pd.read_sql_query(f'''
    SELECT
        "ahiscl"."hrgt_patient_dtl"."gstr_gender_code" AS gender,
        COUNT ( "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" ) AS count_emg 
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_patient_dtl",
        "ahiscl"."hrgt_episode_dtl" 
    WHERE
        "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
        AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
        AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) ={selected_year}
        AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" = 134 AND "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
        AND trunc( "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) = trunc( sysdate ) 
    GROUP BY
        "ahiscl"."hrgt_patient_dtl"."gstr_gender_code"  
    ''',conn)

   
    # print(today_emg_graph['count_emg'])


    if len(today_emg_graph['count_emg']):
        fig = px.pie(today_emg_graph, values="count_emg",color='gender',color_discrete_map={'M':'#CA3435',
                                 'F':'#FEBAAD',
                                 'T':'#E97451'}, names="gender", height=200,hole=0.3)

        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if not len(today_emg_graph['count_emg']) :
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))


    return(fig)

#callback for todays report graph in total count page ---------------------------------------------------------

@app.callback(Output(component_id='today_reportgraph', component_property='figure'),
    [Input(component_id='my_dropdown',component_property='value')],
   
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):


    

    today_report_graph=pd.read_sql_query(f'''
         SELECT COUNT
            ( * ) AS count_reports 
        FROM
            "ahiscl"."gblt_hospital_mst",
            "ahiscl"."hivt_requisition_dtl" 
        WHERE
            "ahiscl"."hivt_requisition_dtl"."hivnum_reqdtl_status" IN ( 14, 26 )
                AND EXTRACT ( YEAR FROM "ahiscl"."hivt_requisition_dtl"."hivt_entry_date" ) ={selected_year} AND "ahiscl"."hivt_requisition_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
            AND trunc( "ahiscl"."hivt_requisition_dtl"."hivt_entry_date" ) = trunc( sysdate ) UNION
        SELECT COUNT
            ( * ) AS count_reports 
        FROM
            "ahiscl"."gblt_hospital_mst",
            "ahiscl"."hivt_requisition_dtl" 
        WHERE
            "ahiscl"."hivt_requisition_dtl"."hivnum_reqdtl_status" IN ( 13 ) 
                AND EXTRACT ( YEAR FROM "ahiscl"."hivt_requisition_dtl"."hivt_entry_date" ) ={selected_year} AND "ahiscl"."hivt_requisition_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
            AND trunc( "ahiscl"."hivt_requisition_dtl"."hivt_entry_date" ) = trunc( sysdate )
    ''',conn)

    # print(today_report_graph['count_reports'])
    colors=['#FBE870','#CF9FFF']
    fig=go.Figure()


   
    if len(today_report_graph['count_reports']) > 1:
        fig=px.pie(today_report_graph, values="count_reports", names="count_reports", height=200,hole=0.3)
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    fig.update_traces(
                  marker=dict(colors=colors))

    if len(today_report_graph['count_reports']) == 1:

        fig=go.Figure()
        fig.update_layout({
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    

    return(fig)

#callback for total admisssion count in total count page ---------------------------------------------------------

@app.callback(Output(component_id='total_adm_count', component_property='children'),
    [Input(component_id='my_dropdown',component_property='value')],

    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):


    df_filtered=pd.read_sql_query(f'''
          
        
        SELECT COUNT(NULLIF("ahiscl"."hipt_patadmission_dtl"."hipnum_admno",0)) AS count_adm
        FROM
            "ahiscl"."hipt_patadmission_dtl",
            "ahiscl"."gblt_hospital_mst" 
        WHERE
          "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 AND "ahiscl"."hipt_patadmission_dtl"."gnum_isvalid" = 1
          AND EXTRACT ( YEAR FROM "ahiscl"."hipt_patadmission_dtl"."hipdt_admdatetime" ) ={selected_year} 
            AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21   AND "ahiscl"."hipt_patadmission_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
    ''',conn)

   
    

    return (df_filtered.count_adm)

#callback for total emergency count in total count page ---------------------------------------------------------

@app.callback(Output(component_id='total_emg_count', component_property='children'),
    [Input(component_id='my_dropdown',component_property='value')],
    
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):


    df_filtered=pd.read_sql_query(f'''
          
               
    SELECT 
    COUNT(NULLIF("ahiscl"."hrgt_patient_dtl"."hrgnum_puk",0)) AS count_emg
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
    
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
    AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) ={selected_year}
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" =134 AND "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
  ''',conn)

    

    return (df_filtered.count_emg)

#callback for total opd count in total count page ---------------------------------------------------------

@app.callback(Output(component_id='total_opd_count', component_property='children'),
    [Input(component_id='my_dropdown',component_property='value')],
    
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):


    df_filtered=pd.read_sql_query(f'''
          
        
    SELECT 
   COUNT(NULLIF("ahiscl"."hrgt_patient_dtl"."hrgnum_puk",0)) AS count_opd
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" AND "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
            AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) ={selected_year}
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <>134
        ''',conn)

    

    return (df_filtered.count_opd)

#callback for total report count in total count page ---------------------------------------------------------

@app.callback(Output(component_id='total_report_count', component_property='children'),
    [Input(component_id='my_dropdown',component_property='value')],

    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):


    df_filtered=pd.read_sql_query(f'''
          
    SELECT
    COUNT(NULLIF("ahiscl"."hivt_requisition_dtl"."hivtnum_req_dno",0)) AS count_reports

    FROM "ahiscl"."gblt_hospital_mst",
    "ahiscl"."hivt_requisition_dtl" 

    WHERE
        EXTRACT ( YEAR FROM "ahiscl"."hivt_requisition_dtl"."hivt_entry_date" ) ={selected_year} AND
      
    "ahiscl"."hivt_requisition_dtl"."hivnum_reqdtl_status" IN ( 14, 26,13 ) AND "ahiscl"."hivt_requisition_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
    ''',conn)
    return (df_filtered.count_reports)

#callback for total opd graph in total count page ---------------------------------------------------------

@app.callback(Output(component_id='total_graph_opd', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):


    total_opd_graph=pd.read_sql_query(f'''   
                        SELECT
                "ahiscl"."hrgt_patient_dtl"."gstr_gender_code"  AS gender,
   COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_opd
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
    "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" ="ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" AND "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" and
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <>134 AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) ={selected_year}
    
    GROUP BY  "ahiscl"."hrgt_patient_dtl"."gstr_gender_code"  
    ''',conn)
    

  

    if len(total_opd_graph['count_opd']):
        fig=px.pie(total_opd_graph, values="count_opd", names="gender",color='gender',color_discrete_map={'M':'#008000',
                                 'F':'#93C572',
                                 'T':'#98FB98'}, height=200,hole=0.3)
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if not len(total_opd_graph['count_opd']):

        fig=go.Figure()
        fig.update_layout({
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    

    return(fig)

#callback for total admission graph in total count page ---------------------------------------------------------

@app.callback(Output(component_id='total_graph_adm', component_property='figure'),
    [Input(component_id='my_dropdown',component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):

    total_adm_graph=pd.read_sql_query(f'''SELECT COUNT
            ( "ahiscl"."hipt_patadmission_dtl".hipnum_admno ) as count_adm,
            "ahiscl"."hipt_patadmission_dtl"."hrgstr_sex" AS gender
          
        FROM
            "ahiscl"."hipt_patadmission_dtl",
            "ahiscl"."gblt_hospital_mst" 
        WHERE
            "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 AND "ahiscl"."hipt_patadmission_dtl"."gnum_isvalid" = 1 
            AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21  AND "ahiscl"."hipt_patadmission_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
            AND EXTRACT ( YEAR FROM "ahiscl"."hipt_patadmission_dtl"."hipdt_admdatetime" ) ={selected_year}
                        
        GROUP BY
            "ahiscl"."hipt_patadmission_dtl"."hrgstr_sex"

    ''',conn)

   

    if len(total_adm_graph['count_adm']):
        fig=px.pie(total_adm_graph, values="count_adm", names="gender",color='gender',color_discrete_map={'M':'#D2042D',
                                 'F':'#F88379',
                                 'T':'#FEBAAD'}, height=200,hole=0.3)
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if not len(total_adm_graph['count_adm']) :

        fig=go.Figure()
        fig.update_layout({
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    

    return(fig)

#callback for total emergency graph in total count page ---------------------------------------------------------

@app.callback(Output(component_id='total_graph_emg', component_property='figure'),
    [Input(component_id='my_dropdown',component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):


    

    total_emg_graph=pd.read_sql_query(f'''  
         SELECT  
                "ahiscl"."hrgt_patient_dtl"."gstr_gender_code"  AS gender,
   COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_emg
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."hrgt_patient_dtl" 
    WHERE
    
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" =134  AND "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
    AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) = {selected_year}
    GROUP BY  "ahiscl"."hrgt_patient_dtl"."gstr_gender_code"
    ''',conn)

   
    if len(total_emg_graph['count_emg']):
        fig=px.pie(total_emg_graph, values="count_emg", names="gender",color='gender',color_discrete_map={'M':'#C04000',
                                 'F':'#F4BB44',
                                 'T':'#FFD580'}, height=200,hole=0.3)
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if not len(total_emg_graph['count_emg']) :

        fig=go.Figure()
        fig.update_layout({
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    

    return(fig)

#callback for total report graph in total count page ---------------------------------------------------------

@app.callback(Output(component_id='total_graph_report', component_property='figure'),
    [Input(component_id='my_dropdown',component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):


    

    total_report_graph=pd.read_sql_query(f'''        
                                SELECT COUNT
        ( * ) AS count_reports
        
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hivt_requisition_dtl" 
    WHERE 
    
    "ahiscl"."hivt_requisition_dtl"."hivnum_reqdtl_status" IN ( 14, 26 ) AND "ahiscl"."hivt_requisition_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
    AND EXTRACT ( YEAR FROM "ahiscl"."hivt_requisition_dtl"."hivt_entry_date" ) ={selected_year}

    UNION
    SELECT COUNT
        ( * ) AS count_reports
        
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hivt_requisition_dtl" 
    WHERE 
   
    "ahiscl"."hivt_requisition_dtl"."hivnum_reqdtl_status" IN ( 13) AND "ahiscl"."hivt_requisition_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
    AND EXTRACT ( YEAR FROM "ahiscl"."hivt_requisition_dtl"."hivt_entry_date" ) ={selected_year}
        
    ''',conn)

   
    colors = ['#5F9EA0','#0047AB']


    if len(total_report_graph['count_reports']) > 1:
        fig=px.pie(total_report_graph, values="count_reports", height=200,hole=0.3)
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

        fig.update_traces(
                  marker=dict(colors=colors))

    if len(total_report_graph['count_reports']) == 1:

        fig=go.Figure()
        fig.update_layout({
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    

    return(fig)

#callback for todays admission graph in total count page ---------------------------------------------------------

@app.callback(Output(component_id='today_adm_graph', component_property='figure'),
    [Input(component_id='my_dropdown',component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):
   
    today_adm_graph=pd.read_sql_query(f'''
    SELECT COUNT
            ( "ahiscl"."hipt_patadmission_dtl".hipnum_admno ) as count_adm,
            "ahiscl"."hipt_patadmission_dtl"."hrgstr_sex" AS gender
            
        FROM
            "ahiscl"."hipt_patadmission_dtl",
            "ahiscl"."gblt_hospital_mst" 
        WHERE
            "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1  AND EXTRACT ( YEAR FROM "ahiscl"."hipt_patadmission_dtl"."hipdt_admdatetime" ) ={selected_year} AND "ahiscl"."hipt_patadmission_dtl"."gnum_isvalid" = 1 
            AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND "ahiscl"."hipt_patadmission_dtl"."gnum_hospital_code" = "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"
            AND trunc( "ahiscl"."hipt_patadmission_dtl".hipdt_admdatetime ) = trunc( sysdate ) 
        GROUP BY
            "ahiscl"."hipt_patadmission_dtl"."hrgstr_sex"
          
    ''',conn)

   
    # print(today_adm_graph['count_adm'])


    if len(today_adm_graph['count_adm']):
        fig = px.pie(today_adm_graph, values="count_adm",color='gender',color_discrete_map={'M':'#E1C16E',
                                 'F':'#6E260E',
                                 'T':'#E97451'}, names="gender", height=200,hole=0.3)

        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if not len(today_adm_graph['count_adm']) :
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found!",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]})

    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))


    return(fig)

#callback for month wise opd graph in total count page ---------------------------------------------------------

@app.callback(Output(component_id='total_month_opdcount', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,n_intervals):

    
    current_month_opd=pd.read_sql_query(f'''SELECT DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) AS months,
    
         COUNT
            ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_opd
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_patient_dtl" ,"ahiscl"."hrgt_episode_dtl"
    WHERE "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"="ahiscl"."hrgt_patient_dtl"."gnum_hospital_code" and 
        
      
             "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
            AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
        AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1
        AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <>134
        AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) ={selected_year}
    GROUP BY
        DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" )
       
                ''',conn)
    # print(current_month_opd)


    if len(current_month_opd['count_opd']) :
        fig=px.bar(current_month_opd, x="months", y="count_opd", barmode="group",text="count_opd",color="count_opd",labels={
                     "months": "Months",
                     "count_opd": " Count",
                     
                 })
        # barchart1 = px.bar(filtered_df, x = "emg_count",y = "gstr_hospital_name", title="Hospital list")
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if not len(current_month_opd['count_opd']) :
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found !",
                "xref": "paper",
                "yref": "paper","showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]
        })

    fig.update_traces(textfont_size=10, textangle=0, textposition="outside")

    return(fig)

#callback for month wise opd count ( gender wise ) in total count page ---------------------------------------------------------

@app.callback(Output(component_id='total_month_opdgender', component_property='figure'),
    [Input(component_id='my_dropdown',component_property='value')],
   
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):

    
    current_month_opdstats=pd.read_sql_query(f''' 
        SELECT
        DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) AS months,
        
        "ahiscl"."hrgt_patient_dtl"."gstr_gender_code" AS gender,
        COUNT
            ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_opd
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_patient_dtl" ,"ahiscl"."hrgt_episode_dtl"
    WHERE "ahiscl"."gblt_hospital_mst"."gnum_hospital_code"="ahiscl"."hrgt_patient_dtl"."gnum_hospital_code" and 
       
             "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
            AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1  AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) ={selected_year}
        AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 AND "ahiscl"."hrgt_episode_dtl"."hrgnum_visit_type" = 1
        AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" <>134 
        
    GROUP BY
        DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ),
        "ahiscl"."hrgt_patient_dtl"."gstr_gender_code"
           
                ''',conn)


    if len(current_month_opdstats['count_opd']) :
        fig=px.bar(current_month_opdstats, x="months", y="count_opd", barmode="group",text="count_opd",color="gender",labels={
                     "months": "Months",
                     "count_opd": " Count",
                     
                 })
        # barchart1 = px.bar(filtered_df, x = "emg_count",y = "gstr_hospital_name", title="Hospital list")
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if not len(current_month_opdstats['count_opd']) :
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found !",
                "xref": "paper",
                "yref": "paper","showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]
        })

    fig.update_traces(textfont_size=10, textangle=0, textposition="outside")

    return(fig)

#callback for month wise casuality count in total count page ---------------------------------------------------------

@app.callback(Output(component_id='total_month_casualitycount', component_property='figure'),
    [Input(component_id='my_dropdown',component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):

    
    current_month_casualitycount=pd.read_sql_query(f'''SELECT
    DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) AS months,
   
         COUNT
            ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_opd 
    FROM
        "ahiscl"."gblt_hospital_mst",
        "ahiscl"."hrgt_patient_dtl" ,"ahiscl"."hrgt_episode_dtl"
    WHERE "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" = "ahiscl"."hrgt_patient_dtl"."gnum_hospital_code" and 
      
             "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
            AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
        AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21
        AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" =134
        AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) = {selected_year} 
    GROUP BY
        DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" )
                ''',conn)


    if len(current_month_casualitycount['count_opd']) :
        fig=px.bar(current_month_casualitycount, x="months", y="count_opd", barmode="group",text="count_opd",color="count_opd",labels={
                     "months": "Months",
                     "count_opd": " Count",
                     
                 })
        # barchart1 = px.bar(filtered_df, x = "emg_count",y = "gstr_hospital_name", title="Hospital list")
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if not len(current_month_casualitycount['count_opd']) :
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found !",
                "xref": "paper",
                "yref": "paper","showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]
        })

    fig.update_traces(textfont_size=10, textangle=0, textposition="outside")

    return(fig)

#callback for month wise casuality count ( gender wise ) in total count page ---------------------------------------------------------

@app.callback(Output(component_id='hosp_display', component_property='figure'),
    [Input(component_id='my_dropdown',component_property='value')],
    [Input('my_interval','n_intervals')])

def update_graph2(selected_year,intervals):

    
    current_month_casualitystats=pd.read_sql_query(f'''   
            SELECT
    DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) AS months,
    
    "ahiscl"."hrgt_patient_dtl"."gstr_gender_code" AS gender,
    COUNT
        ("ahiscl"."hrgt_patient_dtl"."hrgnum_puk") as count_opd
FROM
    "ahiscl"."gblt_hospital_mst",
    "ahiscl"."hrgt_patient_dtl" ,"ahiscl"."hrgt_episode_dtl"
WHERE "ahiscl"."gblt_hospital_mst"."gnum_hospital_code" = "ahiscl"."hrgt_patient_dtl"."gnum_hospital_code" and 
         "ahiscl"."hrgt_episode_dtl"."hrgnum_puk" = "ahiscl"."hrgt_patient_dtl"."hrgnum_puk" 
        AND "ahiscl"."gblt_hospital_mst"."gnum_isvalid" = 1 
    AND "ahiscl"."gblt_hospital_mst"."gnum_state_code" = 21 
    AND "ahiscl"."hrgt_episode_dtl"."gnum_dept_code" =134 
    AND EXTRACT ( YEAR FROM "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ) = {selected_year}
GROUP BY
    DATE_TRUNC( 'month', "ahiscl"."hrgt_patient_dtl"."gdt_entry_date" ),
    "ahiscl"."hrgt_patient_dtl"."gstr_gender_code"
       
                ''',conn)
    fig = go.Figure(layout=dict(template='plotly'))
 


    if len(current_month_casualitystats['count_opd']):
        fig=px.bar(current_month_casualitystats, x="months", y="count_opd", barmode="group",text="count_opd",color="gender",labels={
                     "months": "Months",
                     "count_opd": " Count",
                     
                 })
        # barchart1 = px.bar(filtered_df, x = "emg_count",y = "gstr_hospital_name", title="Hospital list")
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',})

    if not len(current_month_casualitystats['count_opd']) :
        fig=go.Figure()
        fig.update_layout({
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',"xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No data found !",
                "xref": "paper",
                "yref": "paper","showarrow": False,
             
                "font": {
                    "size": 20
                }
            }
        ]
        })

    fig.update_traces(textfont_size=10, textangle=0, textposition="outside")

    return(fig)

#####  MAP  callbacks ------------------------------------------------------------------------------------------
 
@app.callback(
    # dash.dependencies.Output(component_id='map', component_property='srcDoc'),
    # (dash.dependencies.Output(component_id='Required', component_property='value')),
    (dash.dependencies.Output(component_id='my_dropdown2',component_property='options')),
    # (dash.dependencies.Output(component_id='desktops',component_property='figure')),
    # (dash.dependencies.Output(component_id='printer',component_property='figure')),
    # (dash.dependencies.Output(component_id='ups',component_property='figure')),
    (dash.dependencies.Output(component_id='hosp-data-display',component_property='children')),
    [dash.dependencies.Input(component_id='my_checklist',component_property='value')],
    # [dash.dependencies.Input(component_id='my_checklist',component_property='text')],
    [dash.dependencies.Input(component_id='hosp-data-tabs',component_property='value')])
def update_hosp(selected_hosp_type, selected_tab):

    #coordinates of main odisha map
    # coordinates=(20.9517, 85.0985)

    ##plotting the map
    # orissa_map=folium.Map(location=coordinates,zoom_start=7,min_zoom=7,max_zoom=7,zoom_control=False,scrollWheelZoom=False, dragging=False)
    # orissa_map=folium.Map(location=coordinates,zoom_start=7)
    # marker_cluster=folium.plugins.MarkerCluster().add_to(orissa_map)

    # #map to be displayed when no radiobutton option is selected
    # if selected_hosp==None:
    #     orissa_map.save('maplocation.html')
    #     return open('maplocation.html','r').read()

    #map to be displayed when a radiobutton option is selected(including the default option of radiobutton that is selected)
    # elif selected_hosp!= None:
    checklistmap=pd.read_sql_query(f'''SELECT
        COUNT
        ("ahiscl"."hrgt_episode_dtl"."hrgnum_puk") as count ,
        "ahiscl"."gblt_hospital_mst_copy1"."latitude" AS latitude,
        "ahiscl"."gblt_hospital_mst_copy1"."longitude" AS longitude,
        "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name",
        "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_type"
        FROM
        "ahiscl"."hrgt_episode_dtl",
        "ahiscl"."gblt_hospital_mst_copy1" 
        WHERE
        "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code" = "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" AND 
        "ahiscl"."gblt_hospital_mst_copy1"."gnum_isvalid" = 1 
        AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_state_code" = 21 
        AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_type" ={selected_hosp_type}
        AND "ahiscl"."gblt_hospital_mst_copy1"."latitude" != 0
        AND "ahiscl"."gblt_hospital_mst_copy1"."longitude" !=0
        GROUP BY
        "ahiscl"."gblt_hospital_mst_copy1"."latitude",
        "ahiscl"."gblt_hospital_mst_copy1"."longitude",
        "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
        "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name" ''',conn)
        
    update_hosp.hosp_names_filtered=list(checklistmap['gstr_hospital_name'])
    options=[{'label':opt, 'value':opt} for opt in update_hosp.hosp_names_filtered]
    # print(update_hosp.df_hardware_data)

    # .loc[df_hardware_data['Health Facility']=='DHH']
    if selected_tab=='tab1-hardware':
        df_hardware_data=pd.read_csv('C:/Users/HP/Desktop/CDAC/eswasthya_dashboard/hardware1.csv')
        df_hardware_data=df_hardware_data.dropna()
        df_hardware_filtered=df_hardware_data.loc[df_hardware_data['Hosp Type']==selected_hosp_type]
        # result=df_hardware_filtered['Required'].multiply(df_hardware_filtered['No of Institution'])

        if df_hardware_filtered.empty:
            return options, html.Div([
            html.Div([
                html.Div([
                    html.H5("Desktops", className='card-title text-left fw-bold mb-5',style={"color":"cc1818"}),
                    html.H5("No data found.", className='card-text')
                ], className='card col-sm-4 p-3 mt-5',style={"display": "inline-block"}),
                html.Div([
                    html.H5("Printers", className='card-title text-left fw-bold  mb-5',style={"color":"cc1818"}),
                    html.H5("No data found.", className='card-text')

                ],className='card col-sm-4 p-3 mt-5',style={"display": "inline-block"}),
                html.Div([
                    html.H5("UPS", className='card-title text-left fw-bold mb-5',style={"color":"cc1818"}),
                    html.H5("No data found.", className='card-text')
                ], className='card col-sm-4 p-3 mt-5',style={"display": "inline-block"})
            ])
        ])
        else:
            df_hardware_data_desktop=df_hardware_filtered.loc[(df_hardware_filtered['Hardwares']=='Desktops')]
        # fig=px.sunburst(df_hardware_data_desktop, path=['Required','Procured','Delivered'],values=[df_hardware_data_desktop['Required'].iloc[0], df_hardware_data_desktop['Procured'].iloc[0], df_hardware_data_desktop['Delivered'].iloc[0]], color='Type', color_discrete_map={'Delivered':'lightblue', 'Procured':'darkblue','Required':'#FA3373'})
        # , color='Type', color_discrete_map={'Delivered':'lightblue', 'Procured':'darkblue','Required':'#FA3373'})

        # fig=px.pie(df_hardware_data_desktop, values='Amount', names='Type',color='Type',color_discrete_map={'Delivered':'lightblue', 'Procured':'#5162D1','Required':'#FA587D'})
        # fig.update_layout(height=350)

        # new_df=pd.read_csv('C:/Users/HP/Desktop/CDAC/eswasthya_dashboard/hardwarenew.csv')
            df_hardware_data_printer=df_hardware_filtered.loc[df_hardware_filtered['Hardwares']=='Printer']
        # fig2=px.sunburst(df_hardware_data_printer, path=['Hardwares','Type'],values='Amount', color='Type', color_discrete_map={'(?)':'white','Delivered':'lightblue', 'Procured':'darkblue','Required':'#FA3373'})

        # fig2=px.pie(df_hardware_data_printer, values='Amount', names='Type', color='Type',color_discrete_map={'Delivered':'lightblue', 'Procured':'#5162D1','Required':'#FA587D'})
        # fig2.update_layout(height=350)

            df_hardware_data_ups=df_hardware_filtered.loc[df_hardware_filtered['Hardwares']=='UPS']
        # fig3=px.sunburst(df_hardware_data_ups, path=['Hardwares','Type'],values='Amount', color='Type', color_discrete_map={'(?)':'white','Delivered':'lightblue', 'Procured':'darkblue','Required':'#FA3373'})

        # fig3=px.pie(df_hardware_data_ups, values='Amount', names='Type', color='Type',color_discrete_map={'Delivered':'lightblue', 'Procured':'#5162D1','Required':'#FA587D'})
        # fig3.update_layout(height=350)

            return options, html.Div([
                html.Div([
                    html.Div([
                    html.H5("Desktops", className='card-title text-left fw-bold mb-5',style={"color":"cc1818"}),
                # dcc.Graph(figure=fig, className=' card-text shadow-sm rounded')

                    html.H6("Required",style={"display": "inline-block"}),
                    dbc.Progress(value=df_hardware_data_desktop['Required'].iloc[0],max=df_hardware_data_desktop['Required'].iloc[0],label=df_hardware_data_desktop['Required'].iloc[0],className="mb-3", style={"height":"25px"}),
                    html.H6("Procured",style={"display": "inline-block"} ),
                    dbc.Progress(value=df_hardware_data_desktop['Procured'].iloc[0], max=df_hardware_data_desktop['Required'].iloc[0],label=df_hardware_data_desktop['Procured'].iloc[0],color="warning",className="mb-3",style={"height":"25px"}),
                    html.H6("Delivered",style={"display": "inline-block"}),
                    dbc.Progress(value=df_hardware_data_desktop['Delivered'].iloc[0] , max=df_hardware_data_desktop['Required'].iloc[0], label=df_hardware_data_desktop['Delivered'].iloc[0] ,color="success",style={"height":"25px"})

                # dash_table.DataTable(df_hardware_data_desktop.drop(['Health Facility','Hosp Type', 'Hardwares'],axis=1).to_dict('records'), style_cell={'textAlign': 'center'},
                # style_data_conditional=[
                #     {
                #         'if':{
                #             'row_index': 0},
                #             'backgroundColor':'#FA587D'
                #     },
                #     {
                #         'if':{
                #             'row_index': 1},
                #             'backgroundColor':'#5162D1'
                #     },
                #     {
                #         'if':{
                #             'row_index': 2},
                #             'backgroundColor':'lightblue'
                #     }
                # ]),
                # {'backgroundColor': '#CFCAEF'}
                    ], className='card col-sm-4 p-3 mt-5',style={"display": "inline-block"}),
                    html.Div([
                        html.H5("Printers", className='card-title text-left fw-bold  mb-5',style={"color":"cc1818"}),
                    # dcc.Graph(figure=fig2, className=' card-text shadow-sm rounded')

                        html.H6("Required",style={"display": "inline-block"}),
                        dbc.Progress(value=df_hardware_data_printer['Required'].iloc[0],max=df_hardware_data_printer['Required'].iloc[0],label=df_hardware_data_printer['Required'].iloc[0],className="mb-3", style={"height":"25px"}),
                        html.H6("Procured",style={"display": "inline-block"} ),
                        dbc.Progress(value=df_hardware_data_printer['Procured'].iloc[0], max=df_hardware_data_printer['Required'].iloc[0],label=df_hardware_data_printer['Procured'].iloc[0],color="warning",className="mb-3",style={"height":"25px"}),
                        html.H6("Delivered",style={"display": "inline-block"}),
                        dbc.Progress(value=df_hardware_data_printer['Delivered'].iloc[0] , max=df_hardware_data_printer['Required'].iloc[0], label=df_hardware_data_printer['Delivered'].iloc[0] ,color="success",style={"height":"25px"})

                    # dash_table.DataTable(df_hardware_data_printer.drop(['Health Facility','Hosp Type', 'Hardwares'],axis=1).to_dict('records'), style_cell={'textAlign': 'center'},
                    # style_data_conditional=[
                    #     {
                    #     'if':{
                    #         'row_index': 0},
                    #         'backgroundColor':'#FA587D'
                    # },
                    # {
                    #     'if':{
                    #         'row_index': 1},
                    #         'backgroundColor':'#5162D1'
                    # },
                    # {
                    #     'if':{
                    #         'row_index': 2},
                    #         'backgroundColor':'lightblue'
                    # }
                    # ])
                        ],className='card col-sm-4 p-3 mt-5',style={"display": "inline-block"}),
                    html.Div([
                        html.H5("UPS", className='card-title text-left fw-bold mb-5',style={"color":"cc1818"}),
                    # dcc.Graph(figure=fig3, className=' card-text shadow-sm rounded')

                        html.H6("Required",style={"display": "inline-block"}),
                        dbc.Progress(value=df_hardware_data_ups['Required'].iloc[0],max=df_hardware_data_ups['Required'].iloc[0],label=df_hardware_data_ups['Required'].iloc[0],className="mb-3", style={"height":"25px"}),
                        html.H6("Procured",style={"display": "inline-block"} ),
                        dbc.Progress(value=df_hardware_data_ups['Procured'].iloc[0], max=df_hardware_data_ups['Required'].iloc[0],label=df_hardware_data_ups['Procured'].iloc[0],color="warning",className="mb-3",style={"height":"25px"}),
                        html.H6("Delivered",style={"display": "inline-block"}),
                        dbc.Progress(value=df_hardware_data_ups['Delivered'].iloc[0] , max=df_hardware_data_ups['Required'].iloc[0], label=df_hardware_data_ups['Delivered'].iloc[0] ,color="success",style={"height":"25px"})

                    # dash_table.DataTable(df_hardware_data_ups.drop(['Health Facility','Hosp Type', 'Hardwares'],axis=1).to_dict('records'), style_cell={'textAlign': 'center'},
                    # style_data_conditional=[
                    #     {
                    #     'if':{
                    #         'row_index': 0},
                    #         'backgroundColor':'#FA587D'
                    # },
                    # {
                    #     'if':{
                    #         'row_index': 1},
                    #         'backgroundColor':'#5162D1'
                    # },
                    # {
                    #     'if':{
                    #         'row_index': 2},
                    #         'backgroundColor':'lightblue'
                    # }
                    # ])
                        ], className='card col-sm-4 p-3 mt-5',style={"display": "inline-block"})
                    ])
            # html.Div([dash_table.DataTable(df_hardware_data_desktop.drop(['Health Facility','Hosp Type', 'Hardwares'],axis=1).to_dict('records'), style_cell={'textAlign': 'center'},style_data={'backgroundColor': 'rgb(90, 90, 90)','color': 'white'})], className='col-sm-4 p-5',style={"display": "inline-block"}),
            # html.Div([dash_table.DataTable(df_hardware_data_printer.drop(['Health Facility','Hosp Type', 'Hardwares'],axis=1).to_dict('records'), style_cell={'textAlign': 'center'},style_data={'backgroundColor': 'rgb(90, 90, 90)','color': 'white'})], className='col-sm-4 p-5',style={"display": "inline-block"}),
            # html.Div([dash_table.DataTable(df_hardware_data_ups.drop(['Health Facility','Hosp Type', 'Hardwares'],axis=1).to_dict('records'), style_cell={'textAlign': 'center'},style_data={'backgroundColor': 'rgb(90, 90, 90)','color': 'white'})], className='col-sm-4 p-5',style={"display": "inline-block"})])
                ])

    elif selected_tab=='tab4-manpower':
        df_manpower_data=pd.read_csv('C:/Users/HP/Desktop/CDAC/eswasthya_dashboard/manpower.csv')
        df_manpower_data=df_manpower_data.dropna()
        df_manpower_filtered=df_manpower_data.loc[df_manpower_data['Hosp Type']==selected_hosp_type]

        fig4=px.pie(df_manpower_filtered, values="Amount", names="Type", color="Type", color_discrete_sequence=px.colors.sequential.RdBu)
        fig4.update_traces(marker=dict(colors=['#FA587D', 'lightblue', '#5E65FA', 'lightgreen']))
        return options, html.Div([html.Div([dcc.Graph(figure=fig4)], className='col-sm-6',style={"display": "inline-block"}), 
        html.Div([ dash_table.DataTable(df_manpower_filtered.drop(['Health Facility','Hosp Type'],axis=1).to_dict('records'),
        style_table={'width':'330px'},
        style_data_conditional=[
            {
                'if':{
                    'row_index': 0
                },
                'backgroundColor':'#FA587D'
            },
            {
                'if':{
                    'row_index':1
                },
                'backgroundColor':'lightblue'
            },
            {
                'if':{
                    'row_index': 2
                },
                'backgroundColor':'#5E65FA'
            },
            {
                'if':{
                    'row_index':3
                },
                'backgroundColor':'lightgreen'
            }
        ])]
        ,className='col-sm-6 pt-5 d-flex justify-content-end',style={"display": "inline-block"})], className='d-flex')

    elif selected_tab=='tab2-networking':
        df_networking_data=pd.read_csv('C:/Users/HP/Desktop/CDAC/eswasthya_dashboard/lan.csv')
        df_networking_data=df_networking_data.dropna()
        df_networking_filtered=df_networking_data.loc[df_networking_data['Hosp Type']==selected_hosp_type]
        df_networking_filtered=df_networking_filtered.drop(['Health Facility','Hosp Type', 'Commissioned', 'Tendered'],axis=1)
        return options, html.Div([dash_table.DataTable(df_networking_filtered.to_dict('records'),style_cell={'textAlign': 'center'},style_data={'backgroundColor': 'rgb(90, 90, 90)','color': 'white'},style_header={'backgroundColor': 'lightblue'})], className='p-5')

        ##get hospital name filtered according to the selected radiobutton(in the form of dataframe)
        # update_hosp.drop_options=checklistmap['gstr_hospital_name']

        ##convert the filtered names into a dictionary
        # update_hosp.abc=dict(update_hosp.drop_options)
        # print(update_hosp.abc)

        ##collect the latitude and longtitude for the hospitals filtered with radiobutton
        # locations=checklistmap[['latitude','longitude','gstr_hospital_name']]
        # update_hosp.locationlist=locations.values.tolist()

        #map to be displayed when the list of filtered hospitals has no latitude and longtitude(displays no markers)
        # if len(update_hosp.locationlist)==0:
        #     orissa_map=folium.Map(location=coordinates,min_zoom=7,zoom_start=7)
        #     orissa_map.save('maplocation.html')
        #     return open('maplocation.html','r').read(), options

        #map to be displayed with markers having lat. & longt.
        # else:
        #     for point in range(0,len( update_hosp.locationlist)):
        #         html=popup_html(point)
        #         popup=folium.Popup(folium.Html(html,script=True),max_width=500)
        #         folium.Marker(location= update_hosp.locationlist[point][0:2],name=update_hosp.locationlist[point][-1],tooltip=(checklistmap['gstr_hospital_name'][point],'Registrations:',checklistmap['count'][point]),
        #         popup=popup).add_to(marker_cluster)
        #         orissa_map.save('maplocation.html')
        #     hosp_search=Search(layer=marker_cluster, 
        #     search_label="name",placeholder='Search for a hospital',search_zoom=11 , position='topright',weight=5, collapsed=False).add_to(orissa_map)
        #     orissa_map.save('maplocation.html')
            # return open('maplocation.html','r').read(), options



# def popup_html(row):
#     left_col_color = "#3e95b5"
#     right_col_color = "#f2f9ff"
#     html=""" 
#     <!DOCTYPE html>
#     <html>
#     <center><h6 style="margin-bottom:3"; width="100px">hospital name</h4> </center>
#     <center> <table style="height: 126px; width: 305px;">
#     <tbody>
#     <tr>
#     <td style="background-color: """+ left_col_color +""";">Institution Type </td>
#     <td> abc </td>
#     </tr>
#     <tr>
#     <td style="background-color: """+ left_col_color +""";">City and State </td>
#     <td> abc </td>
#     </tr>
#     <tr>
#     <td style="background-color: """+ left_col_color +""";">Highest Degree Awarded </td>
#     <td> abc </td>
#     </tr>
#     </tbody>
#     </table></center>
#     </html>
#     """
#     return html

# @app.callback(dash.dependencies.Output(component_id='data-display',component_property='figure'),
#             # dash.dependencies.Output(component_id='data-mygraph2',component_property='figure'),
#             [dash.dependencies.Input(component_id='my_checklist',component_property='value')],
#             [dash.dependencies.Input(component_id='hosp-data-tabs',component_property='value')],
#             [dash.dependencies.Input(component_id='my_dropdown2',component_property='value')])
# def update_tab_data(selected_catg,selected_tab):
#     checklistmap=pd.read_sql_query(f'''SELECT
#     COUNT("ahiscl"."hrgt_episode_dtl"."hrgnum_puk") as count ,
#     "ahiscl"."gblt_hospital_mst_copy1"."latitude" AS latitude,
#     "ahiscl"."gblt_hospital_mst_copy1"."longitude" AS longitude,
#     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
#     "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name",
#     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_type"
#     FROM
#     "ahiscl"."hrgt_episode_dtl", "ahiscl"."gblt_hospital_mst_copy1" 
#     WHERE
#     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code" = "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" AND 
#     "ahiscl"."gblt_hospital_mst_copy1"."gnum_isvalid" = 1 AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_state_code" = 21 
#     AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_type" ={selected_catg}
#     AND "ahiscl"."gblt_hospital_mst_copy1"."latitude" != 0 AND "ahiscl"."gblt_hospital_mst_copy1"."longitude" !=0
#     GROUP BY
#     "ahiscl"."gblt_hospital_mst_copy1"."latitude","ahiscl"."gblt_hospital_mst_copy1"."longitude","ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
#     "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name" ''',conn)
#     if selected_tab=='tab1-hardware':
#         fig = go.Figure(data=[go.Table(header=dict(values=['Hardware', 'Data']),
#                  cells=dict(values=[list(checklistmap.columns), [1,1,1,1,1,1]]))
#                      ])
#         fig.update_layout(height=300,width=400,margin={"r":0,"t":15,"l":0,"b":0})
#         return fig
#     elif selected_tab=='tab2-LAN':
#         fig = go.Figure(data=[go.Table(header=dict(values=['LAN', 'Data']),
#                  cells=dict(values=[[100, 90, 80, 90], [95, 85, 75, 95]]))
#                      ])
#         return fig
#     elif selected_tab=='tab3-software':
#         fig = go.Figure(data=[go.Table(header=dict(values=['Software', 'Data']),
#                  cells=dict(values=[[100, 90, 80, 90], [95, 85, 75, 95]]))
#                      ])
#         return fig
#     elif selected_tab=='tab4-manpower':
#         fig = go.Figure(data=[go.Table(header=dict(values=['Manpower', 'Data']),
#                  cells=dict(values=[[100, 90, 80, 90], [95, 85, 75, 95]]))
#                      ])
#         return fig
    


    

# # @app.callback(dash.dependencies.Output(component_id='map2', component_property='srcDoc'),
# #     [Input(component_id='my_dropdown2',component_property='value')])
# def update_dropdown_map(drop_hospVal):
#     coordinates=(20.9517, 85.0985)
#     orissa_map=folium.Map(location=coordinates,zoom_start=7,min_zoom=7)

    # if drop_hospVal!= None:
    #     selected_hosp=pd.read_sql_query(f''' SELECT
    #     COUNT
    #     ("ahiscl"."hrgt_episode_dtl"."hrgnum_puk") as count ,
    #     "ahiscl"."gblt_hospital_mst_copy1"."latitude" AS latitude,
    #     "ahiscl"."gblt_hospital_mst_copy1"."longitude" AS longitude,
    #     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
    #     "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name"
    #     FROM
    #     "ahiscl"."hrgt_episode_dtl",
    #     "ahiscl"."gblt_hospital_mst_copy1" 
    #     WHERE
    #     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code" = "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" AND 
    #     "ahiscl"."gblt_hospital_mst_copy1"."gnum_isvalid" = 1 
    #     AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_state_code" = 21 
    #     AND "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name"={drop_hospVal}
    #     GROUP BY
    #     "ahiscl"."gblt_hospital_mst_copy1"."latitude",
    #     "ahiscl"."gblt_hospital_mst_copy1"."longitude",
    #     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
    #     "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name" ''',conn)

    #     locations=selected_hosp[['latitude','longitude']]
    #     locationlist=locations.values.tolist()

    #     # ##map to be displayed when no option from dropdown is selected
    #     # if drop_hospVal==None:
    #     #     orissa_map=folium.Map(location=update_hosp.coordinates,zoom_start=7,min_zoom=7)
    #     #     orissa_map.save('maplocation.html')
    #     #     return open('maplocation.html','r').read()

    #     ##map to be displayed when the list of filtered hospitals has no latitude and longtitude(displays no markers)
    #     if len(locationlist)==0:
    #         orissa_map=folium.Map(location=coordinates,zoom_start=7,min_zoom=7)
    #         orissa_map.save('maplocation.html')
    #         return open('maplocation.html','r').read()

    #     ##map to be displayed with markers having lat. & longt.
    #     else:
    #         for point in range(0,len(locationlist)):
    #             folium.Marker(location=locationlist[point],tooltip=(selected_hosp['gstr_hospital_name'][point],'Registrations:',selected_hosp['count'][point])).add_to(orissa_map)
    #             update_hosp.orissa_map.save('maplocation.html')
    #         return open('maplocation.html','r').read()
    # else:
    #     orissa_map.save('maplocation.html')
    #     return open('maplocation.html','r').read()



# @app.callback(dash.dependencies.Output(component_id='map', component_property='srcDoc'),
#     [dash.dependencies.Input(component_id='my_checklist',component_property='value')],
#     [Input(component_id='my_dropdown2',component_property='value')],
#     prevent_initial_call=True)
# def update_final_map(selected_hosp, drop_hospVal):
#     coordinates=(20.9517, 85.0985)
#     orissa_map=folium.Map(location=coordinates,zoom_start=7,min_zoom=7)
#     triggered_id=ctx.triggered_id

#     if triggered_id == 'my_checklist':
#         # if selected_hosp==None:
#         #     orissa_map.save('maplocation.html')
#         #     return open('maplocation.html','r').read()
#         # elif selected_hosp!= None:
#         checklistmap=pd.read_sql_query(f'''SELECT
#         COUNT
#         ("ahiscl"."hrgt_episode_dtl"."hrgnum_puk") as count ,
#         "ahiscl"."gblt_hospital_mst_copy1"."latitude" AS latitude,
#         "ahiscl"."gblt_hospital_mst_copy1"."longitude" AS longitude,
#         "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
#         "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name",
#         "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_type"
#         FROM
#         "ahiscl"."hrgt_episode_dtl",
#         "ahiscl"."gblt_hospital_mst_copy1" 
#         WHERE
#         "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code" = "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" AND 
#         "ahiscl"."gblt_hospital_mst_copy1"."gnum_isvalid" = 1 
#         AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_state_code" = 21 
#         AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_type" ={selected_hosp}
#         GROUP BY
#         "ahiscl"."gblt_hospital_mst_copy1"."latitude",
#         "ahiscl"."gblt_hospital_mst_copy1"."longitude",
#         "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
#         "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name" ''',conn)

#         ##get hospital name filtered according to the selected radiobutton(in the form of dataframe)
#         drop_options=checklistmap['gstr_hospital_name']

#         ##convert the filtered names into a dictionary
#         abc=dict(drop_options)
#         print(abc)

#         ##collect the latitude and longtitude for the hospitals filtered with radiobutton
#         locations=checklistmap[['latitude','longitude']]
#         locationlist=locations.values.tolist()
            
#         if len(locationlist)==0:
#             orissa_map=folium.Map(location=coordinates,zoom_start=7,min_zoom=7)
#             orissa_map.save('maplocation.html')
#             return open('maplocation.html','r').read()
                
#                 ##map to be displayed with markers having lat. & longt.
#         else:
#             for point in range(0,len(locationlist)):
#                 folium.Marker(location=locationlist[point],tooltip=(checklistmap['gstr_hospital_name'][point],'Registrations:',checklistmap['count'][point])).add_to(orissa_map)
#                 orissa_map.save('maplocation.html')
#             return open('maplocation.html','r').read()
#     elif triggered_id=='my_dropdown2':
#         if drop_hospVal!= None:
#             selected_hosp=pd.read_sql_query(f''' SELECT
#             COUNT
#             ("ahiscl"."hrgt_episode_dtl"."hrgnum_puk") as count ,
#             "ahiscl"."gblt_hospital_mst_copy1"."latitude" AS latitude,
#             "ahiscl"."gblt_hospital_mst_copy1"."longitude" AS longitude,
#             "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
#             "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name"
#             FROM
#             "ahiscl"."hrgt_episode_dtl",
#             "ahiscl"."gblt_hospital_mst_copy1" 
#             WHERE
#             "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code" = "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" AND 
#             "ahiscl"."gblt_hospital_mst_copy1"."gnum_isvalid" = 1 
#             AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_state_code" = 21 
#             AND "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name"={drop_hospVal}
#             GROUP BY
#             "ahiscl"."gblt_hospital_mst_copy1"."latitude",
#             "ahiscl"."gblt_hospital_mst_copy1"."longitude",
#             "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
#             "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name" ''',conn)

#             locations=selected_hosp[['latitude','longitude']]
#             locationlist=locations.values.tolist()

#             # ##map to be displayed when no option from dropdown is selected
#             # if drop_hospVal==None:
#             #     orissa_map=folium.Map(location=update_hosp.coordinates,zoom_start=7,min_zoom=7)
#             #     orissa_map.save('maplocation.html')
#             #     return open('maplocation.html','r').read()

#             ##map to be displayed when the list of filtered hospitals has no latitude and longtitude(displays no markers)
#             if len(locationlist)==0:
#                 orissa_map=folium.Map(location=coordinates,zoom_start=7,min_zoom=7)
#                 orissa_map.save('maplocation.html')
#                 return open('maplocation.html','r').read()

#             ##map to be displayed with markers having lat. & longt.
#             else:
#                 for point in range(0,len(locationlist)):
#                     folium.Marker(location=locationlist[point],tooltip=(selected_hosp['gstr_hospital_name'][point],'Registrations:',selected_hosp['count'][point])).add_to(orissa_map)
#                     orissa_map.save('maplocation.html')
#                     return open('maplocation.html','r').read()
#         else:
#             orissa_map.save('maplocation.html')
#             return open('maplocation.html','r').read()

# xyz=update_final_map.


# def update_hosp(selected_hosp):

    ##coordinates of main odisha map
    # coordinates=(20.9517, 85.0985)

    # ##plotting the map
    # # orissa_map=folium.Map(location=coordinates,zoom_start=7,min_zoom=7,max_zoom=7,zoom_control=False,scrollWheelZoom=False, dragging=False)
    # orissa_map=folium.Map(location=coordinates,zoom_start=7,min_zoom=7)


    ##map to be displayed when no radiobutton option is selected
    # if selected_hosp==None:
    #     orissa_map.save('maplocation.html')
    #     return open('maplocation.html','r').read()

    ##map to be displayed when a radiobutton option is selected(including the default option of radiobutton that is selected)
    # elif selected_hosp!= None:
    #     checklistmap=pd.read_sql_query(f'''SELECT
    #     COUNT
    #     ("ahiscl"."hrgt_episode_dtl"."hrgnum_puk") as count ,
    #     "ahiscl"."gblt_hospital_mst_copy1"."latitude" AS latitude,
    #     "ahiscl"."gblt_hospital_mst_copy1"."longitude" AS longitude,
    #     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
    #     "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name",
    #     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_type"
    #     FROM
    #     "ahiscl"."hrgt_episode_dtl",
    #     "ahiscl"."gblt_hospital_mst_copy1" 
    #     WHERE
    #     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code" = "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" AND 
    #     "ahiscl"."gblt_hospital_mst_copy1"."gnum_isvalid" = 1 
    #     AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_state_code" = 21 
    #     AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_type" ={selected_hosp}
    #     GROUP BY
    #     "ahiscl"."gblt_hospital_mst_copy1"."latitude",
    #     "ahiscl"."gblt_hospital_mst_copy1"."longitude",
    #     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
    #     "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name" ''',conn)

    #     ##get hospital name filtered according to the selected radiobutton(in the form of dataframe)
    #     update_hosp.drop_options=checklistmap['gstr_hospital_name']

    #     ##convert the filtered names into a dictionary
    #     update_hosp.abc=dict(update_hosp.drop_options)
    #     print(update_hosp.abc)

    #     ##collect the latitude and longtitude for the hospitals filtered with radiobutton
    #     locations=checklistmap[['latitude','longitude']]
    #     locationlist=locations.values.tolist()

        ##map to be displayed when the list of filtered hospitals has no latitude and longtitude(displays no markers)
        # if len(locationlist)==0:
        #     orissa_map=folium.Map(location=coordinates,zoom_start=7,min_zoom=7)
        #     orissa_map.save('maplocation.html')
        #     return open('maplocation.html','r').read(), update_hosp.abc

        ##map to be displayed with markers having lat. & longt.
        # else:
        #     for point in range(0,len(locationlist)):
        #         folium.Marker(location=locationlist[point],tooltip=(checklistmap['gstr_hospital_name'][point],'Registrations:',checklistmap['count'][point])).add_to(orissa_map)
        #         orissa_map.save('maplocation.html')
        #     return open('maplocation.html','r').read(), update_hosp.abc

# # @app.callback(dash.dependencies.Output(component_id='map2', component_property='srcDoc'),
# #     [Input(component_id='my_dropdown2',component_property='value')])
# def update_dropdown_map(drop_hospVal):
#     coordinates=(20.9517, 85.0985)
#     orissa_map=folium.Map(location=coordinates,zoom_start=7,min_zoom=7)

    # if drop_hospVal!= None:
    #     selected_hosp=pd.read_sql_query(f''' SELECT
    #     COUNT
    #     ("ahiscl"."hrgt_episode_dtl"."hrgnum_puk") as count ,
    #     "ahiscl"."gblt_hospital_mst_copy1"."latitude" AS latitude,
    #     "ahiscl"."gblt_hospital_mst_copy1"."longitude" AS longitude,
    #     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
    #     "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name"
    #     FROM
    #     "ahiscl"."hrgt_episode_dtl",
    #     "ahiscl"."gblt_hospital_mst_copy1" 
    #     WHERE
    #     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code" = "ahiscl"."hrgt_episode_dtl"."gnum_hospital_code" AND 
    #     "ahiscl"."gblt_hospital_mst_copy1"."gnum_isvalid" = 1 
    #     AND "ahiscl"."gblt_hospital_mst_copy1"."gnum_state_code" = 21 
    #     AND "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name"={drop_hospVal}
    #     GROUP BY
    #     "ahiscl"."gblt_hospital_mst_copy1"."latitude",
    #     "ahiscl"."gblt_hospital_mst_copy1"."longitude",
    #     "ahiscl"."gblt_hospital_mst_copy1"."gnum_hospital_code",
    #     "ahiscl"."gblt_hospital_mst_copy1"."gstr_hospital_name" ''',conn)

    #     locations=selected_hosp[['latitude','longitude']]
    #     locationlist=locations.values.tolist()

    #     # ##map to be displayed when no option from dropdown is selected
    #     # if drop_hospVal==None:
    #     #     orissa_map=folium.Map(location=update_hosp.coordinates,zoom_start=7,min_zoom=7)
    #     #     orissa_map.save('maplocation.html')
    #     #     return open('maplocation.html','r').read()

    #     ##map to be displayed when the list of filtered hospitals has no latitude and longtitude(displays no markers)
    #     if len(locationlist)==0:
    #         orissa_map=folium.Map(location=coordinates,zoom_start=7,min_zoom=7)
    #         orissa_map.save('maplocation.html')
    #         return open('maplocation.html','r').read()

    #     ##map to be displayed with markers having lat. & longt.
    #     else:
    #         for point in range(0,len(locationlist)):
    #             folium.Marker(location=locationlist[point],tooltip=(selected_hosp['gstr_hospital_name'][point],'Registrations:',selected_hosp['count'][point])).add_to(orissa_map)
    #             update_hosp.orissa_map.save('maplocation.html')
    #         return open('maplocation.html','r').read()
    # else:
    #     orissa_map.save('maplocation.html')
    #     return open('maplocation.html','r').read()




if __name__ == '__main__':
    app.run_server(debug=True)


# # OPD = 3
# # EMG AND CASUALLTIY =1
# # PRESCRIPTION = 

# billing
# admission = 2       active patients admit and discharge
# report  generate 14,26  pending 13 
# investgation