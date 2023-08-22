import unittest
from unittest.mock import MagicMock, patch
from unittest import mock
import pandas as pd
from pyICU.connection.Connector import SQLDBConnector


class SQLDBConnectorTestCase(unittest.TestCase):
    def setUp(self):
        self.test_item_identifier = 'creatinine'
        self.engine_mock = MagicMock()
        self.connector = SQLDBConnector(self.engine_mock)

    def test_load_concepts(self):
        # Assuming you have a test concepts.json file in your test directory
        concepts = self.connector.load_concepts(json_file='concepts.json')
        self.assertTrue(isinstance(concepts, dict))
        self.assertTrue(self.test_item_identifier in concepts)
        self.assertEqual(type(concepts[self.test_item_identifier]), type({}))
        self.assertEqual(
            type(concepts[self.test_item_identifier]['label']), str)
        self.assertEqual(
            type(concepts[self.test_item_identifier]['description']), str)

    def test_execute_query(self):
        query = "SELECT * FROM table"
        expected_result = pd.DataFrame(
            {"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        self.engine_mock.return_value = expected_result

        result = self.connector.execute_query(query)

        self.assertEqual(result, expected_result)
        self.engine_mock.assert_called_once_with(
            query, self.connector.sqla_engine, params=None)

    def test_execute_query_file(self):
        file_path = "query.sql"
        query = "SELECT * FROM table"
        expected_result = pd.DataFrame(
            {"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        self.engine_mock.return_value = expected_result

        with patch("builtins.open", create=True) as open_mock:
            open_mock.return_value.__enter__.return_value.read.return_value = query

            result = self.connector.execute_query_file(file_path)

            self.assertEqual(result, expected_result)
            self.engine_mock.assert_called_once_with(
                query, self.connector.sqla_engine, params=None)
            open_mock.assert_called_once_with(file_path, 'r')

    def test_execute_query_folder(self):
        folder_path = "queries"
        query_files: list[str] = ["query1.sql", "query2.sql"]
        queries: list[str] = ["SELECT * FROM table1", "SELECT * FROM table2"]
        expected_results: list[pd.DataFrame] = [
            pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]}),
            pd.DataFrame({"col3": [4, 5, 6], "col4": ["d", "e", "f"]}),
        ]
        self.engine_mock.side_effect = expected_results

        with patch("os.listdir") as listdir_mock:
            listdir_mock.return_value = query_files
            with patch("builtins.open", create=True) as open_mock:
                open_mock.return_value.__enter__.return_value.read.side_effect = queries

                result = self.connector.execute_query_folder(folder_path)

                expected_result: pd.DataFrame = pd.concat(expected_results)
                self.assertEqual(result, expected_result)
                self.assertEqual(self.engine_mock.call_count, 2)
                open_mock.assert_has_calls(
                    [mock.call(f"{folder_path}/{file}", 'r') for file in query_files])

    def test_get_concept(self):

        assert self.connector.get_concept(
            self.test_item_identifier) == self.connector.concepts[self.test_item_identifier]


if __name__ == '__main__':
    unittest.main()
