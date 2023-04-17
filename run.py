# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('GutenbergOnMail')

def get_filter_data(data, filter=[]):
    """
    Filter all the data for the field condition especified in passed var filter
    """
    all_data=[]
    if len(filter)>0:
        for record in data:
            passConds = True
            for cond in filter:
                for fieldcond, valcond in cond.items():
                    try:
                        if (isinstance(valcond,int)):
                            passConds = (record[fieldcond] == valcond) and (passConds)
                        else:  ## is string
                            passConds = (valcond.lower() in record[fieldcond].lower()) and (passConds) 
                    except:
                        pass
            if (passConds):
                all_data.append(record)
    else:
        all_data = data
    return all_data

def print_data(data):
    """
    Print the fields Id, Authors, Title, Language with table format to see tabulated in terminal
    """
    print('\n{:5s} | {:30s} | {:30s} | {:4s}'.format('Id', "Author", "Title", "Lang"))
    print(''.ljust(80, '-'))
    
    for record in data:
        record['Title'] = record['Title'].replace("\n","")
        print(f"{record['Text#']:5d} | {record['Authors'][:30]:30s} | {record['Title'][:30]:30s} | {record['Language']:4s}")

def get_epub_url(data, id):
    record = get_filter_data(data, [{"Text#": int(id)}])
    if len(record) > 0:
        ##print_data(record)
        return "https://www.gutenberg.org/ebooks/"+str(record[0]["Text#"])
    else:
        return None


catalog = SHEET.worksheet('pg_catalog')
data = catalog.get_all_records()
##get_all_values()[1]
print(len(data))
print(data[0])
data = get_filter_data(data, [{"Authors": "Jefferson"}, {"Authors": "Thomas"}, {"Language": "en"}, {"Type": "Text"}])
print(len(data))
print_data(data)

url_ebook = get_epub_url(data, 62187)
if url_ebook:
    print(url_ebook)
