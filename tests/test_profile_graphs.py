import importlib.util
from datetime import date
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('graphs', Path(__file__).resolve().parents[1] / 'tools/generate_profile_graphs.py')
graphs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graphs)


class ProfileGraphsTests(unittest.TestCase):
    def test_calendar_handles_zero_and_formatted_counts(self):
        parser = graphs.CalendarParser()
        parser.feed('<td id="a" data-date="2026-01-01"></td><td id="b" data-date="2026-01-02"></td>'
                    '<tool-tip for="a">No contributions on January 1st.</tool-tip>'
                    '<tool-tip for="b">1,234 contributions on January 2nd.</tool-tip>')
        self.assertEqual(parser.days(), [(date(2026, 1, 1), 0), (date(2026, 1, 2), 1234)])

    def test_incomplete_calendar_fails_instead_of_publishing_false_zeroes(self):
        parser = graphs.CalendarParser()
        parser.feed('<td id="a" data-date="2026-01-01"></td>')
        with self.assertRaises(ValueError):
            parser.days()

    def test_languages_exclude_forks_and_empty_repositories(self):
        repos = [{'language': 'Python', 'fork': False}, {'language': 'Python', 'fork': True},
                 {'language': None, 'fork': False}]
        self.assertEqual(graphs.language_counts(repos), {'Python': 1})

    def test_months_stay_ordered_across_year_boundary(self):
        days = [(date(2025, 12, 31), 3), (date(2026, 1, 1), 2), (date(2026, 1, 2), 4)]
        self.assertEqual(graphs.monthly_counts(days), [('2025-12', 3), ('2026-01', 6)])

    def test_charts_handle_zero_activity_and_escape_labels(self):
        days = [(date(2026, 1, 1), 0)]
        for svg in (graphs.languages_chart(graphs.Counter({'A&B': 1})), graphs.languages_chart(graphs.Counter()),
                    graphs.activity_chart(days), graphs.heatmap_chart(days)):
            ET.fromstring(svg)
            self.assertNotIn('nan', svg)
            self.assertNotIn('inf', svg)
        self.assertIn('A&amp;B', graphs.languages_chart(graphs.Counter({'A&B': 1})))


if __name__ == '__main__':
    unittest.main()
