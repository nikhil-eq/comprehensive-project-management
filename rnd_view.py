import solara
import pandas as pd

from pathlib import Path

EXCEL_PATH = Path('db.xlsx')

def load_data() -> pd.DataFrame:
    df = pd.read_excel(EXCEL_PATH, sheet_name='Sheet1')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    for col in ['current_status', 'stage', 'workstream_name', 'project_name', 'user_name']:
        df[col] = df[col].astype(str).str.strip()
    df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.weekday, unit='D')
    return df
selected_week_label = solara.reactive(None)

TARGET_WORKSTREAM = 'research and development'


def load_rd_log() -> pd.DataFrame:
    df = load_data()

    mask = df['workstream_name'].str.lower() == TARGET_WORKSTREAM
    rd_df = df[mask].copy()

    rd_df = rd_df.sort_values('date', ascending=False)
    return rd_df[['user_name', 'stage', 'rnd_explaination', 'time_spent']]


@solara.component
def Page6():
    
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
    
    solara.Title('Research and Development')
    solara.Markdown('# Research and Development')
    solara.Markdown('All logged R&D work, most recent first.')

    rd_df = load_rd_log()

    if rd_df.empty:
        solara.Markdown('_No Research and Development entries found._')
        return

    result = rd_df.rename(columns={
        'user_name': 'Team Member',
        'stage': 'Stage',
        'rnd_explaination': 'Description',
        'time_spent': 'Time Spent (hrs)',
    })

    solara.Markdown(f"**{len(result)}** entries logged")
    solara.DataFrame(result, items_per_page=25)