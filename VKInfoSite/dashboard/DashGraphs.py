import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.offline as plot_offline
import plotly.graph_objs as go
import pandas as pd
import json
from VK_UserInfo import *
from datetime import datetime as dt


class GenderPieChart:
    def __init__(self, user_info):
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

        labels = ['Male', 'Female']
        values = [counter['male'], counter['female']]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
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

    def __init__(self, user_info):
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
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])
        return graph


class PostsLikesGraph:

    def __init__(self, user_info):
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
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])
        return graph


class ActivityGraph:

    def __init__(self, user_info):
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
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])
        return graph


class UniversityDistributionGraph:

    def __init__(self, user_info):
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
                    data=[go.Pie(
                        labels=self._df['University'],
                        values=self._df['Count'])
                    ]
                )
            )
        ])
        return graph


class CitiesDistributionGraph:

    def __init__(self, user_info):
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
                    data=[go.Pie(
                        labels=self._df['City'],
                        values=self._df['Count'])
                    ]
                )
            )
        ])
        return graph


class CountriesDistributionGraph:

    def __init__(self, user_info):
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
                    data=[go.Pie(
                        labels=self._df['Country'],
                        values=self._df['Count'])
                    ]
                )
            )
        ])
        return graph


class AgeDistributionGraph:

    def __init__(self, user_info):
        self._df = pd.DataFrame({'Age': [], 'Count': []})
        for friend in user_info['friends']['items']:
            try:
                year = int(friend['bdate'].split('.')[-1])
                if year < 1000:
                    raise Exception
                age = dt.now().year - year
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
                    data=[go.Pie(
                        labels=self._df['Age'],
                        values=self._df['Count'])
                    ]
                )
            )
        ])
        return graph


class FriendsActivityGraph:

    def __init__(self, user_info):
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

        token = json.load(open('config/config.json', 'r'))['vk_token']
        vk_user = VK_UserInfo(token=token, domain=user_info['main_info']['domain'])
        for friend in user_info['friends']['items']:
            id = friend['id']
            mutual_friends = vk_user.get_mutual_friends(id=id)
            if id in df.index:
                df.loc[id, 'Mutual friends'] = len(mutual_friends) if mutual_friends else 0

        self._df = df

    def create_graph(self):
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
                            mode='markers',
                            opacity=0.7,
                            marker=dict(opacity=0.9,
                                        reversescale=True,
                                        colorscale='Blues',
                                        size=5),
                            line=dict(width=0.02),
                            name=self._df['Fullname'].values[0]
                        )
                    ],
                    'layout': go.Layout(
                        height=950,
                        #width=950,
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


if __name__ == '__main__':

    #friends_list = MongoDB().load_user_info(domain='ich_bin_sanya')['friends']['items']
    #print(GenderPieChart(friends_list=friends_list).create_graph())

    AgeDistributionGraph(VKMongoDB().load_user_info(domain='ivan_nikitinn')).create_graph()

    #data = VKMongoDB().load_user_info(domain='ivan_nikitinn')['wall']['items']
