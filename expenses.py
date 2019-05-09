
# This program extracts the csv lines from ExpensesOK iOS application and converts it into a Excel friendly copy
# pastable format.
# ExpensesOK does not provide support for income, so this app separates an 'income' and 'expenses' category for you.
import csv, os, re

num_users = 2 ## Number of people in your household using the expenses app.
FILE_NAME_CONTAINS = r"MoneyOK"
FILE_TYPE = r"csv"
preferred_format = [] ## ordering of final file (eg. date, in/out, category, subcategory, amount)
DESKTOP_ABS_PATH = os.sep.join((os.path.expanduser("~"), "Desktop"))

def find_csv_files():
    """This function returns a list of num_users items, all of which will contain 'MoneyOK' in their names."""
    file_list = []
    file_search_regex = re.compile(r".*" + FILE_NAME_CONTAINS.lower() + r".*\." + FILE_TYPE)
    for dir, subdirs, files in os.walk(DESKTOP_ABS_PATH):
        if dir == DESKTOP_ABS_PATH:
            for file in files:
                file = file.lower()
                if file.endswith("." + FILE_TYPE) and file_search_regex.search(file) is not None:
                    file_list.append(file)
    assert (len(file_list) == num_users), f"There are {len(file_list)} files on your desktop but expected {num_users} files. Please change the variable 'num_users' at the top of the file."
    return file_list

