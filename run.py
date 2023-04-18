
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
print("Loading catalog data...")
catalog = SHEET.worksheet('pg_catalog')

catalog_data = [] #All data to work (of the sheet)

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
        print(f"{len(all_data)} records found...")
    else:
        all_data = data
    return all_data

def print_data(data):
    """
    Print the fields Id, Authors, Title, Language with table format to see the result tabulated in terminal
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

def download_ebook(id, with_images=False, format="epub"):
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

def get_all_records(catalog):
    """
    Return all the data of the Catalog/sheet
    """
    print("Loading all the records...")
    data = catalog.get_all_records()
    #print(f"{len(data)} records found...")
    return data

def pause(msg=""):
    """
    Show message to wait in the terminal
    """
    if len(msg)>0:
        print(msg)
    input("\nPress enter to continue...\n")

def clear_terminal():
    """
    Clear the terminal (reset)
    """
    os.system('cls' if os.name == 'nt' else 'clear') #clear the terminal 

def show_menu(opt):
    while True:
        if opt=="1": #Search a book > filters
            clear_terminal()
            print('|====== SEARCH A BOOK (FILTER) =======================')
            print('|----- One condition (simple) ------------------------')
            print('|      1. Search in any field (author or title)')
            print('|      2. Search a book for ID-Number')
            print('|----- Multiple conditions (<AND> operator) -----------')
            print('|      3. Add a author condition')
            print('|      4. Add a title condition')
            print('|      5. Add a language condition')
            print('|      6. Change operator to <OR>')
            print('|------------------------------------------------------')
            print('|      7. Return to the main menu')
            print('|------------------------------------------------------')
            opt_menu = input('| Select a option?\n')
            if opt_menu == "1": #any field

            elif opt_menu =="7": #Return to the main menu
                break
        elif opt=="2": #Search and send ebook
            break
            pass
        elif opt=="3": #Show statistics of request
            break
            pass
        else:
            pause(f'Error: Unknown option selected "{opt}"')
            break


def prompt_options():
    """
    Show in terminal commandLine options and interactive menu
    """
    while True:
        clear_terminal()
        print(''.ljust(80, '-'))
        print('| python3 run.py [filter <condition>] [getebook <ID_Number> <email@domain>] [stat_request]')
        print('|    Examples:')
        print('|      python3 run.py filter "Thomas Jefferson"')
        print('|      python3 run.py getebook 62187 me@example.com')
        print('|      python3 run.py stat_request')
        print(''.ljust(80, '-'))
        print('| Options:')
        print('|      1. Search a book (filter)')
        print('|      2. Send ebook to mail')
        print('|      3. See Statistics of request')
        option_sel = input('| Select a option (press "q" to exit)?\n')
        if option_sel.lower() =="q":
            break
        else: ##Validate the option in the func show_menu
            show_menu(option_sel)
            

def main():
    """
    Main function
    """
    prompt_options()

main()

#data = catalog.get_all_records()
#data = get_all_records(catalog)
#print(f"{len(data)} records found...")
##get_all_values()[1]



#print(data[0])
#data = get_filter_data(data, [{"Authors": "Jefferson"}, {"Authors": "Thomas"}, {"Language": "en"}, {"Type": "Text"}])
#print(len(data))
#print_data(data)

#url_ebook = get_epub_url(data, 62187)
#if url_ebook:
#    print(url_ebook)
#    ebook_local = download_ebook(62187)
#    if ebook_local:
#        #Send a email with the ebook
#        os.remove(ebook_local)
#        pass

