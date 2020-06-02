import dash
import dash_html_components as html
import dash_core_components as dcc
from django.shortcuts import render
from . import graphs
from django_plotly_dash import DjangoDash
from main import mongo
from main.models import VKToken


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
    ])],
    className='jumbotron'
)
cached_graphs = {}

@app.callback(
    dash.dependencies.Output('graphs', 'children'),
    [dash.dependencies.Input('info-graphs-input', 'value'),
     dash.dependencies.Input('domain_id', 'value'),
     dash.dependencies.Input('token_id', 'value')])
def update_graph(selected_graphs, domain, token):
    active_graphs = []
    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
    user_info = storage.get_user(domain=domain)

    for i, graph_name in enumerate(selected_graphs):
        try:
            if graph_name not in cached_graphs:
                graph = graphs_dict[graph_name](user_info=user_info, token=token)
                cached_graphs[graph_name] = graph.create_graph()
            active_graphs.append(cached_graphs[graph_name])
        except KeyError:
            active_graphs.append(html.H4(
                f"{graph_name} graph is not available: no information about user with domain '{domain}' in DB",
                style={'marginTop': 20, 'marginBottom': 20}
            ))

    return active_graphs


def dash(request, domain):
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
