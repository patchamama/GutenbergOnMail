
import gspread
from google.oauth2.service_account import Credentials
import os
import urllib.request


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('GutenbergOnMail')

def get_filter_data(data, filter=[], and_cond = True):
    """
    Filter all the data for the field condition especified in passed var filter
    """
    all_data=[]
    if len(filter)>0:
        for record in data:
            passConds = and_cond ##If True: <cond> and <cond>, if False <cond> or <cond>
            for cond in filter:
                for fieldcond, valcond in cond.items():
                    try:
                        if (isinstance(valcond,int)):
                            if and_cond:
                                passConds = (record[fieldcond] == valcond) and (passConds)
                            else: ## or
                                passConds = (record[fieldcond] == valcond) or (passConds)
                        else:  ## is string
                            if and_cond:
                                passConds = (valcond.lower() in record[fieldcond].lower()) and (passConds) 
                            else: ## or
                                passConds = (valcond.lower() in record[fieldcond].lower()) or (passConds) 
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
    """
    Return the URL of ebook to download it if a ID is given...
    """
    record = get_filter_data(data, [{"Text#": int(id)}])
    if len(record) > 0:
        ##print_data(record)
        return f"https://www.gutenberg.org/ebooks/{record[0]['Text#']}"
    else:
        return None

def download_epub(id, with_images=False, format="epub"):
    """
    Download a epub file from the Gutenberg website with one number (id) = Text#
    """
    #https://www.gutenberg.org/ebooks/62187.epub.images
    #https://www.gutenberg.org/ebooks/62187.epub3.images
    #https://www.gutenberg.org/ebooks/62187.epub.noimages
    urlimage = "images" if (with_images) else "noimages"
    url_ebook = f"https://www.gutenberg.org/ebooks/{id}.{format}.{urlimage}"
    print(url_ebook)
    try:
        web_file = urllib.request.urlopen(url_ebook).read()
        file_name = f"{id}.epub"
        epub_local=open(file_name, 'wb')
        epub_local.write(web_file)
        epub_local.close()
        return file_name
    except:
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
    download_epub(62187)

