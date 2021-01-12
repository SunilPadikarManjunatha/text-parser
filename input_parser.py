"""Input parser and it's utility methods."""
import json
import logging
import os
import re

import pandas as pd
from const import *

logging.basicConfig(
	filename='input_parser.log',
	level=logging.DEBUG,
	format=
	'%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S',
)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def make_path(file_name):
	"""Return a path to a specified file."""
	return os.path.join(BASE_PATH, 'inputs', file_name)

def make_key_index_dict(standard_definitions, key):
	"""Return a dictionary by converting an array of dictionaries to key:item
	pair."""
	keys_dict = {}
	for item in standard_definitions:
		keys_dict[item[key]] = item

	return keys_dict


def process_input(df, std_def_key_index, error_codes):
	"""
	Return report and summary lists.

	Iterate each row in input dataframe and validate each field
	according to standard_definition.json.
	"""
	logging.info('Started processing input data')
	report_list = []
	summary_list = []
	for row in df.iterrows():
		section = row[1]['Section']
		if section in std_def_key_index:
			sub_sections = std_def_key_index[section]['sub_sections']
			process_input_row(
				row, section, sub_sections, report_list, error_codes, summary_list
			)
	return (report_list, summary_list)


def write_csv(report_list):
	"""Write 2D array of data to report.csv file."""
	report_df = pd.DataFrame(report_list, columns=REPORT_COLUMNS)
	logging.info('Writing report to csv file.')
	report_df.to_csv(os.path.join(BASE_PATH, 'parsed/report.csv'), index=False)


def process_input_row(
	row, section, sub_sections, report, error_codes, summary_list
):
	"""Iterate each subsection and validate each field in a input row according
	to standard_definition.json and create summary_list accorging to
	error_code."""
	logging.info('Started processing subsections for %s', section)
	for subs in sub_sections:
		col = []
		sub_section = subs['key']
		data_type = subs['data_type']
		max_length = subs['max_length']

		column = sub_section.replace(section, '')
		value = row[1][column]
		error_code = ERROR_05
		given_dt = ''
		is_length_matched = False
		given_len = ''

		if value is not None and value == value:
			given_dt = get_given_data_type(value)
			logging.info('Validating field %s=>%s', section, sub_section)
			given_len = len(str(value))
			is_length_matched = check_max_length(max_length, value)
			error_code = get_error_code(
				given_dt, data_type, is_length_matched
			)
		else:
			logging.warning('Invalid field %s=>%s', section, sub_section)

		col = col + [
			section,
			sub_section,
			given_dt,
			data_type,
			given_len,
			max_length,
			error_code,
		]
		summary_list.append(
			build_summary(
				error_codes[error_code], section, sub_section, data_type,
				max_length
			)
		)
		report.append(col)


def build_summary(error_code, section, sub_section, data_type, max_length):
	"""Return summary text by populating message_template with appropriate
	values."""
	logging.info(
		'Building summary for %s=>%s and error code %s', section, sub_section,
		error_code['code']
	)
	message = error_code['message_template']
	if error_code['code'] in [ERROR_02, ERROR_03]:
		message = message.format(data_type=data_type, max_length=max_length)
	message = message.replace('LXY', sub_section)
	message = message.replace('LX', section)
	return message + '\n'


def write_summary(summary_list):
	"""Write summary data to summary.txt file."""
	file = open(os.path.join(BASE_PATH, 'parsed/summary.txt'), 'w+')
	file.writelines(summary_list)
	file.close()

def get_given_data_type(value):
	"""Return given data-type of a field."""
	try:
		value = int(value)
		return DIGITS_TYPE
	except:
		pass

	if value and all(x.isalpha() or x.isspace() for x in value):
		return WORD_CHARACTERS_TYPE
	
	return OTHERS_TYPE

def check_max_length(max_length, value):
	"""Return True if expected length of a field is equal to actual length of
	the filed."""
	if len(str(value)) <= max_length:
		return True

	return False


def get_error_code(given_dt, data_type, given_len):
	"""Return error code for a field."""
	error_code = ''
	if given_dt == data_type and given_len:
		error_code = ERROR_01
	elif given_dt != data_type and given_len:
		error_code = ERROR_02
	elif given_dt == data_type and not given_len:
		error_code = ERROR_03
	else:
		error_code = ERROR_04

	return error_code

def build_input_and_column_names(input_file):
	"""
		Return 2D array of input fields and column headers
	"""
	count = 0
	input_list = []
	with open(input_file, 'r') as f:
		lines = f.readlines()

		for l in lines:
			columns = l.replace('\n', '').split(DELIMITER)
			input_list.append(columns)
			column_count = len(columns)
			count = column_count if count < column_count else count

	f.close()

	column_names = [str(i) for i in range(1, count)]
	return (input_list, column_names)

def main():
	logging.info('Started!!!')

	std_def_key_index = make_key_index_dict(
		json.load(open(make_path('standard_definition.json'))), 'key'
	)
	logging.info('Read standard_definition.json')
	error_codes = make_key_index_dict(
		json.load(open(make_path('error_codes.json'))), 'code'
	)
	logging.info('Read error_codes.json')
	input_list, column_names = build_input_and_column_names(make_path(INPUT_FILE))
	input_df = pd.DataFrame(input_list, columns= INPUT_DEFAULT_HEADER + column_names)
	logging.info('Parsed input_file.txt')
	report_list, message_list = process_input(
		input_df, std_def_key_index, error_codes
	)
	write_csv(report_list)
	write_summary(message_list)
	logging.info('Finished!!!')


if __name__ == '__main__':
	print("Started!")
	main()
	print("Finished!")