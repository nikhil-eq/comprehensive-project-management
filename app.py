import solara
import solara.lab

from home import Page
from daily_entry import Page1
from weekly_view import Page2
from monthly_view import Page3
from delivered_view import Page4
from efficiency_view import Page5
from rnd_view import Page6

from db import load_data

routes = [
    solara.Route(path="/", component=Page, label="Home"),
    solara.Route(path="daily-entry", component=Page1, label="Daily Entry"),
    solara.Route(path="weekly-view", component=Page2, label="Weekly View"),
    solara.Route(path="monthly-view", component=Page3, label="Monthly View"),
    solara.Route(path="delivered-view", component=Page4, label="Delivered View"),
    solara.Route(path="efficiency-view", component=Page5, label="Efficiency View"),
    solara.Route(path="rnd-view", component=Page6, label="Research and Development"),
]

@solara.component
def Layout(children=[]):
    # Force dark mode AND set the dark theme primary to your color
    solara.lab.theme.dark = True
    solara.lab.theme.themes.dark.primary = "#0B1118"
    solara.lab.theme.themes.dark.navigation = "#0B1118"

    route_current, all_routes = solara.use_route()

    # Ultra-specific CSS that no Vuetify inline style can beat
    solara.HTML(tag="div", unsafe_innerHTML="""
        <style>
        html body .v-application .v-app-bar.v-toolbar,
        html body .v-application header.v-app-bar,
        .v-app-bar.v-app-bar--fixed,
        .v-app-bar.v-app-bar--absolute {
            background-color: #0B1118 !important;
            background: #0B1118 !important;
            border-bottom: 1px solid #1a2a3a !important;
            color: #e8eef4 !important;
            box-shadow: none !important;
        }
        .v-app-bar .v-toolbar__title,
        .v-app-bar .v-app-bar-title {
            color: #e8eef4 !important;
        }
        .v-application, .v-application--wrap {
            background-color: #0a0f16 !important;
        }
        .v-tabs {
            background-color: #0a0f16 !important;
        }
        .v-tab {
            color: #8fa3b8 !important;
        }
        .v-tab--active {
            color: #e8eef4 !important;
        }
        </style>
    """)

    # Do NOT pass color="#0B1118" here — let it use theme primary (which we set above)
    with solara.AppLayout(
        children=children,
        title="Project Management",
        toolbar_dark=True,
    ) as layout:
        with layout.app_bar:
            solara.AppBarTitle("Project Management")

        with solara.Tabs(
            value=route_current.path if route_current else "/",
            on_value=lambda p: solara.router.push(p)
        ):
            for r in all_routes:
                solara.Tab(r.label, path_or_route=r)

    return layout




    
