from django.shortcuts import render

from .graphs import *
from django_plotly_dash import DjangoDash
from main import mongo
from main.models import VKToken


app = DjangoDash(name='Graphs',
                 id='domain_id,token_id',
                 serve_locally=True,
                 add_bootstrap_links=True)

graphs_list = [['Gender', 'GenderPieChart'],
               ['University', 'UniversityDistributionGraph'],
               ['City', 'CitiesDistributionGraph'],
               ['Country', 'CountriesDistributionGraph'],
               ['Age', 'AgeDistributionGraph'],
               ['Friends activity', 'FriendsActivityGraph']]

app.layout = html.Div([
    html.H2('Graphs'),
    html.Div([
        dcc.Dropdown(
            id='info-graphs-input',
            options=[{'label': s[0], 'value': s[1]} for s in graphs_list],
            value=['GenderPieChart'],
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
     dash.dependencies.Input('token_id', 'value')]
)
def update_graph(graphs_list, domain, token):
    graphs = []
    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
    user_info = storage.get_user(domain=domain)

    for i, class_name in enumerate(graphs_list):
        try:
            if class_name not in cached_graphs:
                graph = eval(class_name)(user_info=user_info, token=token)
                cached_graphs[class_name] = graph.create_graph()
            graphs.append(cached_graphs[class_name])
        except ValueError:
            graphs.append(html.H3(
                '{} graph is not available'.format(class_name),
                style={'marginTop': 20, 'marginBottom': 20}
            ))

    return graphs


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
