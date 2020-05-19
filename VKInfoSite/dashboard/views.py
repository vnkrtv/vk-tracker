from django.shortcuts import render

from .graphs import *
from django_plotly_dash import DjangoDash
from main import mongo


app = DjangoDash(name='Graphs', id='domain_id', serve_locally=True)

graphs_list = [['Gender', 'GenderPieChart'],
               ['University', 'UniversityDistributionGraph'],
               ['City', 'CitiesDistributionGraph'],
               ['Country', 'CountriesDistributionGraph'],
               ['Age', 'AgeDistributionGraph'],
               ['Friends activity', 'FriendsActivityGraph']]

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='info-graphs-input',
            options=[{'label': s[0], 'value': s[1]} for s in graphs_list],
            value=['GenderPieChart'],
            multi=True,
        ),
        dcc.Input(id='domain_id', type='hidden', value=''),
        html.Div(id='graphs')
    ],
    )
],
)
cached_graphs = {}


@app.callback(
    dash.dependencies.Output('graphs', 'children'),
    [dash.dependencies.Input('info-graphs-input', 'value'),
     dash.dependencies.Input('domain_id', 'value')]
)
def update_graph(graphs_list, domain):
    graphs = []
    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())

    for i, class_name in enumerate(graphs_list):
        try:
            user_info = storage.get_user(domain=domain)
            graph = eval(class_name)(user_info=user_info)
        except ValueError:
            graphs.append(html.H3(
                '{} graph is not available'.format(class_name),
                style={'marginTop': 20, 'marginBottom': 20}
            ))
            continue

        if class_name not in cached_graphs:
            cached_graphs[class_name] = graph.create_graph()
        graphs.append(cached_graphs[class_name])

    return graphs


def dash(request, domain):
    return render(request, 'dashboard/graphs.html', {'data': {'domain_id': {'value': domain}}})
