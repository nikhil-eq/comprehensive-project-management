import solara
import solara.lab

# ── THEME MUST BE SET AT MODULE LEVEL ──
solara.lab.theme.dark = True
solara.lab.theme.themes.dark.primary = "#0B1118"
solara.lab.theme.themes.dark.navigation = "#0B1118"
solara.lab.theme.themes.light.primary = "#0B1118"  # fallback safety

from home import Page
from daily_entry import Page1
from weekly_view import Page2
from monthly_view import Page3
from delivered_view import Page4
from efficiency_view import Page5
from rnd_view import Page6

routes = [
    solara.Route(path="/", component=Page, label="Home"),
    solara.Route(path="daily-entry", component=Page1, label="Daily Entry"),
    solara.Route(path="weekly-view", component=Page2, label="Weekly View"),
    solara.Route(path="monthly-view", component=Page3, label="Monthly View"),
    solara.Route(path="delivered-view", component=Page4, label="Delivered View"),
    solara.Route(path="efficiency-view", component=Page5, label="Efficiency View"),
    solara.Route(path="rnd-view", component=Page6, label="Research and Development"),
]

# ── Global dark CSS ──
DARK_CSS = """
.v-application, .v-application--wrap, html, body {
    background-color: #0a0f16 !important;
}
.v-app-bar, header.v-app-bar {
    background-color: #0B1118 !important;
    border-bottom: 1px solid #1a2a3a !important;
    color: #e8eef4 !important;
    box-shadow: none !important;
}
.v-app-bar .v-toolbar__title {
    color: #e8eef4 !important;
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
.v-card {
    background-color: #111a25 !important;
    border: 1px solid #1a2a3a !important;
    color: #e8eef4 !important;
}
.v-data-table {
    background-color: #111a25 !important;
    color: #e8eef4 !important;
}
.v-data-table th, .v-data-table td {
    color: #e8eef4 !important;
    border-bottom: 1px solid #1a2a3a !important;
}
.v-input__slot {
    background-color: #111a25 !important;
    border: 1px solid #1a2a3a !important;
}
.v-label, .v-select__selection {
    color: #8fa3b8 !important;
}
.v-input input, .v-input textarea {
    color: #e8eef4 !important;
}
.v-list {
    background-color: #111a25 !important;
    color: #e8eef4 !important;
}
.v-menu__content {
    background-color: #111a25 !important;
    border: 1px solid #1a2a3a !important;
}
.v-expansion-panel {
    background-color: #111a25 !important;
    color: #e8eef4 !important;
    border: 1px solid #1a2a3a !important;
}
.v-expansion-panel-header {
    color: #e8eef4 !important;
}
.v-btn {
    color: #e8eef4 !important;
}
"""


@solara.component
def Layout(children=[]):
    route_current, all_routes = solara.use_route()

    # Inject CSS properly as a <style> tag
    solara.HTML(tag="style", unsafe_innerHTML=DARK_CSS)

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