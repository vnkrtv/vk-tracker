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
                 # ['Activity', 'ActivityGraph'],
                   ['University', 'UniversityDistributionGraph'],
                   ['City', 'CitiesDistributionGraph'],
                   ['Country', 'CountriesDistributionGraph'],
                   ['Age', 'AgeDistributionGraph'],
                   ['Friends activity', 'FriendsActivityGraph'],
                   ]

    external_stylesheets = ['static/main/css/bootstrap.css',
                            'static/main/css/bootstrap-grid.css',
                            'static/main/css/bootstrap-reboot.css']
    app = dash.Dash(name='VK User Info',
                    url_base_pathname="/graphs/",
                    external_stylesheets=external_stylesheets,
                    csrf_protect=False)
    app.config.suppress_callback_exceptions = True

    app.layout = html.Div([
        html.Div([
            html.H1([
                html.A('VK User Info', href='/', style={'color': 'black'})
            ]),
            html.Button('Back'),
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
    cached_graphs = {}

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

            if class_name not in cached_graphs:
                cached_graphs[class_name] = graph.create_graph()
            graphs.append(cached_graphs[class_name])

        return graphs

    return app


if __name__ == "__main__":
    app = _create_app()
    app.run_server()