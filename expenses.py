
# This program extracts the csv lines from ExpensesOK iOS application and converts it into a Excel friendly copy
# pastable format.
# ExpensesOK does not provide support for income, so this app separates an 'income' and 'expenses' category for you.
import csv, os, re, datetime

#### EDIT VARIABLES BELOW AND PROGRAM SHOULD WORK ACCORDINGLY ####
NUM_USERS = 2 ## Number of people in your household using the expenses app.
FILE_NAME_CONTAINS = r"MoneyOK"
FILE_TYPE = r"csv"
DESKTOP_ABS_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

LABEL_DATE = "Date"
LABEL_AMOUNT = "Amount"
LABEL_CATEGORY = "Category"
LABEL_CATEGORY_GROUP = "Category group"
LABEL_NOTE = "Note"
PREFERRED_FORMAT = (
    LABEL_DATE,
    LABEL_CATEGORY_GROUP,
    LABEL_CATEGORY,
    LABEL_AMOUNT,
    LABEL_NOTE,
) # ordering of columns in final file (eg. date, in/out, category, subcategory, amount)

AMOUNT_COL_TITLE = "Amount"
CURRENCY = "KRW"
CURRENCIES_WITH_NO_DECIMAL = ["krw", "jpy"] ## Can add to this list accordingly. So far it has:
# krw: Korean Won
# jpy: Japanese Yen

DATE_TIME_FORMAT_ORIG = "%Y.%m.%d" ## Format of the date string to change into date object
DELIMITER = "\t" ## Separate columns with tabs
SALARY_STRING_NAME = "급여" ## What did you write to mean "Salary" in Categories section?
USER_INPUT_YEAR_MONTH_FORMAT = "YYYY-MM" ## format of yr & month user should type
USER_INPUT_YEAR_MONTH_FORMAT_DATETIME_OBJ = "%Y-%m" ## When changing user's input into datetime.date obj
                                                    # '-' to '.' etc. if prefer the user to type another format
USER_INPUT_YEAR_MONTH_FORMAT_REGEX = r"\d\d\d\d-\d\d" ## regex for the format the user must type the YYYY-MM; can change the

OUTPUT_FILENAME = "output_expenses.txt"

UNWANTED_UNICODE_CHARS = (b'\xef', b'\xbb', b'\xbf', b'\ufeff') ## misc unwanted chars in utf-16 encoding

#### EDIT VARIABLES ABOVE AND PROGRAM SHOULD WORK ACCORDINGLY ####

def ask_user_for_choice_until_proper_input(input_text, choices):
    """Asks user for a choice until they input something in choices.
    Returns the user's choice"""
    choice = ""
    while choice.lower() not in choices or choice == "":
        choice = input(input_text)
        if choice.lower() == choices:
            choice = ""
    return choice

def find_csv_files():
    """Returns a list of csv files with their absolute file paths.
    len(file_list) == NUM_USERS"""
    global NUM_USERS
    file_list = []
    file_search_regex = re.compile(r".*" + FILE_NAME_CONTAINS.lower() + r".*\." + FILE_TYPE.lower())
    for dir, subdirs, files in os.walk(DESKTOP_ABS_PATH):
        if dir == DESKTOP_ABS_PATH:
            for file in files:
                file = file.lower()
                if file.endswith("." + FILE_TYPE) and file_search_regex.search(file) is not None:
                    file_path = os.path.join(DESKTOP_ABS_PATH, file)
                    file_list.append(file_path)
    if len(file_list) != NUM_USERS:
        choices = "yn"
        input_text = f"Expected {NUM_USERS} .{FILE_TYPE} files on the Desktop, but there were {len(file_list)} files.\
        Would you like to run the program for all {len(file_list)} files? (y/n)\n"
        choice = ask_user_for_choice_until_proper_input(input_text, choices)
        if choice.lower() == "y":
            NUM_USERS = len(file_list)
            file_list = find_csv_files()
    # todo: the assert below prints out the message with literal space characters if split into multiple lines? Check why
    assert (len(file_list) == NUM_USERS), f"There are {len(file_list)} files on your desktop but expected {NUM_USERS} files. Please change the variable 'NUM_USERS' at the top of the file."
    return file_list

def create_rows_list(csv_reader):
    """Returns a 2D list with the very first row containing the name of the columns, and the subsequent rows
    representing the values for each column.
    csv_reader: a csv file reader using csv module"""
    rows_list = []
    for row in csv_reader:
        rows_list.append(row)
    return rows_list

def remove_extraneous_chars_and_convert_byte_to_string(byte_string, encoding):
    """Removes unwanted chars and returns string form of original byte_string"""
    for unwanted_char in UNWANTED_UNICODE_CHARS:
        if unwanted_char in byte_string:
            byte_string = byte_string.replace(unwanted_char, b"")
    return byte_string.decode(encoding)

def create_list_of_data(rows_list):
    """This function returns a list of dicts which define the values of each row in the original csv file.
    rows_list: a 2D list with the very first row containing the keys for the dicts
    corresponding columns underneath the first row are the values for the dicts
    Returns list in following format:
    [{"Date": "2019-05-09", "Amount": 5000, ...},{"Date": "2019-05-08", "Amount": 9000, ...}, etc]"""
    list_data = []
    first_row = 0
    num_rows = len(rows_list)
    num_cols = len(rows_list[first_row])
    for row in range(first_row + 1, num_rows):
        dict_data = {}
        for col in range(num_cols):
            col_title = rows_list[first_row][col]
            col_title = remove_extraneous_chars_and_convert_byte_to_string(col_title.encode(), "utf-8")
            cur_item = rows_list[row][col]
            cur_item = remove_extraneous_chars_and_convert_byte_to_string(cur_item.encode(), "utf-8")

            if col_title in PREFERRED_FORMAT:
                dict_data[col_title] = cur_item
        list_data.append(dict_data)
    return list_data

def list_data_strings_to_python_objects(list_data):
    """Void function; changes list_data but with Python objects rather than all strings
    eg. if key == 'Date', changes value to datetime object
    if key == 'Amount', changes value to positive integer (if KRW)
    """
    for dic_data in list_data:
        for title in PREFERRED_FORMAT:
            if dic_data[title] == "":
                dic_data[title] = None
            else:
                if title.lower() == "date":
                    dic_data[title] = datetime.datetime.strptime(dic_data[title], DATE_TIME_FORMAT_ORIG).date()
                elif title.lower() == "amount":
                    dic_data[title] = abs(float(dic_data[title]))
                    if CURRENCY.lower() in CURRENCIES_WITH_NO_DECIMAL:
                        dic_data[title] = int(dic_data[title])

def find_next_month(date_obj):
    """Finds and returns the first day of the month after date_obj's month.
    date_obj: a datetime.date object with day=1"""
    import datetime
    next_month = date_obj + datetime.timedelta(days=32)
    yr = next_month.year
    m = next_month.month
    day = 1
    next_month = datetime.date(yr, m, day)
    return next_month

def extract_month(list_data, month):
    """returns list_data with only the month the user wanted
    month: string in the form YYYY-MM (stored in var USER_INPUT_YEAR_MONTH_FORMAT)"""
    regex_obj = re.compile(USER_INPUT_YEAR_MONTH_FORMAT_REGEX)
    assert regex_obj.search(month) != None, "The month format is incorrect, it should be in the following format: " + USER_INPUT_YEAR_MONTH_FORMAT

    target_month_object = datetime.datetime.strptime(month, USER_INPUT_YEAR_MONTH_FORMAT_DATETIME_OBJ).date()
    month_after_object = find_next_month(target_month_object)
    new_list_data = []
    for row in list_data:
        if target_month_object <= row["Date"] < month_after_object:
            new_list_data.append(row)
    return new_list_data

def swap_values_in_tuple(tuple_, index1, index2):
    """Returns the same tuple with the two items in index1 & index2 swapped"""
    list_ = list(tuple_)
    temp_item = list_[index1]
    list_[index1] = list_[index2]
    list_[index2] = temp_item
    return tuple(list_)

def convert_to_tuples_list_data(list_data):
    """Convert dictionary form list_data to tuples list data for easy csv writing.
    Returns that new list_data object.
    Items in tuples will be strings.
    eg. [("2019-05-10", "-5000", "Expense", "", ""), ("2019-05-31, "2983829", "Salary", "", ""), ...]"""
    new_list_data = []
    for dict_row in list_data:
        preferred_order = PREFERRED_FORMAT
        working_tuple = []
        is_salary = False
        if dict_row["Category"] == SALARY_STRING_NAME: is_salary = True
        ## invert LABEL_CATEGORY && LABEL_CATEGORY_GROUP's order if LABEL_CATEGORY_GROUP is empty
        ## required because of how the app labels inverts categories/subcategories
        invert_categories = False
        if dict_row[LABEL_CATEGORY_GROUP] is None: invert_categories = True
        if invert_categories:
            assert LABEL_CATEGORY in preferred_order, f"{LABEL_CATEGORY} is not in the following list: {preferred_order}"
            assert LABEL_CATEGORY_GROUP in preferred_order, f"{LABEL_CATEGORY_GROUP} is not in the following list: {preferred_order}"
            categories_index = preferred_order.index(LABEL_CATEGORY)
            categories_group_index = preferred_order.index(LABEL_CATEGORY_GROUP)
            preferred_order = swap_values_in_tuple(preferred_order, categories_index, categories_group_index)

        for col_title in preferred_order:
            val = dict_row[col_title]
            if val == None:
                val = ""
            elif col_title.lower() == "amount":
                if not is_salary:
                    val = -val
            val = str(val)
            val = val.replace(u"\xa0", u" ") ## replace No-Break Space with regular space
            working_tuple.append(val)
        working_tuple = tuple(working_tuple)
        new_list_data.append(working_tuple)
    return new_list_data

def find_new_line_escape_sequence():
    """Returns escape sequence for new line depending on platform.
    Windows == '\r\n'; Unix == '\n'
    """
    import platform
    is_windows = False
    if "windows" in platform.system().lower():
        is_windows = True
    new_line = "\n"
    if is_windows:
        new_line = "\r\n"
    return new_line

def output_list_data_to_txt(list_data, delim, append_to_file=False, enc="utf-8"):
    """void function; takes the data from list_data and outputs it into a txt file
    rows are each list item
    columns are each key; separated by delim
    list_data: list of tuples, each tuple contains the values to be written
    delim: the deliminator that separates each column (eg. "\t" or "," etc.
    append_to_file: whether to open file in write or append mode"""
    write_mode = "w"
    if append_to_file: write_mode = "a"
    # new_line = find_new_line_escape_sequence() # not necessary?

    file_path = os.path.join(DESKTOP_ABS_PATH, OUTPUT_FILENAME)
    working_file = open(file_path, write_mode, encoding=enc, newline="")
    # working_file_writer = csv.writer(working_file, delimiter=delim, lineterminator=new_line) # lineterminator not necessary?
    working_file_writer = csv.writer(working_file, delimiter=delim)
    for line in list_data:
        working_file_writer.writerow(line)
    working_file.close()

def truncate_last_line(file_path):
    """void function; removes the last new line in file_path for easy copy paste to Excel and
    no new rows are created in Excel Table"""
    with open(file_path, 'rb+') as filehandle: # source: https://stackoverflow.com/a/18857381
        filehandle.seek(-1, os.SEEK_END) # puts cursor at file[-1] position?
        assert filehandle.read() == b"\n", "The last line is not a '\\n' character, cannot truncate"
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate() # 'shortens' file up to cursor's position?

def main():
    wanted_month = input("Input the year and month in the format YYYY-MM: ")
    files_list = find_csv_files()
    append_to_file = False
    for file in files_list:
        try:
            with open(file, "r", encoding="utf-8") as test_read_file:
                test_read_file.read()
            # successfully read in utf-8 encoding, continue to open file as normal
            orig_file = open(file, "r", encoding="utf-8")
            # print("opening unix file")
        except UnicodeDecodeError:
            orig_file = open(file, "r", encoding="utf-16") ## if exported as 'windows' file in the app
            # print("opening windows file")
        orig_file_reader = csv.reader(orig_file, delimiter=DELIMITER) # delimiter should be "," but only works with "\t"?

        rows_list = create_rows_list(orig_file_reader)
        list_data = create_list_of_data(rows_list)
        list_data_strings_to_python_objects(list_data)
        list_data = extract_month(list_data, wanted_month)
        list_data = convert_to_tuples_list_data(list_data)
        output_list_data_to_txt(list_data, DELIMITER, append_to_file=append_to_file)
        append_to_file = True
    truncate_last_line(os.path.join(DESKTOP_ABS_PATH, OUTPUT_FILENAME)) # Removes last '\n' char
    print(f"Finished! Check your Desktop to find the file '{OUTPUT_FILENAME}'")


if __name__ == "__main__":
    main()
