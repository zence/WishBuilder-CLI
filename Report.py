import json
import os

class Report:
    def __init__(self, report_json: str=None):
        if not report_json:
            # Valid File Test
            self.valid_files = False
            self.valid_files_report = ''

            # Directory Test
            self.pass_directory_test = False
            self.directory_test_report = ''

            # Configuration File Text
            self.pass_configuration_test = False
            self.configuration_test_report = ''

            # File Path Test
            self.pass_file_test = False
            self.file_test_report = ''

            self.pass_tsv_test = False
            self.tsv_test_report = ''

            # Run User Scripts
            self.pass_script_test = False
            self.script_test_report = ''

            # Key File Test
            self.pass_key_test = False
            self.key_test_report = ''

            # Example Data table
            self.data_preview = ''
            self.meta_data_preview = ''

            # Data Test Cases
            self.pass_data_tests = False
            self.data_tests_report = ''

            # Other (updates and strings of previous status report, if this is true, only the other_content will be
            # used when cast to a string
            self.other = False
            self.other_content = ''
        else:
            report_dict = json.loads(report_json)

            # Valid File Test
            self.valid_files = report_dict['valid_files']
            self.valid_files_report = report_dict['valid_files_report']

            # Directory Test
            self.pass_directory_test = report_dict['pass_directory_test']
            self.directory_test_report = report_dict['directory_test_report']

            # Configuration File Text
            self.pass_configuration_test = report_dict['pass_configuration_test']
            self.configuration_test_report = report_dict['configuration_test_report']

            # File Path Test
            self.pass_file_test = report_dict['pass_file_test']
            self.file_test_report = report_dict['file_test_report']

            self.pass_tsv_test = report_dict['pass_tsv_test']
            self.tsv_test_report = report_dict['tsv_test_report']

            # Run User Scripts
            self.pass_script_test = report_dict['pass_script_test']
            self.script_test_report = report_dict['script_test_report']

            # Key File Test
            self.pass_key_test = report_dict['pass_key_test']
            self.key_test_report = report_dict['key_test_report']

            # Example Data table
            self.data_preview = report_dict['data_preview']
            self.meta_data_preview = report_dict['meta_data_preview']

            # Data Test Cases
            self.pass_data_tests = report_dict['pass_data_tests']
            self.data_tests_report = report_dict['data_tests_report']

            # Other
            if 'other' in report_dict.keys():
                self.other = report_dict['other']
                self.other_content = 'other_content'
            else:
                self.other = False
                self.other_content = ''

    def __str__(self) -> str:
        if self.other:
            return self.other_content
        else:
            out = self.valid_files_report
            out += self.directory_test_report
            out += self.configuration_test_report
            out += self.file_test_report
            out += self.script_test_report
            out += self.tsv_test_report
            out += self.key_test_report
            out += self.meta_data_preview
            out += self.data_preview
            out += self.data_tests_report

            return out

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
