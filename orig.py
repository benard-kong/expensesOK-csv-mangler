#!/usr/bin/env python3

import csv, os, re

# os.chdir(r"C:\Users\Darren\Desktop")
# Get the user's desktop.
desktop = os.path.expanduser("~") + r"\Desktop"
os.chdir(desktop)

# Regex for matching the file name
#fileSearchRegex = re.compile(".*moneybook.*\\.csv")
fileSearchRegex = re.compile(".*MoneyOK.*\\.csv")

# This function returns a list of 2 items, an SP moneybook & BK moneybook.
def find_csv_files():
    fileList = []
    for subdir, dirs, files in os.walk("."):
        if subdir == ".":
            for file in files:
                if file.endswith(".csv") and fileSearchRegex.search(file) is not None:
                    fileList.append(file)
    #print(fileList)
    if len(fileList) is not 2: # If there isn't exactly two files, return None
        return
    return fileList

def format_expenses():
    current_month = input("Input the year and month in the format YYYY-MM: ")
    fileList = find_csv_files()
    if fileList is None:
        print("You should only have two expenses files originally. Something is wrong")
        return
    for fileIndex in range(len(fileList)): # Did range in order to decide when to write and when to append.
        if fileIndex == 0: write_or_append = "w"
        else: write_or_append = "a"
        origFile = open(fileList[fileIndex], "r", encoding="utf-8")
        origFileReader = csv.reader(origFile, delimiter = "\t")

        outputFile = open("expensesOutput.csv", write_or_append, encoding="utf-8", newline="")
        outputFileWriter = csv.writer(outputFile, delimiter="\t", lineterminator="\n")
        DATE = 0
        AMOUNT = 1
        CATEGORY = 4
        CATEGORY_GROUP = 5
        COMMENT = 6
        for row in origFileReader:
            if row[DATE] == "Date":
                continue
            newRow = []
            category_is_main_cat = False
            is_salary = False
            row[DATE] = row[DATE].replace(".", "-")
            if row[DATE].startswith(current_month) == False: # skips if it's not the current month
                continue
            newRow.append(row[DATE])
            if row[CATEGORY_GROUP] == "":
                category_is_main_cat = True
            if row[CATEGORY] == "급여":
                is_salary = True
            if is_salary == True:
                newRow.append("수입")
            else:
                newRow.append("지출")
            if category_is_main_cat == True: # input CATEGORY first if there's no sub-category
                newRow.append(row[CATEGORY])
                newRow.append(row[CATEGORY_GROUP])
            else: # input CATEGORY_GROUP first if there is a sub-category
                newRow.append(row[CATEGORY_GROUP])
                newRow.append(row[CATEGORY])
            newRow.append(row[COMMENT])
            newRow.append(str(abs(int(row[AMOUNT]))))
            category_is_main_cat = False
            is_salary = False
            outputFileWriter.writerow(newRow)
        origFile.close()
        outputFile.close()

format_expenses()

##def format_expenses():
##    fileList = find_csv_files()
##    if fileList is None:
##        print("You should only have two expenses files originally. Something is wrong")
##        return
##    for fileIndex in range(len(fileList)): # Did range in order to decide when to write and when to append.
##        if fileIndex == 0: write_or_append = "w"
##        else: write_or_append = "a"
##        origFile = open(fileList[fileIndex], "r", encoding="utf-8")
##        origFileReader = csv.reader(origFile)
##
##        outputFile = open("expensesOutput.csv", write_or_append, encoding="utf-8", newline="")
##        outputFileWriter = csv.writer(outputFile, delimiter="\t", lineterminator="\n")
##
##        for row in origFileReader:
##            newRow = []
##            for indexNum in range(len(row)):
##                row[indexNum] = row[indexNum].strip(" ")
##                if indexNum == 0:
##                    row[indexNum] = row[indexNum].replace(".", "-")
##                    if row[indexNum].startswith(u"\ufeff"): # This is for deleting the character at the front of each csv file. Otherwise it'll screw up your excel.
##                        row[indexNum] = row[indexNum].strip(u"\ufeff")
##                        #row[indexNum] = row[indexNum][1:]
##                        # Either one of the codes above will work. Take your pick.
##                elif indexNum == 3:
##                    splitDashesList = row[indexNum].split("-")
##                    newRow += splitDashesList
##                    continue
##                newRow.append(row[indexNum])
##            outputFileWriter.writerow(newRow)
##
##        origFile.close()
##        outputFile.close()

#format_expenses()


###The following test code is to see if I was able to delete the "\ufeff" char correctly.
##exp = open("expensesOutput.csv", "r", encoding="utf-8")
##expR = csv.reader(exp)
##for row in expR:
##    print(row)
