REPORT_COLUMNS =  [
    "Section",
    "Sub-Section",
    "Given DataType",
    "Expected DataType",
    "Given Length",
    "Expected MaxLength",
    "Error Code",
    ]
INPUT_HEADERS = ["Section", "1", "2", "3"]
DELIMITER = "&"
INPUT_FILE = "input_file.txt"

#digits and word_characters regx
DIGITS_PATTERS = "[^0-9]+"
WORD_CHARACTERS_PATTERN = "[^A-Za-z ]+"

#Types
DIGITS_TYPE = "digits"
WORD_CHARACTERS_TYPE = "word_characters"
OTHERS_TYPE = "others"

#Error codes
ERROR_01 = "E01"
ERROR_02 = "E02"
ERROR_03 = "E03"
ERROR_04 = "E04"
ERROR_05 = "E05"
