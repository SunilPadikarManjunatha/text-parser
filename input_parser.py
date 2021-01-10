import json
import os
import pandas as pd
import re
from const import *
import logging

logging.basicConfig(
    filename='input_parser.log',
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    )
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def make_path(file_name):
    return os.path.join(BASE_PATH, "inputs", file_name)

def make_key_index_dict(standard_definitions, key):
    keys_dict = {}
    for index, item in enumerate(standard_definitions):
        keys_dict[item[key]] = item
    
    return keys_dict

def process_input(df, std_def_key_index, error_codes):
    logging.info("Started processing input data")
    report_list = []
    messages_list = []
    for row in df.iterrows():
        section = row[1]["Section"]
        sub_sections = std_def_key_index[section]['sub_sections']
        process_subsections(row, section, sub_sections, report_list, error_codes, messages_list)
    return (report_list, messages_list)

def write_csv(report_list):
    report_df = pd.DataFrame(report_list, columns = REPORT_COLUMNS)
    logging.info("Writing report to csv file.")
    report_df.to_csv(os.path.join(BASE_PATH, 'parsed/report.csv'), index=False)

def process_subsections(row, section, sub_sections, report, error_codes, messages_list):
    logging.info("Started processing subsections for %s", section)
    for subs in sub_sections:
            col = []
            sub_section = subs['key']
            data_type = subs['data_type']
            max_length = subs['max_length']

            column = sub_section.replace(section, "")
            value = row[1][column]
            error_code = ERROR_05
            expected_dt = ""
            is_length_matched = False
            expected_len = ""

            if value == value:
                expected_dt = get_expected_data_type(value)
                logging.info("Validating field %s=>%s", section, sub_section)
                expected_len = len(str(value))
                is_length_matched = is_expected_max_length(max_length, value)
                error_code = get_error_code(expected_dt, data_type, is_length_matched)
            else:
                logging.warning("Invalid field %s=>%s", section, sub_section)

            col = col + [
                section,
                sub_section,
                expected_dt,
                data_type,
                expected_len,
                max_length,
                error_code,
            ]
            messages_list.append(build_summary(error_codes[error_code], section, sub_section,data_type, max_length ))
            report.append(col)

def build_summary(error_code, section, sub_section , data_type, max_length):
    logging.info("Building summary for %s=>%s and error code %s", section, sub_section, error_code['code'])
    message = error_code['message_template']
    if error_code['code'] in [ERROR_02, ERROR_03]:
        message = message.format(data_type=data_type, max_length=max_length)
    message = message.replace("LXY", sub_section)
    message = message.replace("LX", section)
    return message + "\n"

def write_summary(messages):
    file = open(os.path.join(BASE_PATH, "parsed/summary.txt"), "w+")
    file.writelines(messages)
    file.close()

def get_expected_data_type(value):
    expected_dt = ""

    if not re.search(DIGITS_PATTERS, str(value)):
        expected_dt = DIGITS_TYPE
        value = int(value)
    elif not re.search(WORD_CHARACTERS_PATTERN, str(value)):
        expected_dt = WORD_CHARACTERS_TYPE
    else:
        expected_dt = OTHERS_TYPE

    return expected_dt

def is_expected_max_length(max_length, value):
    if max_length == len(str(value)):
        return True

    return False

def get_error_code(expected_dt, data_type, expected_len):
    error_code = ""
    if expected_dt == data_type and expected_len:
        error_code = ERROR_01
    elif expected_dt != data_type and expected_len:
        error_code = ERROR_02
    elif expected_dt == data_type and not expected_len:
        error_code = ERROR_03
    else:
        error_code = ERROR_04

    return error_code

def main():
    logging.info("Started!!!")
    
    std_def_key_index = make_key_index_dict(json.load(open(make_path('standard_definition.json'))), 'key')
    logging.info("Read standard_definition.json")
    error_codes = make_key_index_dict(json.load(open(make_path('error_codes.json'))), 'code')
    logging.info("Read error_codes.json")
    input_df = pd.read_csv(make_path(INPUT_FILE), delimiter=DELIMITER, names=INPUT_HEADERS)
    logging.info("Parsed input_file.txt")
    report_list, message_list  = process_input(input_df, std_def_key_index, error_codes)
    write_csv(report_list)
    write_summary(message_list)
    logging.info("Finished!!!")

if __name__ == "__main__":
    main()
