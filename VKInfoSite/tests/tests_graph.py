# pylint: disable=invalid-name
"""
Dash graphs tests, covered graphs.py
"""
import json
from dashboard import graphs
from django.test import TestCase


class MainTest(TestCase):
    """

    """

    def setUp(self):
        """

        """
        with open('VKInfoSite/tests/tests_data/first_user.json', 'r') as file:
            self.user = json.load(file)


class GenderDistributionPieChartTest(MainTest):
    """

    """

    def test_creating_graph(self):
        """

        """
        graph = graphs.GenderDistributionPieChart(user_info=self.user)
        graph.create_graph()


class UniversityDistributionPieChartTest(MainTest):
    """

    """

    def test_creating_graph(self):
        """

        """
        graph = graphs.UniversityDistributionPieChart(user_info=self.user)
        graph.create_graph()


class AgeDistributionPieChartTest(MainTest):
    """

    """

    def test_creating_graph(self):
        """

        """
        graph = graphs.AgeDistributionPieChart(user_info=self.user)
        graph.create_graph()


class CountriesDistributionPieChartTest(MainTest):
    """

    """

    def test_creating_graph(self):
        """

        """
        graph = graphs.CountriesDistributionPieChart(user_info=self.user)
        graph.create_graph()


class CitiesDistributionPieChartTest(MainTest):
    """

    """

    def test_creating_graph(self):
        """

        """
        graph = graphs.CitiesDistributionPieChart(user_info=self.user)
        graph.create_graph()


class CitiesDistributionPieChartTest(MainTest):
    """

    """

    def test_creating_graph(self):
        """

        """
        graph = graphs.CitiesDistributionPieChart(user_info=self.user)
        graph.create_graph()
