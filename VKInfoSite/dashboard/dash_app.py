from MongoDB import VKMongoDB
from .DashGraphs import *


def dispatcher(request, domain):
    app = _create_app(domain)
    app.config['suppress_callback_exceptions'] = True
    params = {
        'data': request.body,
        'method': request.method,
        'content_type': request.content_type
    }
    with app.server.test_request_context(request.path, **params):
        app.server.preprocess_request()
        try:
            response = app.server.full_dispatch_request()
        except Exception as e:
            response = app.server.make_responce(app.server.handle_exception(e))
        return response.get_data()


def _create_app(domain):
    graphs_list = [['Gender', 'GenderPieChart'],
                   ['Activity', 'ActivityGraph'],
                   ['University', 'UniversityDistributionGraph'],
                   ['City', 'CitiesDistributionGraph'],
                   ['Country', 'CountriesDistributionGraph'],
                   ['Age', 'AgeDistributionGraph'],
                   ['Friends activity', 'FriendsActivityGraph'],
                   ]

    app = dash.Dash(name='VK User Info',
                    url_base_pathname="/graphs/",
                    csrf_protect=False)
    app.config.suppress_callback_exceptions = True

    app.layout = html.Div([
        html.Div([
            html.H1([
                html.A('VK User Info', href='/', style={'color': 'black'})
            ]),
            dcc.Dropdown(
                id='info-graphs-input',
                options=[{'label': s[0], 'value': s[1]} for s in graphs_list],
                value=['GenderPieChart'],
                multi=True,
            ),
            html.Div(id='graphs')
        ],
            className='container'
        )
    ],
        className='jumbotron'
    )

    @app.callback(
        dash.dependencies.Output('graphs', 'children'),
        [dash.dependencies.Input('info-graphs-input', 'value')]
    )
    def update_graph(graphs_list):
        graphs = []
        print(graphs_list)
        config = json.load(open('config/config.json', 'r'))
        for i, class_name in enumerate(graphs_list):
            try:
                user_info = VKMongoDB(
                    host=config['mdb_host'],
                    port=config['mdb_port']
                ).load_user_info(domain=domain)
                graph = eval(class_name)(user_info=user_info)
            except:
                graphs.append(html.H3(
                    '{} graph is not available'.format(class_name),
                    style={'marginTop': 20, 'marginBottom': 20}
                ))
                continue

            graphs.append(graph.create_graph())

        return graphs

    return app


if __name__ == "__main__":
    app = _create_app()
    app.run_server()

"""
        for i, class_name in enumerate(graphs_list):
            try:
                user_info = VKMongoDB().load_user_info(domain=domain)
                graph = type(class_name, (), {'user_info': user_info}).create_graph()
            except:
                graphs.append(html.H3(
                    'Graph is not available for {}'.format('you'),
                    style={'marginTop': 20, 'marginBottom': 20}
                ))
                continue

            graphs.append(graph)"""