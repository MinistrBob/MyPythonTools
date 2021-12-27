import unittest
import os
import shutil
from tempfile import gettempdir
from datetime import datetime
from ControlVeeamBackup import get_list_current_vbk, get_list_current_vms


class TestControlVeeamBackup(unittest.TestCase):
    # get temp folder for test
    temp_folder = ''
    list_filename = ['DNS1D2020-08-29T221034_971F.vbk', 'DNS2D2020-08-29T221232_6C3A.vbk',
                     'pm-jiraD2020-11-11T213840_0437.vbk', 'pm-jiraD2020-11-28T093153_A971.vbk',
                     'pm-nginxD2020-11-11T213859_97A2.vbk', 'pm-postgresqlD2020-11-11T213853_0921.vbk',
                     'pm-postgresqlD2020-11-28T094057_5DE7.vbk']
    result_filename = {'DNS1': [datetime(2020, 8, 29, 0, 0), 1],
                       'DNS2': [datetime(2020, 8, 29, 0, 0), 1],
                       'pm-jira': [datetime(2020, 11, 28, 0, 0), 2],
                       'pm-nginx': [datetime(2020, 11, 11, 0, 0), 1],
                       'pm-postgresql': [datetime(2020, 11, 28, 0, 0), 2]}

    def setUp(self):
        # get OS temp folder
        temp_path = gettempdir()
        # get temp folder for test
        self.temp_folder = os.path.join(temp_path, 'temp_folder')
        # print(self.temp_folder)
        # delete test folder
        if os.path.exists(self.temp_folder):
            try:
                shutil.rmtree(self.temp_folder)
            except OSError:
                print(f"Delete directory {self.temp_folder} failed")
                exit(1)
        # create test folder
        try:
            os.mkdir(self.temp_folder)
        except OSError:
            print(f"Creation test directory {self.temp_folder} failed")
            exit(1)
        # create test files
        for one_file in self.list_filename:
            try:
                with open(os.path.join(self.temp_folder, one_file), 'w') as fp:
                    fp.write("---")
            except OSError:
                print(f"Creation test files {os.path.join(self.temp_folder, one_file)} failed")
                exit(1)

    def tearDown(self):
        pass

    def test_get_list_current_vbk(self):
        # print(self.temp_folder)
        self.assertEqual(get_list_current_vbk(self.temp_folder), self.result_filename)

    def test_get_list_current_vms(self):
        self.assertTrue(type(get_list_current_vms()) is dict)


if __name__ == '__main__':
    unittest.main()
