from unittest import TestCase
import sys
import os
sys.path.insert(1, os.path.abspath(os.path.dirname(os.path.abspath(__file__))+"/.."))
from input_parser import (
	make_path, 
	make_key_index_dict,
	process_input,
	build_summary,
	write_summary,
	get_given_data_type,
	check_max_length,
	process_input_row,
)

import pandas as pd
import json

class Tests(TestCase):

	def setUp(self):
		self.base_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__))+"/..")
		self.std_defs = [
			{
				"key": "L1",
				"sub_sections": [
					{
						"key": "L11",
						"data_type": "digits",
						"max_length": 1
					},
				]
			},
			{
				"key": "L2",
				"sub_sections": [
					{
						"key": "L21",
						"data_type": "word_characters",
						"max_length": 2
					},
				]
			}
		]
		self.expected_key_index_dict = {
			"L1": {
				"key": "L1",
				"sub_sections": [
					{
						"key": "L11",
						"data_type": "digits",
						"max_length": 1
					},
				]
			},
			"L2":{
				"key": "L2",
				"sub_sections": [
					{
						"key": "L21",
						"data_type": "word_characters",
						"max_length": 2
					},
				]
			}
		}
		self.error_codes  = make_key_index_dict(json.load(open(make_path('error_codes.json'))), 'code')


	def test_make_path(self):
		self.assertEqual(
			make_path("test.json"), 
			"{}/{}".format(self.base_path, "inputs/test.json")
			)

	def test_make_key_index_dict(self):
		self.assertDictEqual(
			make_key_index_dict(self.std_defs, 'key'),
			self.expected_key_index_dict
			)

	def test_process_input_E01(self):
		report, summary = self._process_input(pd.DataFrame([["L1", 2]], columns = ["Section", "1"]))
		self.assertListEqual(report, [["L1", "L11", "digits", "digits", 1, 1, "E01"]])
		self.assertListEqual(summary, ["L11 field under segment L1 passes all the validation criteria.\n"])

	def test_process_input_E02(self):
		report, summary = self._process_input(pd.DataFrame([["L1", "A"]], columns = ["Section", "1"]))
		self.assertListEqual(report, [["L1", "L11", "word_characters", "digits", 1, 1, "E02"]])
		self.assertListEqual(summary, ['L11 field under section L1 fails the data type (expected: digits) validation, however it passes the max length (1) validation\n'])

	def test_process_input_E02_others(self):
		report, summary = self._process_input(pd.DataFrame([["L1", "-"]], columns = ["Section", "1"]))
		self.assertListEqual(report, [["L1", "L11", "others", "digits", 1 , 1, "E02"]])
		self.assertListEqual(summary, ['L11 field under section L1 fails the data type (expected: digits) validation, however it passes the max length (1) validation\n'])

	def test_process_input_E03(self):
		report, summary = self._process_input(pd.DataFrame([["L1", 12]], columns = ["Section", "1"]))
		self.assertListEqual(report, [["L1", "L11", "digits", "digits", 2, 1, "E03"]])
		self.assertListEqual(summary, ['L11 field under section L1 fails the max length (expected: 1) validation, however it passes the data type (digits) validation\n'])

	def test_process_input_E04(self):
		report, summary = self._process_input(pd.DataFrame([["L1", "aa"]], columns = ["Section", "1"]))
		self.assertListEqual(report, [["L1", "L11", "word_characters", "digits", 2, 1, "E04"]])
		self.assertListEqual(summary, ['L11 field under section L1 fails all the validation criteria.\n'])

	def test_process_input_E05(self):
		report, summary = self._process_input(pd.DataFrame([["L1", float('nan')]], columns = ["Section", "1"]))
		self.assertListEqual(report, [["L1", "L11", "", "digits", '' , 1, "E05"]])
		self.assertListEqual(summary, ['L11 field under section L1 is missing.\n'])

	def _process_input(self, input_df):
		return process_input(input_df, self.expected_key_index_dict, self.error_codes)

	def test_build_summary_E01(self):
		self.assertEqual(build_summary({"code": "E01", "message_template": "LXY is a subsection of LX."}, "L1", "L12", "", ""), "L12 is a subsection of L1.\n")

	def test_build_summary_E02(self):
		self.assertEqual(
			build_summary({"code": "E02", "message_template": "LXY is a subsection of LX and is of {data_type} data type and {max_length} character(s) long."}, "L1", "L12", "digits", 2), 
			"L12 is a subsection of L1 and is of digits data type and 2 character(s) long.\n")

	def test_write_summary(self):
		write_summary(["A", "B"])
		file = open(os.path.join(self.base_path, "parsed/summary.txt"), "r")
		self.assertEqual(file.read(), "AB")
		file.close()

	def test_get_given_data_type(self):
		self.assertEqual(get_given_data_type(1), 'digits')
		self.assertEqual(get_given_data_type("AAA "), 'word_characters')
		self.assertEqual(get_given_data_type("-AA"), 'others')
		self.assertEqual(get_given_data_type("-"), 'others')

	def test_check_max_length(self):
		self.assertTrue(check_max_length(2, "AS"))
		self.assertFalse(check_max_length(2, "S"))
		self.assertTrue(check_max_length(2, 12))

	def test_process_input_row(self):
		report = []
		messages_list = []
		sub_sections = self.expected_key_index_dict['L1']['sub_sections']
		row = (0,pd.Series(["L1", 2], index =['Sections', "1"]))
		process_input_row(row, "L1", sub_sections, report, self.error_codes, messages_list)

		self.assertListEqual(report, [["L1", "L11", 'digits', 'digits', 1,1, "E01"]])
		self.assertListEqual(messages_list,["L11 field under segment L1 passes all the validation criteria.\n"])
		self.assertEqual(len(messages_list), 1)
