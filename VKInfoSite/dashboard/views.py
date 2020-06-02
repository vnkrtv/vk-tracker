# pylint: disable=invalid-name, no-member, global-statement
"""
DjangoDash app and dash view
"""
import dash
import dash_html_components as html
import dash_core_components as dcc
from django.shortcuts import render
from django_plotly_dash import DjangoDash
from main.models import VKToken
from main import mongo
from . import graphs

app = DjangoDash(name='Graphs',
                 id='domain_id,token_id',
                 serve_locally=True,
                 add_bootstrap_links=True)

graphs_list = [['Gender', 'GenderDistributionPieChart'],
               ['University', 'UniversityDistributionPieChart'],
               ['City', 'CitiesDistributionPieChart'],
               ['Country', 'CountriesDistributionPieChart'],
               ['Age', 'AgeDistributionPieChart'],
               ['Friends activity', 'FriendsActivityScatterPlot']]

graphs_dict = {
    'GenderDistributionPieChart': graphs.GenderDistributionPieChart,
    'UniversityDistributionPieChart': graphs.UniversityDistributionPieChart,
    'CitiesDistributionPieChart': graphs.CitiesDistributionPieChart,
    'CountriesDistributionPieChart': graphs.CountriesDistributionPieChart,
    'AgeDistributionPieChart': graphs.AgeDistributionPieChart,
    'FriendsActivityScatterPlot': graphs.FriendsActivityScatterPlot
}

app.layout = html.Div([
    html.H2('Graphs'),
    html.Div([
        dcc.Dropdown(
            id='info-graphs-input',
            options=[{'label': s[0], 'value': s[1]} for s in graphs_list],
            value=['GenderDistributionPieChart'],
            multi=True,
        ),
        dcc.Input(id='domain_id', type='hidden', value=''),
        dcc.Input(id='token_id', type='hidden', value=''),
        html.Div(id='graphs')
    ])
], className='jumbotron')

cached_graphs = {}


@app.callback(
    dash.dependencies.Output('graphs', 'children'),
    [dash.dependencies.Input('info-graphs-input', 'value'),
     dash.dependencies.Input('domain_id', 'value'),
     dash.dependencies.Input('token_id', 'value')])
def update_graph(selected_graphs, domain, token):
    """
    Updates graph in case of input Dropdown values

    :param selected_graphs: list of selected graph names
    :param domain: VK user domain
    :param token: VK token with all rights
    """
    active_graphs = []
    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
    user_info = storage.get_user(domain=domain)

    for graph_name in selected_graphs:
        try:
            if graph_name not in cached_graphs:
                graph = graphs_dict[graph_name](user_info=user_info, token=token)
                cached_graphs[graph_name] = graph.create()
            active_graphs.append(cached_graphs[graph_name])
        except KeyError:
            active_graphs.append(html.H4(
                f"{graph_name} is not available: no info about user with domain '{domain}' in DB",
                style={'marginTop': 20, 'marginBottom': 20}
            ))

    return active_graphs


def dashboard(request, domain):
    """
    'dashboard/${domain}' page view - displays
    iframe with DjangoDash 'Graphs' app
    """
    global cached_graphs
    cached_graphs = {}
    query = VKToken.objects.filter(user__id=request.user.id)
    token = query[0].token if query else ''
    context = {
        'title': 'Dashboard | VK Tracker',
        'args': {
            'domain_id': {
                'value': domain
            },
            'token_id': {
                'value': token
            }
        }
    }
    return render(request, 'dashboard/graphs.html', context)
