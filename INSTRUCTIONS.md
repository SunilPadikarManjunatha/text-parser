
## Task Objective:

Parse the input file (`input_file.txt`), using the provided standard definition  (`standard_definition.json`) and generate a summary report.

## Tech Stack:

Language: Prefrred language is `Python` but you are open to use whatever language you're comfortable with 

You don't need anything else, but feel free to go fancy if you feel there's a need. 

## Instructions: 

### You are expected to 

1. Create a git repo and push this code along with your finished work. Please share the link of the repo with us. 
2. Use the standard definition provided (`standard_definition.json`)
3. Parse the input file (`input_file.txt`) that contains multiple sections which are separated by new line (`\n`) character, and the sections are sub-separated by ampersand character (`&`)
4. Refer to `error_codes.json` for appropriate finding the appropriate error codes. 
5. After parsing the file create a csv file (`parsed/report.csv`). Refer `sample/report.csv` (`report.csv` file in sample folder) for the list of columns and the expected output given the following input:

	```
	L1&99&&A
	L4&9
	```

6. Create a txt file (`parsed/summary.txt`) containing a summary of the report in plain english. Refer to `sample/summary.txt` (`summary.txt` in sample folder) for the expected output given the following input: 

	```
	L1&99&&A
	L4&9
	```

7. Write unit tests for your code 
8. Provide a readme with instructions to run your code 

### Brownie points for:
1. Logging 
2. Functionalize your code. One function does only one thing. 
3. Comments 
4. Naming conventions, file names and project structure
5. Clarity and ease of understanding the code

## Notes: 

1. Parse the input file based on the given definitions in the same order as they appear.  
2. Following the order of the definitions, the missing field will always be the later once. 
3. digits are only numbers between `0-9` and word characters are english letters between `A-Z` (both lower and uppercase) including space.
4. Empty spaces count towards the length of the field, e.g. length of `A A` is 3. 
5. The sample uses the same standard_definition.json provided along with this task.
6. Use `others` as the datatype for datatypes other than `digits` and `word_characters`. 
