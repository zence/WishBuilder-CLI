import gzip, os, sys
from Constants import *
import pandas as pd
from PullRequest import PullRequest
from Shared import *

def get_test_file_path(data_file_path):
    return os.path.dirname(data_file_path) + '/test_' + os.path.basename(data_file_path).rstrip('.gz')

def get_data_file_path(test_file_path):
    return os.path.dirname(test_file_path) + "/" + os.path.basename(test_file_path).lstrip("test_") + ".gz"

# Check if there is a test file for every data file
def check_test_for_every_data(pr: PullRequest, gz_file_paths, test_file_paths):
    printToLog("Running check_test_for_every_data", pr)
    report = "### Testing Files:\n\n"
    passed = True

    for f in gz_file_paths:
        test_file_path = get_test_file_path(f)

        if not os.path.exists(test_file_path):
            printToLog("Data file {} is missing required test file {}.".format(os.path.basename(f), os.path.basename(test_file_path)), pr)
            report += "{}\tData file {} is missing required test file {}.\n\n".format(RED_X, os.path.basename(f), os.path.basename(test_file_path))
            passed = False

    for f in test_file_paths:
        data_file_path = get_data_file_path(f)

        if not os.path.exists(data_file_path):
            printToLog("Test file {} is missing required data file {}".format(os.path.basename(f), os.path.basename(data_file_path)), pr)
            report += "{}\tTest file {} is missing required data file {}\n\n".format(RED_X, os.path.basename(f), os.path.basename(data_file_path))
            passed = False

    pr.report.pass_key_test = passed

    if not passed:
        report += "#### Results: FAIL\n\n"
        pr.report.key_test_report = report
    else:
        r, passed = check_test_files(test_file_paths, pr)
        report += r
        pr.report.key_test_report = report

        if passed:
            report, passed, num_samples = compare_files(gz_file_paths, test_file_paths, pr)
            pr.num_samples = num_samples
            pr.report.data_tests_report = report
            pr.report.pass_data_tests = passed

    return passed

def get_num_data_features(data_file_path):
    printToLog("Checking how many variables are in {}".format(data_file_path), pr)

    header_items = None
    with gzip.open(data_file_path) as data_file:
        header_items = data_file.readline().decode().rstrip("\n").split("\t")

    return len(header_items)

# Are all test files in correct format?
def check_test_files(test_file_list, pr):
    printToLog("Running check_test_files", pr)

    min_samples = MIN_SAMPLES
    min_test_cases = MIN_TEST_CASES
    report = ''
    passed = True

    for f in test_file_list:
#        min_features = MIN_FEATURES
#        data_file_path = get_data_file_path(f)
#        num_data_features = get_num_data_features(data_file_path)
#
#        if num_data_features == 1:
#            min_features = 1

        row_count = 0
        samples = {}

        report += "#### Running \"{0}\"\n\n".format(f)

        with open(f, 'r') as test_file:
            headers = test_file.readline().rstrip('\n').split('\t')
            # Make sure there are three columns named Sample, Variable, Value
            passed, temp_report = check_test_columns(headers, f, pr)
            if passed:
                report += "{check_mark}\t\"{0}\" has three columns with the correct headers\n\n"\
                    .format(os.path.basename(f), check_mark=CHECK_MARK)
            else:
                report += temp_report

            for line in test_file:
                row_count += 1
                data = line.rstrip('\n').split('\t')
                if len(data) is not 3 and len(data) is not 0:  # Make sure each row has exactly three columns
                    report += "{red_x}\tRow {0} of \"{1}\" should contain exactly three columns\n\n"\
                        .format(row_count, os.path.basename(f), red_x=RED_X)
                    passed = False
                elif len(data) != 0:  # Add data to a map
                    if data[0] not in samples.keys():
                        samples[data[0]] = [data[1] + data[2]]
                    else:
                        if data[1] + data[2] not in samples[data[0]]:
                            samples[data[0]].append(data[1] + data[2])

        if len(samples.keys()) < min_samples:  # Make sure there are enough unique sample IDs to test
            report += "{red_x}\t\"{0}\" does not contain enough unique samples to test (min: {1})\n\n"\
                .format(os.path.basename(f), min_samples, red_x=RED_X)
            passed = False
        else:
            report += "{check_mark}\t\"{0}\" contains enough unique samples to test\n\n"\
                .format(os.path.basename(f), check_mark=CHECK_MARK)

#        for sample in samples:  # Make sure each sample has enough features to test
#            if len(samples[sample]) < min_features:
#                report += "{red_x}\tSample \"{0}\" does not have enough features to test (min: {1})\n\n"\
#                    .format(sample, min_features, red_x=RED_X)
#                passed = False
#
#        if passed:
#            report += "{check_mark}\t\"{0}\" has enough features to test (min: {1}) for every sample\n\n"\
#                .format(os.path.basename(f), min_features, check_mark=CHECK_MARK)

        if row_count == 0:  # Check if file is empty
            report += "{red_x}\t\"{0}\" is empty.\n\n".format(f, red_x=RED_X)
            passed = False
        elif row_count < min_test_cases:  # Check if there are enough test cases
            report += "{red_x}\t\"{0}\" does not contain enough test cases ({1}; min: {2})\n\n"\
                .format(os.path.basename(f), row_count, min_test_cases, red_x=RED_X)
            passed = False
        else:
            report += "{check_mark}\t\"{0}\" contains enough test cases ({1}; min: {2})\n\n"\
                .format(os.path.basename(f), row_count, min_test_cases, check_mark=CHECK_MARK)

    if passed:
        report += "#### Results: PASS\n---\n"
    else:
        report += "#### Results: FAIL\n---\n"

    return report, passed

# Check if the column headers of the test f are "Sample", "Variable", and "Value"
def check_test_columns(col_headers, file, pr):
    printToLog("Running check_test_columns", pr)
    passed = True
    report = ""

    if len(col_headers) != 3:  # Make sure there are exactly three columns
        report += "{red_x}\t\"{0}\" does not contain three columns\n\n".format(file, red_x=RED_X)
        passed = False
    else:  # Check the names of each column
        if col_headers[0] != "Sample" and col_headers[0] != "SampleID":
            report += "{red_x}\tFirst column of \"{0}\" must be titled \"Sample\"\n\n'".format(file, red_x=RED_X)
            passed = False
        if col_headers[1] != "Variable":
            report += "{red_x}\tSecond column of \"{0}\" must be titled \"Variable\"\n\n".format(file, red_x=RED_X)
            passed = False
        if col_headers[2] != "Value":
            report += "{red_x}\tThird column of \"{0}\" must be titled \"Value\"\n\n')".format(file, red_x=RED_X)
            passed = False

    return passed, report

def compare_files(data_file_list, test_file_list, pr):
    printToLog("Running compare_files", pr)
    passed = True
    report = "### Comparing Files:\n\n"
    unique_samples = set()

    for data_file_path in data_file_list:
        test_file_path = get_test_file_path(data_file_path)
        test_dict = {}

        with open(test_file_path, 'r') as test_file:
            column_headers = test_file.readline().rstrip('\n').split('\t')

            for line in test_file:
                test_data = line.rstrip('\n').split('\t')

                if len(test_data) != 3:
                    printToLog("Invalid test line in {}: {}".format(os.path.basename(test_file_path), test_data), pr)
                    report += "{red_x}\tInvalid test line in {}: {}".format(os.path.basename(test_file_path), test_data) + "\n\n"
                    passed = False
                    continue

                sample = test_data[0]
                variable = test_data[1]
                value = test_data[2]

                if sample not in test_dict:
                    test_dict[sample] = {}

                test_dict[sample][variable] = value

        report += "#### Comparing \"{0}\" and \"{1}\"\n\n".format(os.path.basename(data_file_path), os.path.basename(test_file_path))

        with gzip.open(data_file_path, 'r') as data_file:
            report += create_html_table(NUM_SAMPLE_COLUMNS, NUM_SAMPLE_ROWS, data_file_path)

            data_header = data_file.readline().decode().rstrip('\n').split('\t')

            # Make sure column headers are unique in data file
            unique_variables = []
            for variable in data_header:
                if variable not in unique_variables:
                    unique_variables.append(variable)
                else:
                    passed = False
                    printToLog('{0} is in "{1}" column header more than once\n\n'.format(variable, os.path.basename(data_file_path)), pr)
                    report += "{red_x}\t{0} is in \"{1}\" column header more than once\n\n".format(variable, os.path.basename(data_file_path), red_x=RED_X)

            if data_header[0] != "Sample":  # Make sure first column header is named "Sample"
                report += "{red_x}\tFirst column of \"{0}\" must be titled \"Sample\"\n\n".format(os.path.basename(data_file_path), red_x=RED_X)
                passed = False
            else:
                report += "{check_mark}\tFirst column of \"{0}\" is titled \"Sample\"\n\n".format(os.path.basename(data_file_path), check_mark=CHECK_MARK)

            # PARSING THROUGH DATA FILE
            samples_tested = set()
            for line in data_file:
                data_items = line.decode().rstrip('\n').split('\t')
                sample = data_items[0]
                unique_samples.add(sample)
                samples_tested.add(sample)

                if sample not in test_dict:
                    continue

                for variable in sorted(test_dict[sample]):
                    test_value = test_dict[sample][variable]

                    if variable not in data_header:
                        if test_value == "<Missing>":
                            report += "{check_mark}\tSuccess: No value for the \"{0}\" variable for sample {1} in {2}.\n\n".format(variable, sample, os.path.basename(data_file_path), check_mark=CHECK_MARK)
                        else:
                            printToLog('No value for the {0} variable was found for sample {1} in {2}'.format(variable, sample, os.path.basename(data_file_path)), pr)
                            report += "{red_x}\tNo value for the \"{0}\" variable was found for sample {1} in {2}.\n\n".format(variable, sample, os.path.basename(data_file_path), red_x=RED_X)
                            passed = False
                        continue

                    value = data_items[data_header.index(variable)]
                    if value == test_value:
                        report += "{check_mark}\tSuccess: The value ({0}) for the \"{1}\" variable in {2} matches the test value ({3}) for {4}.\n\n".format(value, variable, os.path.basename(data_file_path), test_value, sample, check_mark=CHECK_MARK)
                    else:
                        printToLog('The value ({0}) for the "{1}" variable in {2} does not match the test value ({3}) for {4}.'.format(value, variable, os.path.basename(data_file_path), test_value, sample), pr)
                        report += "{red_x}\tThe value ({0}) for the \"{1}\" variable in {2} does not match the test value ({3}) for {4}.\n\n".format(value, variable, os.path.basename(data_file_path), test_value, sample, red_x=RED_X)
                        passed = False

            samples_not_in_data = sorted(list(set(test_dict.keys()) - samples_tested))

            if len(samples_not_in_data) > 0:
                passed = False

                for error_sample in samples_not_in_data:
                    printToLog("Data for sample {0} was in {1} but not {2}.".format(error_sample, os.path.basename(test_file_path), os.path.basename(data_file_path)), pr)
                    report += "{red_x}\tData for sample {0} was in {1} but not {2}.\n\n".format(error_sample, os.path.basename(test_file_path), os.path.basename(data_file_path), red_x=RED_X)

    if passed:
        report += "#### Results: PASS\n---\n"
    else:
        report += "#### Results: FAIL\n---\n"

    return report, passed, len(unique_samples)

def create_html_table(columns, rows, file_path):
    table = '\n### First ' + str(columns) + ' columns and ' + str(rows) + ' rows of ' + file_path + ':\n\n'
    table += '<table style="width:100%; border: 1px solid black;">\n'
    with gzip.open(file_path, 'r') as inFile:
        for i in range(rows):
            table += "\t<tr align='left'>\n"
            line = inFile.readline().decode().rstrip('\n').split('\t')
            if len(line) < columns:
                columns = len(line)
            for j in range(columns):
                if i == 0:
                    table += "\t\t<th align='left'>{}</th>\n".format(line[j])
                else:
                    table += "\t\t<td align='left'>{}</td>\n".format(line[j])

            table += '\n'
            table += '\t</tr>\n'
    table += '</table>\n'
    return table
