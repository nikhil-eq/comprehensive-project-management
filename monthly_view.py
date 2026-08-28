import solara
import pandas as pd

from pathlib import Path

from db import load_data

selected_month_label = solara.reactive(None)


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


def get_monthly_project_status(month_df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per workstream for the selected month: all projects touched
    (with their latest status) listed together, plus a completed count.
    """
    # latest status per project, within this month only
    project_status = (
        month_df.sort_values('date')
                .groupby(['workstream_name', 'project_name'], as_index=False)
                .last()[['workstream_name', 'project_name', 'current_status']]
    )

    project_status = project_status.sort_values(['workstream_name', 'project_name'])

    # build a "Project Name (Status)" string per project, then merge them per workstream
    project_status['project_display'] = (
        project_status['project_name'] + ' (' + project_status['current_status'] + ')'
    )

    is_completed = project_status['current_status'].str.lower() == 'completed'
    project_status['is_completed'] = is_completed

    result = (
        project_status.groupby('workstream_name')
                       .agg(
                           project_names=('project_display', lambda s: ' • '.join(s)),
                           completed_count=('is_completed', 'sum'),
                           total_projects=('project_name', 'count'),
                       )
                       .reset_index()
    )

    result['workstream_name'] = pd.Categorical(
        result['workstream_name'], categories=workstreams_list_delivery, ordered=True
    )
    result = result.sort_values('workstream_name').reset_index(drop=True)
    return result


@solara.component
def Page3():
    
    solara.HTML(tag="style", unsafe_innerHTML="""
            .nav-card:hover {
                background: #162233 !important;
                border-color: #2a3f55 !important;
                transform: translateY(-2px);
            }
            .nav-card:active {
                transform: translateY(0);
            }
        
            /* make the DataFrame table transparent / dark-theme friendly */
            .v-data-table,
            .v-data-table__wrapper,
            .v-table,
            .v-table__wrapper {
                background: transparent !important;
            }
            .v-data-table table,
            .v-data-table thead,
            .v-data-table tbody,
            .v-data-table tr {
                background: transparent !important;
            }
            .v-data-table th,
            .v-data-table td {
                background: transparent !important;
                color: #e8eef4 !important;
                border-bottom: 1px solid #1a2a3a !important;
                border-right: 1px solid #1a2a3a !important;
                padding: 0 16px !important;
            }
            .v-data-table th:last-child,
            .v-data-table td:last-child {
                border-right: none !important;
            }
            .v-data-table tbody tr:hover {
                background: #162233 !important;
            }
            .v-data-footer {
                background: transparent !important;
                color: #8fa3b8 !important;
            }
            """)
    
    solara.Title('Monthly View')
    
    with solara.Card(style = {
        'background': "#145256FF"
    }):
        solara.Markdown('## Monthly Work Log')

        df = load_data()

        months = sorted(df['month_start'].dropna().unique(), reverse=True)
        month_labels = {m: f"{pd.Timestamp(m).strftime('%B %Y')}" for m in months}
        label_to_month = {v: k for k, v in month_labels.items()}
        month_label_options = list(month_labels.values())

        if not month_label_options:
            solara.Markdown('_No dated entries found._')
            return

        if selected_month_label.value not in month_label_options:
            selected_month_label.value = month_label_options[0]

        solara.Select(label='Select Month', value=selected_month_label, values=month_label_options)

    current_month = label_to_month[selected_month_label.value]
    month_df = df[df['month_start'] == current_month]

    result = get_monthly_project_status(month_df)
    result = result.rename(columns={
        'workstream_name': 'Workstream',
        'project_names': 'Project Name',
        'completed_count': 'Completed Projects Count',
        'total_projects': 'Total Projects Touched',
    })
    
    with solara.Card(style = {
        'background': "#0f3b23"
        }): 

            solara.DataFrame(result, items_per_page=25)
            
    with solara.Card(style = {
        'background': "#3f3d08ff"
    }):
        solara.Markdown(f"**{result['Completed Projects Count'].sum() if not result.empty else 0}** projects completed in {selected_month_label.value}")
        solara.Markdown(f"**{result['Total Projects Touched'].sum() if not result.empty else 0}** projects touched in {selected_month_label.value}")