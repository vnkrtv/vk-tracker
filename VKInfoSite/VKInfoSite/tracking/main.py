import sys
from VK_UserActivity import *

if __name__ == '__main__':
    with open('../vktoken/vktoken.json', 'r') as file:
        token = json.load(file)['vk_token']

    try:
        data = VK_UserActivity(domain=sys.argv[1], token=token).get_activity()
    except Exception as e:
        print(e)
        exit(1)

    with open(f'/home/leadness/{sys.argv[1]}.txt', 'w') as file:
        json.dump(data, file)


class OnlineGraph:

    def __init__(self, activity_list, **kwargs):
        self._df = pd.DataFrame({
            'online':   [item['online'] for item in activity_list],
            'platform': [item['platform'] for item in activity_list],
            'time':     [item['time'] for item in activity_list]
        })

    def create_graph(self):
        graph = html.Div([
            html.H4('Online', style={'text-align': 'center'}),
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


class VKUserActivity(VKUser):

    def check_user_activity(self):
        user = self._session.users.get(user_ids=self._domain, fields='last_seen,online', v='5.103')[0]

        # is_online = user['online']
        # last_seen_timestamp = user['last_seen']['time']
        # last_seen_platform = user['last_seen']['platform'] - 1

        # self.load_activity(last_seen_timestamp, is_online, last_seen_platform)

    def get_activity(self):
        def parse_info(start_monitoring_timestamp, activity_list):
            platform_dict = {
                1: 'm.vk.com',
                2: 'iPhone app',
                3: 'iPad app',
                4: 'Android app',
                5: 'Windows Phone app',
                6: 'Windows 8 app',
                7: 'web (vk.com)',
                8: 'VK Mobile'
            }

            activity = []
            for info in activity_list:
                delta = (info & 0b111111111111111111111111111)
                online = (info >> 31)
                platform = (info >> 28 & 0b111) + 1
                timestamp = start_monitoring_timestamp + delta
                last_seen_time = datetime.fromtimestamp(timestamp)
                """
                activity.append({
                    'online':   online,
                    'platform': platform_dict[platform],
                    'minute':   last_seen_time.minute,
                    'hour':     last_seen_time.hour,
                    'day':      last_seen_time.day,
                    'month':    last_seen_time.month,
                    'year':     last_seen_time.year
                })
                """
                activity.append({
                    'online': online,
                    'platform': platform_dict[platform],
                    'time': last_seen_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            return activity

        with open('', 'r'):
            act = parse_info(self._id)
        return act

