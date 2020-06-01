import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import time
import vk
from datetime import datetime


class GenderDistributionPieChart:
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
            html.H4('Gender distribution', style={'text-align': 'center'}),
            dcc.Graph(
                id='gender-graph',
                figure=fig
            )
            ]
        )
        return graph


class UniversityDistributionPieChart:

    def __init__(self, user_info, **_):
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
        self._df = self._df.drop(0, errors='ignore')

    def create_graph(self):
        graph = html.Div([
            html.H4('University distribution', style={'text-align': 'center'}),
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


class CitiesDistributionPieChart:

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
            html.H4('Cities distribution', style={'text-align': 'center'}),
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


class CountriesDistributionPieChart:

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
            html.H4('Countries distribution', style={'text-align': 'center'}),
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


class AgeDistributionPieChart:

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
            html.H4('Age distribution', style={'text-align': 'center'}),
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


class FriendsActivityScatterPlot:

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
            html.H4('Friends activity', style={'text-align': 'center'}),
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
