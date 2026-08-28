import solara
import pandas as pd
from pathlib import Path

from db import load_data

selected_week_label = solara.reactive(None)

TARGET_WORKSTREAM = 'miscellaneous'
TARGET_STAGES_TOOLS_AUTOMATION = {'tool building', 'automation'}

TARGET_STAGES_PROCESS_IMPROVEMENTS = {'process improvements'}


def load_tool_usage_summary() -> pd.DataFrame:
    df = load_data()
    
    df['workstream_value_added'] = df['workstream_value_added'].astype(str).str.strip()
    df['broader_view'] = df['broader_view'].astype(str).str.strip()
    df['efficiency_description'] = df['efficiency_description'].astype(str).str.strip()
    df['manual_against_automation'] = df['manual_against_automation'].astype(str).str.strip()
    
    # For Tools and Automation Table

    mask_tools_automation = (
        (df['workstream_name'].str.lower() == TARGET_WORKSTREAM)
        & (df['stage'].str.lower().isin(TARGET_STAGES_TOOLS_AUTOMATION))
    )
    filtered_tools_automation = df[mask_tools_automation]

    summary_tools_automation = (
        filtered_tools_automation.groupby(['user_name', 'workstream_value_added', 'broader_view', 'efficiency_description', 'manual_against_automation'], as_index=False)
                .agg(hours_spent=('time_spent', 'sum'))
    )
    summary_tools_automation = summary_tools_automation.sort_values(['user_name', 'workstream_value_added']).reset_index(drop=True)
    
    
    # For Process Improvements Table
    
    mask_process_improvements = (
        (df['workstream_name'].str.lower() == TARGET_WORKSTREAM)
        & (df['stage'].str.lower().isin(TARGET_STAGES_PROCESS_IMPROVEMENTS)) 
    )
    
    filtered_process_improvements = df[mask_process_improvements]
    
    summary_process_improvements = (
        filtered_process_improvements.groupby(['user_name', 'workstream_value_added', 'broader_view', 'efficiency_description'], as_index = False)
                                    .agg(hours_spent = ('time_spent', 'sum'))
    )
    
    summary_process_improvements = summary_process_improvements.sort_values(['user_name', 'workstream_value_added']).reset_index(drop = True)
        
    
    return summary_tools_automation, summary_process_improvements


@solara.component
def Page5():
    
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
    
    solara.Title('Improvements / Tool Usage')
    solara.Markdown('## Tool / Automation Usage')
    solara.Markdown(
        'Tools Build adding value in existing workstreams along with Manual v/s Automation/Tool Usage'
    )

    summary_tools_automation_df, summary_process_improvements_df = load_tool_usage_summary()

    if summary_tools_automation_df.empty or summary_process_improvements_df.empty:
        solara.Markdown('_No matching entries found. Check that stage values in the sheet match the expected labels._')
        return

    solara.DataFrame(summary_tools_automation_df, items_per_page=25)
    
    solara.Markdown('## Process Improvements')
    solara.DataFrame(summary_process_improvements_df, items_per_page = 25)