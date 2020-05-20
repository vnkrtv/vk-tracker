import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import json
import time
import vk
from datetime import datetime


class GenderPieChart:
    def __init__(self, user_info, **kwargs):
        """
        :param friends_list: list of friends JSONs
        """
        self._data = user_info['friends']['items']

    def create_graph(self):
        counter = {
            'male': 0,
            'female': 0
        }

        for friend in self._data:
            gender = 'male' if friend['sex'] == 2 else 'female'
            counter[gender] = counter[gender] + 1

        labels = ['Female', 'Male']
        values = [counter['female'], counter['male']]

        fig = go.Figure(
            layout=dict(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            ),
            data=[go.Pie(labels=labels, values=values)]
        )
        fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                          marker=dict(colors=['red', 'blue'], line=dict(color='blue', width=2)))

        graph = html.Div([
            html.H3('Gender', style={'text-align': 'center'}),
            dcc.Graph(
                id='gender-graph',
                figure=fig
            )
            ]
        )
        return graph


class PhotoLikesGraph:

    def __init__(self, user_info, **kwargs):
        self._data = user_info['photos']['items']

    def create_graph(self):
        for photo in self._data:
            photo['likes'] = photo['likes']['count']
            photo['comments'] = photo['comments']['count']

        df = pd.DataFrame(self._data)
        graph = html.Div([
            html.H3('Photos activity', style={'text-align': 'center'}),
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
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])
        return graph


class PostsLikesGraph:

    def __init__(self, user_info, **kwargs):
        self._data = user_info['wall']['items']

    def create_graph(self):

        for post in self._data:
            post['likes'] = post['likes']['count']
            post['comments'] = post['comments']['count']

        df = pd.DataFrame(self._data)

        graph = html.Div([
            html.H3('Wall activity', style={'text-align': 'center'}),
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
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])
        return graph


class ActivityGraph:

    def __init__(self, user_info, **kwargs):
        self._data = user_info

    def create_graph(self):
        df = pd.DataFrame({'Likes': [], 'Comments': [], 'Fullname': []})

        for post in self._data['wall']['items']:
            for like in post['likes']['items']:
                id = like['id']

                if id in df.index:
                    df.loc[id, 'Likes'] = df.loc[id, 'Likes'] + 1
                else:
                    fullname = like['first_name'] + ' ' + like['last_name']
                    df.loc[id] = [1, 0, fullname]

            for comment in post['comments']['items']:
                id = comment['id']

                if id in df.index:
                    df.loc[id, 'Comments'] = df.loc[id, 'Comments'] + 1
                else:
                    fullname = like['first_name'] + ' ' + like['last_name']
                    df.loc[id] = [0, 1, fullname]

        for photo in self._data['photos']['items']:
            for like in photo['likes']['items']:
                id = like['id']

                if id in df.index:
                    df.loc[id, 'Likes'] = df.loc[id, 'Likes'] + 1
                else:
                    fullname = like['first_name'] + ' ' + like['last_name']
                    df.loc[id] = [1, 0, fullname]

            profiles = {
               item['id']: item['first_name'] + ' ' + item['last_name']
               for item in photo['comments']['profiles']
            }
            for item in photo['comments']['groups']:
                profiles[item['id']] = 'Group'

            for comment in photo['comments']['items']:
                id = comment['from_id']

                if id in df.index:
                    df.loc[id, 'Comments'] = df.loc[id, 'Comments'] + 1
                else:
                    fullname = profiles[id]
                    df.loc[id] = [0, 1, fullname]

        graph = html.Div([
            html.H3('Activity', style={'text-align': 'center'}),
            dcc.Graph(
                id='posts-likes',
                figure={
                    'data': [
                        go.Scatter(
                            x=df['Likes'],
                            y=df['Comments'],
                            text=df['Fullname'],
                            mode='markers',
                            opacity=0.7,
                            marker={
                                'size': 15,
                                'line': {'width': 0.5, 'color': 'white'}
                            },
                            name=df['Fullname'].values[0]
                        )
                    ],
                    'layout': go.Layout(
                        xaxis={'type': 'log', 'title': 'Likes'},
                        yaxis={'title': 'Comments'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])
        return graph


class UniversityDistributionGraph:

    def __init__(self, user_info, **kwargs):
        self._df = pd.DataFrame({'University': [], 'Count': []})

        for friend in user_info['friends']['items']:
            try:
                university = friend['university']
                if university in self._df.index:
                    self._df.loc[university, 'Count'] = self._df.loc[university, 'Count'] + 1
                else:
                    self._df.loc[university] = [friend['university_name'], 1]
            except:
                pass

        self._df = self._df.sort_values(['Count'])
        self._df = self._df.drop(0)

    def create_graph(self):
        graph = html.Div([
            html.H3('University distribution', style={'text-align': 'center'}),
            dcc.Graph(
                id='universities-distribution',
                figure=go.Figure(
                    layout=dict(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    ),
                    data=[go.Pie(
                        labels=self._df['University'],
                        values=self._df['Count'])
                    ]
                )
            )
        ])
        return graph


class CitiesDistributionGraph:

    def __init__(self, user_info, **kwargs):
        self._df = pd.DataFrame({'City': [], 'Count': []})

        for friend in user_info['friends']['items']:
            try:
                id = friend['city']['id']
                if id in self._df.index:
                    self._df.loc[id, 'Count'] = self._df.loc[id, 'Count'] + 1
                else:
                    self._df.loc[id] = [friend['city']['title'], 1]
            except:
                pass

        self._df = self._df.sort_values(['Count'])

    def create_graph(self):
        graph = html.Div([
            html.H3('Cities distribution', style={'text-align': 'center'}),
            dcc.Graph(
                id='cities-distribution',
                figure=go.Figure(
                    layout=dict(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    ),
                    data=[go.Pie(
                        labels=self._df['City'],
                        values=self._df['Count'])
                    ]
                )
            )
        ])
        return graph


class CountriesDistributionGraph:

    def __init__(self, user_info, **kwargs):
        self._df = pd.DataFrame({'Country': [], 'Count': []})

        for friend in user_info['friends']['items']:
            try:
                id = friend['country']['id']
                if id in self._df.index:
                    self._df.loc[id, 'Count'] = self._df.loc[id, 'Count'] + 1
                else:
                    self._df.loc[id] = [friend['country']['title'], 1]
            except:
                pass

        self._df = self._df.sort_values(['Count'])

    def create_graph(self):
        graph = html.Div([
            html.H3('Countries distribution', style={'text-align': 'center'}),
            dcc.Graph(
                id='countries-distribution',
                figure=go.Figure(
                    layout=dict(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    ),
                    data=[go.Pie(
                        labels=self._df['Country'],
                        values=self._df['Count'])
                    ]
                )
            )
        ])
        return graph


class AgeDistributionGraph:

    def __init__(self, user_info, **kwargs):
        self._df = pd.DataFrame({'Age': [], 'Count': []})
        for friend in user_info['friends']['items']:
            try:
                year = int(friend['bdate'].split('.')[-1])
                if year < 1000:
                    raise Exception
                age = datetime.now().year - year
                if age in self._df.index:
                    self._df.loc[age, 'Count'] = self._df.loc[age, 'Count'] + 1
                else:
                    self._df.loc[age] = [str(age) + ' y. o.', 1]
            except:
                pass

        self._df = self._df.sort_values(['Count'])

    def create_graph(self):
        graph = html.Div([
            html.H3('Age distribution', style={'text-align': 'center'}),
            dcc.Graph(
                id='countries-distribution',
                figure=go.Figure(
                    layout=dict(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    ),
                    data=[go.Pie(
                        labels=self._df['Age'],
                        values=self._df['Count'])
                    ]
                )
            )
        ])
        return graph


class FriendsActivityGraph:

    _token: str
    _timeout: float = 0.35

    def __init__(self, user_info, token, **kwargs):
        self._token = token
        df = pd.DataFrame({'Likes': [], 'Comments': [], 'Fullname': [], 'Mutual friends': []})
        for post in user_info['wall']['items']:
            for like in post['likes']['items']:
                id = like['id']

                if id in df.index:
                    df.loc[id, 'Likes'] = df.loc[id, 'Likes'] + 1
                else:
                    fullname = like['first_name'] + ' ' + like['last_name']
                    df.loc[id] = [1, 0, fullname, 0]

            for comment in post['comments']['items']:
                id = comment['id']

                if id in df.index:
                    df.loc[id, 'Comments'] = df.loc[id, 'Comments'] + 1
                else:
                    fullname = like['first_name'] + ' ' + like['last_name']
                    df.loc[id] = [0, 1, fullname, 0]

        for photo in user_info['photos']['items']:
            for like in photo['likes']['items']:
                id = like['id']

                if id in df.index:
                    df.loc[id, 'Likes'] = df.loc[id, 'Likes'] + 1
                else:
                    fullname = like['first_name'] + ' ' + like['last_name']
                    df.loc[id] = [1, 0, fullname, 0]

            if 'profiles' in photo['comments']:
                profiles = {
                    item['id']: item['first_name'] + ' ' + item['last_name']
                    for item in photo['comments']['profiles']
                }
            else:
                profiles = {}

            if 'groups' in photo['comments']:
                for item in photo['comments']['groups']:
                    profiles[item['id']] = 'Group'

            for comment in photo['comments']['items']:
                id = comment['from_id']

                if id in df.index:
                    df.loc[id, 'Comments'] = df.loc[id, 'Comments'] + 1
                else:
                    fullname = profiles[id]
                    df.loc[id] = [0, 1, fullname, 0]

        session = vk.API(vk.Session(access_token=self._token))
        code = """
            var friends = {friends};
            var res = [];
            var i = 0;
            while (i < friends.length) {{
                var mutual_friends = API.friends.getMutual({{
                        "source_uid": {user_id},
                        "target_uid": friends[i],
                    }});
                res.push(mutual_friends);
                i = i + 1;
            }}
            return res;
        """

        user_id = user_info['main_info']['id']
        friends_ids = [friend['id'] for friend in user_info['friends']['items']]

        # 25 - max API requests per one execute method
        friends_groups = list(zip(*[iter(friends_ids)] * 25))
        remaining_friends_count = len(friends_ids) - 25 * len(friends_groups)
        friends_groups.append(friends_ids[len(friends_ids) - remaining_friends_count:])

        for friends_group in friends_groups:
            friends = list(friends_group)
            req_code = code.format(user_id=user_id, friends=friends).replace('\n', '').replace('  ', '')

            for friend_id, mutual_friends in zip(friends, session.execute(code=req_code, v=5.102)):
                if friend_id in df.index:
                    df.loc[friend_id, 'Mutual friends'] = len(mutual_friends) if mutual_friends else 0
            time.sleep(self._timeout)

        self._df = df

    def create_graph(self):
        def get_hovertext(df):
            kwargs = {
                'name': df['Fullname'],
                'likes_count': df['Likes'],
                'comments_count': df['Comments'],
                'mut_friends_count': df['Mutual friends']
            }
            text = """
            {name}
            Likes: {likes_count}
            Comments: {comments_count}
            Mutual friends: {mut_friends_count}
            """.format(**kwargs)
            return text

        graph = html.Div([
            html.H3('Friends activity', style={'text-align': 'center'}),
            dcc.Graph(
                id='activity-distribution',
                figure={
                    'data': [
                        go.Scatter3d(
                            x=self._df['Likes'],
                            y=self._df['Comments'],
                            z=self._df['Mutual friends'],
                            text=self._df['Fullname'],
                            hovertemplate='%{text}<br>'
                                          'Likes: %{x}<br>'
                                          'Comments: %{y}<br>'
                                          'Mutual friends: %{z}'
                                          '<extra></extra>',
                            mode='markers',
                            opacity=0.7,
                            showlegend=False,
                            marker=dict(opacity=0.9,
                                        reversescale=True,
                                        colorscale='Blues',
                                        size=5),
                            line=dict(width=0.02),
                        )
                    ],
                    'layout': go.Layout(
                        height=950,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        scene=dict(
                            xaxis=dict(title="Likes"),
                            yaxis=dict(title="Comments"),
                            zaxis=dict(title="Mutual friends")
                        )
                    ),
                }

            )
        ],
        )
        return graph


class OnlineGraph:

    def __init__(self, activity_list, **kwargs):
        self._df = pd.DataFrame({
            'online':   [item['online'] for item in activity_list],
            'platform': [item['platform'] for item in activity_list],
            'time':     [item['time'] for item in activity_list]
        })

    def create_graph(self):
        graph = html.Div([
            html.H3('Online', style={'text-align': 'center'}),
            dcc.Graph(
                id='online-graph',
                figure=go.Figure(
                    layout=dict(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    ),
                    data=[go.Scatter(
                        x=self._df['time'],
                        y=self._df['online'],
                        name=self._df.at[i, 'platform'],
                        xaxis_range=['2016-07-01', '2016-12-31']
                    ) for i in range(len(self._df))]
                )
            )
        ])
        return graph


if __name__ == '__main__':
    with open('../db/ivan_nikitinn.txt', 'r') as file:
        data = json.load(file)

    app = dash.Dash(__name__)
    app.layout = OnlineGraph(activity_list=data).create_graph()
    app.run_server(debug=True)

    #  data = VKMongoDB().load_user_info(domain='ivan_nikitinn')['wall']['items']
