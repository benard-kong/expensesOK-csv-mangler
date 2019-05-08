
# This program extracts the csv lines from ExpensesOK iOS application and converts it into a Excel friendly copy
# pastable format.
# ExpensesOK does not provide support for income, so this app separates an 'income' and 'expenses' category for you.
import os

num_users = 2 ## Number of people in your household using the expenses app.
preferred_format = []
desktop = os.sep.join((os.path.expanduser("~"), "Desktop"))

