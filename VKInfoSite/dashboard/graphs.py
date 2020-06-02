# pylint: disable=too-few-public-methods, too-many-branches
"""
Dash pie charts and scatter plot for visualization VK user info
"""
from datetime import datetime
import time
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import vk


class GenderDistributionPieChart:
    """Class for creating gender distribution pie chart"""

    def __init__(self, user_info: dict, **_):
        """
        Get data for pie chart

        :param user_info: dict with all VK user info
        :param _: useless params
        """
        self._data = user_info['friends']['items']

    def create(self) -> html.Div:
        """
        Create gender distribution pie chart

        :return: html.Div component with title and pie chart
        """
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
                plot_bgcolor='rgba(0,0,0,0)'),
            data=[go.Pie(labels=labels, values=values)]
        )
        fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                          marker=dict(colors=['red', 'blue'], line=dict(color='blue', width=2)))

        graph = html.Div([
            html.H4('Gender distribution', style={'text-align': 'center'}),
            dcc.Graph(
                id='gender-graph',
                figure=fig)
        ])
        return graph


class UniversityDistributionPieChart:
    """Class for creating universities distribution pie chart"""

    def __init__(self, user_info: dict, **_):
        """
        Get data for pie chart

        :param user_info: dict with all VK user info
        :param _: useless params
        """
        self._df = pd.DataFrame({'University': [], 'Count': []})
        for friend in user_info['friends']['items']:
            university = friend.get('university', -1)
            if university in self._df.index:
                self._df.loc[university, 'Count'] = self._df.loc[university, 'Count'] + 1
            else:
                self._df.loc[university] = [friend.get('university_name', 'Not specified'), 1]

        self._df = self._df.sort_values(['Count'])
        self._df = self._df.drop(0, errors='ignore')

    def create(self) -> html.Div:
        """
        Create universities distribution pie chart

        :return: html.Div component with title and pie chart
        """
        graph = html.Div([
            html.H4('University distribution', style={'text-align': 'center'}),
            dcc.Graph(
                id='universities-distribution',
                figure=go.Figure(
                    layout=dict(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'),
                    data=[go.Pie(
                        labels=self._df['University'],
                        values=self._df['Count'])]
                )
            )
        ])
        return graph


class CitiesDistributionPieChart:
    """Class for creating cities distribution pie chart"""

    def __init__(self, user_info: dict, **_):
        """
        Get data for pie chart

        :param user_info: dict with all VK user info
        :param _: useless params
        """
        self._df = pd.DataFrame({'City': [], 'Count': []})

        for friend in user_info['friends']['items']:
            not_specified_city = {'id': -1, 'title': 'Not specified'}
            city = friend.get('city', not_specified_city)
            city_id = city['id']
            if city_id in self._df.index:
                self._df.loc[city_id, 'Count'] = self._df.loc[city_id, 'Count'] + 1
            else:
                self._df.loc[city_id] = [city['title'], 1]

        self._df = self._df.sort_values(['Count'])

    def create(self) -> html.Div:
        """
        Create cities distribution pie chart

        :return: html.Div component with title and pie chart
        """
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
                        values=self._df['Count'])]
                )
            )
        ])
        return graph


class CountriesDistributionPieChart:
    """Class for creating countries distribution pie chart"""

    def __init__(self, user_info: dict, **_):
        """
        Get data for pie chart

        :param user_info: dict with all VK user info
        :param _: useless params
        """
        self._df = pd.DataFrame({'Country': [], 'Count': []})

        for friend in user_info['friends']['items']:
            not_specified_country = {'id': -1, 'title': 'Not specified'}
            country = friend.get('country', not_specified_country)
            country_id = country['id']
            if country_id in self._df.index:
                self._df.loc[country_id, 'Count'] = self._df.loc[country_id, 'Count'] + 1
            else:
                self._df.loc[country_id] = [country['title'], 1]

        self._df = self._df.sort_values(['Count'])

    def create(self) -> html.Div:
        """
        Create countries distribution pie chart

        :return: html.Div component with title and pie chart
        """
        graph = html.Div([
            html.H4('Countries distribution', style={'text-align': 'center'}),
            dcc.Graph(
                id='countries-distribution',
                figure=go.Figure(
                    layout=dict(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'),
                    data=[go.Pie(
                        labels=self._df['Country'],
                        values=self._df['Count'])]
                )
            )
        ])
        return graph


class AgeDistributionPieChart:
    """Class for creating age distribution pie chart"""

    def __init__(self, user_info: dict, **_):
        """
        Get data for pie chart

        :param user_info: dict with all VK user info
        :param _: useless params
        """
        self._df = pd.DataFrame({'Age': [], 'Count': []})
        for friend in user_info['friends']['items']:
            try:
                year = int(friend['bdate'].split('.')[-1])
                if year < 1000:
                    continue
                age = datetime.now().year - year
                if age in self._df.index:
                    self._df.loc[age, 'Count'] = self._df.loc[age, 'Count'] + 1
                else:
                    self._df.loc[age] = [str(age) + ' y. o.', 1]
            except KeyError:
                pass
        self._df = self._df.sort_values(['Count'])

    def create(self) -> html.Div:
        """
        Create age distribution pie chart

        :return: html.Div component with title and pie chart
        """
        graph = html.Div([
            html.H4('Age distribution', style={'text-align': 'center'}),
            dcc.Graph(
                id='countries-distribution',
                figure=go.Figure(
                    layout=dict(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'),
                    data=[go.Pie(
                        labels=self._df['Age'],
                        values=self._df['Count'])]
                )
            )
        ])
        return graph


class FriendsActivityScatterPlot:
    """Class for creating friends activity scatter plot"""

    _timeout: float = 0.35
    _v: float = 5.102

    def __init__(self, user_info: dict, token: str):
        """
        Get data for scatter plot and load
        mutual friends by VK API

        :param user_info: dict with all VK user info
        :param token: VK token with all rights
        """
        self._token = token
        self._df = FriendsActivityScatterPlot.parse_info(user_info)
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
                if (!mutual_friends) {{
                    mutual_friends = [];
                }}
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
            req_code = code.format(user_id=user_id, friends=friends)
            mutual_friends_ids_list = session.execute(code=req_code, v=self._v)

            for friend_id, mutual_friends_ids in zip(friends, mutual_friends_ids_list):
                if friend_id in self._df.index:
                    self._df.loc[friend_id, 'Mutual friends'] = len(mutual_friends_ids)

            time.sleep(self._timeout)

    @staticmethod
    def parse_info(user_info: dict) -> pd.DataFrame:
        """
        Parse user info dict to pandas DataFrame

        :param user_info: dict with all user info
        :return: DataFrame with friends activity
        """
        tmp_df = pd.DataFrame({'Likes': [], 'Comments': [], 'Fullname': [], 'Mutual friends': []})
        for post in user_info['wall']['items']:
            for like in post['likes']['items']:
                user_id = like['id']

                if user_id in tmp_df.index:
                    tmp_df.loc[user_id, 'Likes'] = tmp_df.loc[user_id, 'Likes'] + 1
                else:
                    fullname = like['first_name'] + ' ' + like['last_name']
                    tmp_df.loc[user_id] = [1, 0, fullname, 0]

            for comment in post['comments']['items']:
                user_id = comment['id']

                if user_id in tmp_df.index:
                    tmp_df.loc[user_id, 'Comments'] = tmp_df.loc[user_id, 'Comments'] + 1
                else:
                    fullname = comment['first_name'] + ' ' + comment['last_name']
                    tmp_df.loc[user_id] = [0, 1, fullname, 0]

        for photo in user_info['photos']['items']:
            for like in photo['likes']['items']:
                user_id = like['id']

                if user_id in tmp_df.index:
                    tmp_df.loc[user_id, 'Likes'] = tmp_df.loc[user_id, 'Likes'] + 1
                else:
                    fullname = like['first_name'] + ' ' + like['last_name']
                    tmp_df.loc[user_id] = [1, 0, fullname, 0]

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
                user_id = comment['from_id']

                if user_id in tmp_df.index:
                    tmp_df.loc[user_id, 'Comments'] = tmp_df.loc[user_id, 'Comments'] + 1
                else:
                    fullname = profiles[user_id]
                    tmp_df.loc[user_id] = [0, 1, fullname, 0]
        return tmp_df

    def create(self) -> html.Div:
        """
        Create friends activity scatter plot

        :return: html.Div component with title and scatter plot
        """
        graph = html.Div([
            html.H4('Friends activity', style={'text-align': 'center'}),
            dcc.Graph(
                id='activity-scatter',
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
                            zaxis=dict(title="Mutual friends"))
                    ),
                }

            )
        ])
        return graph
