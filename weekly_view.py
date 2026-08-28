import solara
import pandas as pd

from pathlib import Path

import matplotlib.pyplot as plt

EXCEL_PATH = Path('db.xlsx')

def load_data() -> pd.DataFrame:
    df = pd.read_excel(EXCEL_PATH, sheet_name='Sheet1')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    for col in ['current_status', 'stage', 'workstream_name', 'project_name', 'user_name']:
        df[col] = df[col].astype(str).str.strip()
    df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.weekday, unit='D')
    return df
selected_week_label = solara.reactive(None)


workstreams_list_delivery = [
    'Initial Stratification - HIR',
    'Initial Stratification - NFMR',
    'Restratification - HIR',
    'Restratification - NFMR',
    'Restratification - Regen Check',
    'Change Detection',
    'Fire Impact Assessment',
    'Grid Creation',
    'Spatial Data Cleaning and Ingestion',
    'AD Survey Packages',
    'Field Survey Packages',
    'Adhoc Analysis',
    'Carbon Plus',
]

rnd_list = [
    'Research and Development', 
    'Miscellaneous',
    'Paddock Mapping and Digitisation' 
]


def get_latest_status_map(df: pd.DataFrame) -> pd.DataFrame:
    """Each (user, workstream, project)'s latest known status/stage,
    based on that user's most recent dated entry for that project."""
    return (
        df.sort_values('date')
          .groupby(['user_name', 'workstream_name', 'project_name'], as_index=False)
          .last()[['user_name', 'workstream_name', 'project_name', 'current_status', 'stage']]
          .rename(columns={'current_status': 'latest_status', 'stage': 'latest_stage'})
    )
    
def get_workstream_ops_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per workstream: how many distinct projects have been touched,
    how many are completed, and a bullet-point breakdown of project names
    (every project touched, plus a separate list of the ones still In Progress).
    """
    scoped = df[df['workstream_name'].isin(workstreams_list_delivery)].copy()
    scoped['current_status'] = scoped['current_status'].str.strip().str.lower()

    # latest known status per (workstream, project) — not per user, since this
    # view is about project completion, not who logged it
    project_status = (
        scoped.sort_values('date')
              .groupby(['workstream_name', 'project_name'], as_index=False)
              .last()[['workstream_name', 'project_name', 'current_status']]
    )

    def build_row(group: pd.DataFrame) -> pd.Series:
        completed = group[group['current_status'] == 'completed']
        in_progress = group[group['current_status'] != 'completed']

        all_names = "\n".join(f"• {n}" for n in sorted(group['project_name']))
        in_progress_names = (
            "\n".join(f"• {n}" for n in sorted(in_progress['project_name']))
            if not in_progress.empty else "—"
        )

        return pd.Series({
            'total_touched': group['project_name'].nunique(),
            'completed_count': len(completed),
            'all_projects': all_names,
            'in_progress_projects': in_progress_names,
        })

    summary = (
        project_status.groupby('workstream_name')
                       .apply(build_row, include_groups = False)
                       .reset_index()
    )

    summary['workstream_name'] = pd.Categorical(
        summary['workstream_name'], categories=workstreams_list_delivery, ordered=True
    )
    summary = summary.sort_values('workstream_name').reset_index(drop=True)
    return summary

def get_paddock_summary(df: pd.DataFrame) -> pd.DataFrame:

    scoped = df[df['workstream_name'].isin(['Paddock Mapping and Digitisation'])].copy()
    scoped['current_status'] = scoped['current_status'].str.strip().str.lower()

    project_status = (
        scoped.sort_values('date')
                .groupby(['workstream_name', 'project_name'], as_index=False)
                .last()[['workstream_name', 'project_name', 'current_status']]
    )

    def build_row(group: pd.DataFrame) -> pd.Series:
        completed = group[group['current_status'] == 'completed']
        in_progress = group[group['current_status'] != 'completed']

        all_names = "\n".join(f"• {n}" for n in sorted(group['project_name']))
        in_progress_names = (
            "\n".join(f"• {n}" for n in sorted(in_progress['project_name']))
            if not in_progress.empty else "—"
        )

        return pd.Series({
            'total_touched': group['project_name'].nunique(),
            'completed_count': len(completed),
            'all_projects': all_names,
            'in_progress_projects': in_progress_names,
        })

    summary = (
        project_status.groupby('workstream_name')
                        .apply(build_row, include_groups = False)
                        .reset_index()
    )

    summary['workstream_name'] = pd.Categorical(
        summary['workstream_name'], categories= ['Paddock Mapping and Digitisation'], ordered=True
    )
    summary = summary.sort_values('workstream_name').reset_index(drop=True)
    
    summary = summary.rename(columns = {
        'workstream_name': 'Workstream', 
        'total_touched': 'Projects Planned', 
        'completed_count': 'Projects Completed',
        'all_projects': 'All Projects', 
        'in_progress_projects': 'In Progress Projects'
    })
    
    return summary


def get_workstream_rnd_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per remaining R&D stage (excludes Paddock Mapping and Digitisation —
    see get_paddock_summary for that). Detail column lists that stage's logged
    rnd_explaination entries.
    """
    scoped = df[df['workstream_name'].isin(rnd_list)].copy()
    scoped['stage'] = scoped['stage'].str.strip()
    scoped['rnd_explaination'] = scoped['rnd_explaination'].astype(str).str.strip()

    paddock_stage_names = {'Processing', 'Completed'}
    scoped = scoped[~scoped['stage'].isin(paddock_stage_names)]

    stage_display_names = {
        'iMAD': 'iMAD: Change Detection',
        'WS3: ALS-to-CPC': 'WS3: ALS-to-CPC',
        'Fire Impact Assessment': 'Fire Impact Assessment',
        'WS2: Allometric Equations': 'WS2: Allometric Equations',
    }
    scoped['stage'] = scoped['stage'].replace(stage_display_names)

    def build_row(group: pd.DataFrame) -> pd.Series:
        explanations = group['rnd_explaination'].dropna()
        explanations = explanations[explanations != '']
        detail = "\n".join(f"• {e}" for e in explanations) if not explanations.empty else "—"

        return pd.Series({
            'planned': group['project_name'].nunique(),
            'detail': detail,
        })

    summary = (
        scoped.groupby('stage', group_keys=True)
              .apply(build_row, include_groups=False)
              .reset_index()
    )

    summary = summary.sort_values('stage').reset_index(drop=True)
    
    summary = summary.drop(columns = ['planned'])
    
    summary = summary.rename(columns={
        'stage': 'Workstream',
        'detail': 'Progress',
    })
    return summary

def get_user_workstream_hours(week_df: pd.DataFrame) -> pd.DataFrame:
    """
    Hours per (user, workstream) for the given week, across ALL workstreams
    (no filtering to workstreams_list_delivery — Miscellaneous, R&D, etc. included).
    """
    hours = (
        week_df.groupby(['user_name', 'workstream_name'], as_index=False)
               .agg(hours=('time_spent', 'sum'))
    )
    # pivot: rows = user, columns = workstream, values = hours
    pivot = hours.pivot(index='user_name', columns='workstream_name', values='hours').fillna(0)
    return pivot


@solara.component
def Page2():
    solara.Title('Weekly View')
    
    with solara.Card(
        style = {'background': "#050e22fc"}
    ):
    
        solara.Markdown('## Weekly Work Log')

        df = load_data()
        
        weeks = sorted(df['week_start'].dropna().unique(), reverse=True)
        week_labels = {w: f"Week of {pd.Timestamp(w).strftime('%d %b %Y')}" for w in weeks}
        label_to_week = {v: k for k, v in week_labels.items()}
        week_label_options = list(week_labels.values())

        if not week_label_options:
            solara.Markdown('_No dated entries found._')
            return

        if selected_week_label.value not in week_label_options:
            selected_week_label.value = week_label_options[0]

        solara.Select(label='Select Week', value=selected_week_label, values=week_label_options)

    current_week = label_to_week[selected_week_label.value]
    week_df = df[df['week_start'] == current_week]

    weekly_hours = (
        week_df.groupby(['user_name', 'workstream_name', 'project_name'], as_index=False)
               .agg(hours_this_week=('time_spent', 'sum'))
    )

    latest_status = get_latest_status_map(df)
    result = weekly_hours.merge(
        latest_status,
        on=['user_name', 'workstream_name', 'project_name'],
        how='left',
    )

    result = result.sort_values(['user_name', 'workstream_name', 'project_name'])
    result = result.rename(columns={
        'user_name': 'Team Member',
        'workstream_name': 'Workstream',
        'project_name': 'Project Name',
        'hours_this_week': 'Hours (this week)',
        'latest_stage': 'Last thing did',
        'latest_status': 'Current Status',
    })
    
    # HTML for DF
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

    with solara.Card(
            style = {'background': "#093d44fb"}
        ):
    
        solara.Markdown(f"**{len(result)}** entries for {selected_week_label.value}")
        solara.DataFrame(result, items_per_page=25)
    
    with solara.Card(
            style = {'background': "#22051ffb"}
        ):
    
        solara.Markdown("## Executive Project Summary")

        ops_summary = get_workstream_ops_summary(week_df)
        ops_summary = ops_summary.rename(columns={
            'workstream_name': 'Workstream',
            'total_touched': 'Projects Planned',
            'completed_count': 'Projects Completed',
            'all_projects': 'All Projects',
            'in_progress_projects': 'In Progress Projects',
        })
        
        solara.DataFrame(ops_summary, items_per_page=20)
        
        solara.Markdown("## WS1: Paddock Mapping and Digitisation")
        paddock_summary = get_paddock_summary(week_df)
        solara.DataFrame(paddock_summary, items_per_page=20)

        solara.Markdown("## R&D Summary")
        rnd_summary = get_workstream_rnd_summary(week_df)
        solara.DataFrame(rnd_summary, items_per_page=20)
        
    with solara.Card(
            style = {'background': "#050e22fc"}
        ):
    
        solara.Markdown(f"## Team Bandwidth")
        solara.Markdown("Hours spent per team member, broken down by workstream.")

        bandwidth = get_user_workstream_hours(week_df)

        if bandwidth.empty:
            solara.Markdown('_No hours logged this week._')
        else:
            fig, ax = plt.subplots(figsize=(9, max(3, 0.6 * len(bandwidth))))
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)

            bottom = pd.Series(0.0, index=bandwidth.index)
            for workstream in bandwidth.columns:
                values = bandwidth[workstream]
                ax.barh(bandwidth.index, values, left=bottom, label=workstream)
                bottom += values

            text_color = "#e8eef4"
            ax.set_xlabel('Hours', color=text_color)
            ax.set_ylabel('')
            ax.tick_params(colors=text_color)
            for spine in ax.spines.values():
                spine.set_color("#3a4a5a")

            legend = ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
            legend.get_frame().set_alpha(0.0)
            for text in legend.get_texts():
                text.set_color(text_color)

            ax.invert_yaxis()
            fig.tight_layout()

            solara.FigureMatplotlib(fig, dependencies=[bandwidth.to_json()])