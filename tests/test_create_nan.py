import os
import shutil
import unittest
import networkx as nx
import numpy as np
from geoframepy.timeseries.files_utils import process_network_to_timeseries
from geoframepy.timeseries.io_csv import pandas_read_OMS_timeseries


class TestProcessNetworkToTimeseries(unittest.TestCase):

    def setUp(self):
        self.net = nx.DiGraph()
        self.net.add_edges_from([(1, 2), (2, 3)])
        self.root_path = './tests/test_output'
        if os.path.exists(self.root_path):
            shutil.rmtree(self.root_path)
        os.makedirs(self.root_path)

    def tearDown(self):
        if os.path.exists(self.root_path):
            shutil.rmtree(self.root_path)

    def test_process_network_to_timeseries(self):
        process_network_to_timeseries(self.net, self.root_path, "2024-01-01 00:00", "2024-01-01 10:00", "H")
        for node in self.net.nodes:
            file_path = os.path.join(self.root_path, f"{node}", f"Nan_{node}.csv")
            print(os.getcwd())
            self.assertTrue(os.path.isfile(file_path), f"File {file_path} was not created.")
            df = pandas_read_OMS_timeseries(file_path)
            self.assertEqual(len(df), 11, "The number of rows in the CSV file is incorrect.")
            self.assertTrue((df.columns == [str(node)]).all(), "Column names are incorrect.")
            self.assertTrue(df[str(node)].isna().all(), "The values in the CSV file are incorrect.")


if __name__ == '__main__':
    unittest.main()
