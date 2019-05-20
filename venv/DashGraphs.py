import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from threading import Thread


class NewThread(Thread):
    """
    A threading example
    """

    def __init__(self, name):
        """Инициализация потока"""
        Thread.__init__(self)
        self.name = name

    def run(self, data):
        super(NewThread, self).start()
        return GenderGraph(friends_list=data).run()


class GenderGraph:
    def __init__(self, friends_list):
        """

        :param friends_list: list of friends JSONs
        """
        self._data = friends_list

    def run(self):
        # external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

        app = dash.Dash("Friends graph")  # , external_stylesheets=external_stylesheets)

        counter = {
            'male': 0,
            'female': 0
        }

        for friend in self._data:
            gender = 'male' if friend['sex'] == 1 else 'female'
            counter[gender] = counter[gender] + 1

        app.layout = html.Div(children=[
            dcc.Graph(
                id='gender-graph',
                figure={
                    'data': [
                        {'x': [1], 'y': [counter['male']], 'type': 'bar', 'name': 'Male'},
                        {'x': [1], 'y': [counter['female']], 'type': 'bar', 'name': 'Female'},
                    ],
                    'layout': {
                        'title': 'Friends genders'
                    }
                }
            )
        ])

        port = 8050
        app.run_server(debug=False, port=port)
        return port


class PhotoLikesGraph:

    def __init__(self, photos_list):
        self._data = photos_list

    def run(self):
        app = dash.Dash("Photo likes")  # , external_stylesheets=external_stylesheets)

        for photo in self._data:
            photo['likes'] = photo['likes']['count']
            photo['comments'] = photo['comments']['count']

        df = pd.DataFrame(self._data)
        print(df)

        app.layout = html.Div([
            dcc.Graph(
                id='photos-likes',
                figure={
                    'data': [
                        go.Scatter(
                            x=df[df.index==i]['likes'].values,
                            y=df[df.index==i]['comments'].values,
                            text=str(df[df.index==i]['photo_id'].values[0]),
                            mode='markers',
                            opacity=0.7,
                            marker={
                                'size': 15,
                                'line': {'width': 0.5, 'color': 'white'}
                            },
                            name=str(df[df.index==i]['photo_id'].values[0])
                        ) for i in df.index
                    ],
                    'layout': go.Layout(
                        xaxis={'type': 'log', 'title': 'Comments'},
                        yaxis={'title': 'Likes'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])

        port = 8051
        app.run_server(debug=False, port=port)
        return port




class PostsLikesGraph:

    def __init__(self, posts_list):
        self._data = posts_list

    def run(self):
        app = dash.Dash("Posts likes")  # , external_stylesheets=external_stylesheets)

        for post in self._data:
            post['likes'] = post['likes']['count']
            post['comments'] = post['comments']['count']

        df = pd.DataFrame(self._data)
        print(df)

        app.layout = html.Div([
            dcc.Graph(
                id='posts-likes',
                figure={
                    'data': [
                        go.Scatter(
                            x=df[df.index==i]['likes'].values,
                            y=df[df.index==i]['comments'].values,
                            text=str(df[df.index==i]['post_id'].values[0]),
                            mode='markers',
                            opacity=0.7,
                            marker={
                                'size': 15,
                                'line': {'width': 0.5, 'color': 'white'}
                            },
                            name=str(df[df.index == i]['post_id'].values[0]),
                        ) for i in df.index
                    ],
                    'layout': go.Layout(
                        xaxis={'type': 'log', 'title': 'Likes'},
                        yaxis={'title': 'Comments'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])

        port = 8052
        app.run_server(debug=False, port=port)
        return port
