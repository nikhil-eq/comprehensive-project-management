import solara
import pandas as pd
import openpyxl

from pathlib import Path
from datetime import date, datetime

from db import append_entry, load_project_names

#--------------------------------------------------
#              DATABASE PATH
#--------------------------------------------------

EXCEL_PATH = Path('db.xlsx')
        
style = {
        "background": "#ffffff00", 
    }

#---------------------------------------------------------
#          DECLARE ALL THE REACTIVE ELEMENTS HERE
#---------------------------------------------------------

user_name = solara.reactive("")
workstream_name = solara.reactive("")
project_name = solara.reactive("")
current_status = solara.reactive("")
stage = solara.reactive("")
today_update = solara.reactive("")
next_steps = solara.reactive("")
time_spent = solara.reactive(0.0)
entry_date = solara.reactive(date.today())

broader_view = solara.reactive("")
efficiency_description = solara.reactive("")
rnd_explaination = solara.reactive("")

workstream_value_added = solara.reactive("")
manual_against_automation = solara.reactive("")



#-----------------------------------------------------------


def save_name_to_excel(entry_date, name: str, workstream: str, project: str,
                       status: str, stage_val: str, today_update: str, steps: str, hours: float,
                       broader_view: str, efficiency_description: str, rnd_explaination: str,
                       workstream_value_added: str, manual_against_automation: str):
    if not name.strip():
        return

    # Convert date to string so JSON can serialize it
    date_str = entry_date.isoformat() if hasattr(entry_date, 'isoformat') else str(entry_date)

    row_data = {
        'date': date_str,   # <-- was entry_date, now date_str
        'user_name': name,
        'workstream_name': workstream,
        'project_name': project,
        'current_status': status,
        'stage': stage_val,
        'today_update': today_update,
        'next_steps': steps,
        'time_spent': hours,
        'broader_view': broader_view,
        'efficiency_description': efficiency_description,
        'rnd_explaination': rnd_explaination,
        'workstream_value_added': workstream_value_added,
        'manual_against_automation': manual_against_automation,
    }

    append_entry(row_data)


def submit_entry():
    save_name_to_excel(
        entry_date.value,
        user_name.value,
        workstream_name.value,
        project_name.value,
        current_status.value,
        stage.value,
        today_update.value,
        next_steps.value,
        time_spent.value,
        broader_view.value,
        efficiency_description.value, 
        rnd_explaination.value, 
        workstream_value_added.value, 
        manual_against_automation.value
    )
    # clear the form after a successful submit, but keep the name
    workstream_name.value = ""
    project_name.value = ""
    current_status.value = ""
    stage.value = ""
    today_update.value = ""
    next_steps.value = ""
    time_spent.value = 0.0
    broader_view.value = ""
    efficiency_description.value = ""
    rnd_explaination.value = ""
    workstream_value_added.value = ""
    manual_against_automation.value = ""
    
#-------------------------------------------------
#           WORKSTREAM NAMES and STEPS Involved
#-------------------------------------------------

workstreams_list = [
    'Initial Stratification - HIR', 
    'Initial Stratification - NFMR',
    'Restratification - HIR', 
    'Restratification - NFMR',
    'Restratification - Regen Check', 
    'Change Detection', 
    'Paddock Mapping and Digitisation', 
    'Fire Impact Assessment', 
    'Grid Creation',
    'Spatial Data Cleaning and Ingestion', 
    'AD Survey Packages',
    'Field Survey Packages', 
    'Adhoc Analysis', 
    'Carbon Plus', 
    'Miscellaneous', 
    'Research and Development',
    'Others (Neither Ops nor R&D)'
]

workstreams_list_delivery = [
    'Initial Stratification - HIR', 
    'Initial Stratification - NFMR',
    'Restratification - HIR', 
    'Restratification - NFMR',
    'Restratification - Regen Check', 
    'Change Detection', 
    'Paddock Mapping and Digitisation', 
    'Fire Impact Assessment', 
    'Grid Creation',
    'Spatial Data Cleaning and Ingestion', 
    'AD Survey Packages',
    'Field Survey Packages', 
    'Adhoc Analysis', 
    'Carbon Plus', 
]

xl_sheet = pd.read_excel('Change Detection Tracker - Updated.xlsx')

project_names = list(xl_sheet['Project name'])


@solara.component
def team_info():
    solara.Select(label='Who are you?',
                      value=user_name,
                      on_value=lambda value: setattr(user_name, "value", value),
                      values = ['Nikhil', 'Radha', 'Yogi', 'Rupaz'])


@solara.component
def daily_entry_form():
    solara.lab.InputDate(label='Select Date', value=entry_date, style = style)
    solara.Select(label='Workstream', value=workstream_name, values = workstreams_list, style = style)
    
    if workstream_name.value not in ["Miscellaneous", "Carbon Plus", "Research and Development", "Others (Neither Ops nor R&D)"]:
        
        solara.Select(label='Project Name', value=project_name, values = project_names, style = style)
    
    
    if workstream_name.value in ['Initial Stratification - HIR']:

        solara.Select(label='Stage', value=stage,
                  values=["Pre Processing", "Product Update", "Post Processing", "Peer Review"], style = style)
    elif workstream_name.value in ['Initial Stratification - NFMR']:
        
        solara.Select(label = 'Stage', value = stage, values = ['Exclusions Delineation', 'CEAs Delineation', 'Peer Review'])
        
    elif workstream_name.value in ['Restratification - HIR', 'Restratification - NFMR', 'Restratification - Regen Check']:
        
        solara.Select(label='Stage', value=stage,
                          values = ["Iterative Failing Grid Removal", "0.2ha Compilance", "1.5km Radius Check", "Model Point Allocation",
                                  "Strata File Update", "Topology / Geometry Check", "Peer Review"], style = style)
        
    elif workstream_name.value in ['AD Survey Packages']:
            
        solara.Select(label='Stage', value=stage,
                              values = ["Track Digitisation", "Point / Plot Allocation", "Maps Preparation",  "Peer Review"], style = style)
    
    elif workstream_name.value in ['Miscellaneous']:
                
            solara.Select(label='Stage', value=stage,
                                  values = ["Meetings", "Process Improvements", "Tool Building", "Automation", "Debugging"], style = style)
        
    elif workstream_name.value in ['Research and Development']:
            
        solara.Select(label='Stage', value=stage,
                              values = ["iMAD", "WS3: ALS-to-CPC", "Fire Impact Assessment", "WS2: Allometric Equations"], style = style)
    
    elif workstream_name.value in ['Others (Neither Ops nor R&D)']:
        
        solara.InputText(label = 'Work (e.g., Sheets / Tracker / 1:1 etc., )', value = stage)
    
    
    else: 
        
        solara.Select(label='Stage', value=stage,
                                      values = ['Processing', 'Peer Review'], style = style)
    
    if workstream_name.value in workstreams_list and not workstream_name.value in ['Research and Development'] and \
                not stage.value in ["Process Improvements", "Tool Building", "Automation"]:
        
        solara.InputText(label = "Today's Update", value = today_update, style = style)
    
    if workstream_name.value != 'Others (Neither Ops nor R&D)':
    
        solara.Select(label='Current Status', value=current_status,
                        values=["In Progress", "Blocked", "Completed"], style = style)
    
    if stage.value in ['Process Improvements', 'Automation', 'Tool Building']:
        
        solara.Select(label = 'Value Added Workstream?', value = workstream_value_added, values = workstreams_list_delivery, style = style)
        
        solara.InputText(label = "Broader View of Enhancements  Made", value = broader_view, style = style)
        
        solara.InputText(label = "Detailed Description of Enhancement / Tool / Automation", value = efficiency_description, style = style)
    
    if stage.value in ['Automation', 'Tool Building']:
        
        solara.InputText(label = "Manual v/s Automated workflow gain", value = manual_against_automation, style = style)
        
        
    
    elif workstream_name.value in ['Research and Development']:
            
        solara.InputText(label='In-detail Explaination of the progress / trials', value = rnd_explaination, style = style)
    
    solara.InputText(label='Next Steps', value=next_steps, style = style)
    
    solara.InputFloat(label='Time Spent (hours)', value=time_spent, style = style)


@solara.component
def Page1():
    
    with solara.Div(
        style = {'background': "#ff000000"}):
    
        with solara.Card(style = style):
        

            solara.Markdown('## Daily Log Entry')
            solara.Markdown('Please Enter your Name to continue')

            team_info()

            if user_name.value not in [None, ""]:

                solara.Markdown(f'We Know You are Working Great, {user_name.value}')

                daily_entry_form()
                
                solara.Markdown("\n ")
                solara.Markdown("\n")

                solara.Button(
                    label='Submit',
                    on_click=submit_entry, 
                    color = 'green', 
                    style = {
                        'color': 'white'
                    }
                )