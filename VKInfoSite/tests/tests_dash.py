# pylint: disable=invalid-name
"""
Dash graphs tests, covered graphs.py
"""
import json
from unittest import mock
from django.test import TestCase
from django.urls import reverse
from dashboard import graphs


class MainTest(TestCase):
    """
    Base class for all tests
    """

    def setUp(self):
        """
        Load user data for graphs
        """
        with open('VKInfoSite/tests/tests_data/first_user.json', 'r') as file:
            self.user = json.load(file)


class GenderDistributionPieChartTest(MainTest):
    """
    Test for GenderDistributionPieChart graph
    """

    def test_creating_graph(self):
        """
        Test for creating GenderDistributionPieChart graph
        """
        graph = graphs.GenderDistributionPieChart(user_info=self.user)
        graph.create_graph()


class UniversityDistributionPieChartTest(MainTest):
    """
    Test for UniversityDistributionPieChart graph
    """

    def test_creating_graph(self):
        """
        Test for creating UniversityDistributionPieChart graph
        """
        graph = graphs.UniversityDistributionPieChart(user_info=self.user)
        graph.create_graph()


class AgeDistributionPieChartTest(MainTest):
    """
    Test for AgeDistributionPieChart graph
    """

    def test_creating_graph(self):
        """
        Test for creating AgeDistributionPieChart graph
        """
        graph = graphs.AgeDistributionPieChart(user_info=self.user)
        graph.create_graph()


class CountriesDistributionPieChartTest(MainTest):
    """
    Test for CountriesDistributionPieChart graph
    """

    def test_creating_graph(self):
        """
        Test for creating CountriesDistributionPieChart
        """
        graph = graphs.CountriesDistributionPieChart(user_info=self.user)
        graph.create_graph()


class CitiesDistributionPieChartTest(MainTest):
    """
    Test for CitiesDistributionPieChart graph
    """

    def test_creating_graph(self):
        """
        Test for creating CitiesDistributionPieChart graph
        """
        graph = graphs.CitiesDistributionPieChart(user_info=self.user)
        graph.create_graph()


class FriendsActivityScatterPlotTest(MainTest):
    """
    Test for FriendsActivityScatterPlot graph
    """
    @mock.patch('dashboard.graphs.vk.API')
    def test_creating_graph(self, vk_api):
        """
        Test for creating FriendsActivityScatterPlot graph
        """
        with open('VKInfoSite/tests/tests_data/first_user.json', 'r') as file:
            user = json.load(file)
        vk_api.execute.return_value = user['friends']['items']
        graph = graphs.FriendsActivityScatterPlot(user_info=self.user, token='token')
        graph.create_graph()


class DashViewTest(MainTest):
    """
    Test for displaying page with graphs
    """

    def test_dash(self):
        """
        Test for displaying iframe with graphs
        """
        domain = self.user['main_info']['domain']
        response = self.client.get(reverse('dashboard:dash', args=(domain,)),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<iframe src="/django_plotly_dash/app/Graphs/initial/')
