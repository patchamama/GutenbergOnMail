
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
            if "<operator>" in record:
                and_cond = record["<operator>"]=="and"
            passConds = and_cond ##If True: <cond> and <cond>, if False <cond> or <cond>
            for cond in filter:
                for fieldcond, valcond in cond.items():
                    if (fieldcond != "<operator>"):
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
    global catalog_data
    if (len(catalog_data) == 0):
        catalog_data = get_all_records(catalog)
    cond_total = []
    and_operator = True
    while True:
        if opt=="1": #Search a book > filters
            clear_terminal()
            print('|====== MAIN > SEARCH A BOOK (FILTER) ================')
            if len(cond_total) > 0:
                print(f"| Conditions: {cond_total}")
            else:
                print("|      No conditions")
            print( '|----- One condition (simple + Conditions reset) ------')
            print( '|      1. Search in any field (author or title)')
            print( '|      2. Search a book for ID-Number')
            print( '|----- Multiple conditions (<AND> operator) -----------')
            print( '|      3. Add a author condition')
            print( '|      4. Add a title condition')
            print( '|      5. Add a language condition')
            print( '|------------------------------------------------------')
            print(f'|      6. Change operator to <{"OR" if (and_operator) else "AND"}>')
            print( '|      7. Reset conditions')
            print( '|      8. Show results')
            print( '|------------------------------------------------------')
            print( '|      9. Return to the main menu')
            print( '|------------------------------------------------------')
            opt_menu = input('| Select a option?\n')
            if opt_menu == "1": #any field
                search_cond = input("Enter the author or title to search?\n")
                if len(search_cond) > 0:
                    filtered_data = catalog_data #Reset all the conditions and use as input all the data of the catalog
                    cond_total = [{"Authors": search_cond}, {"Title": search_cond}, {"<operator>": "or"}]
                    filtered_data = get_filter_data(filtered_data, [{"Authors": search_cond}, {"Title": search_cond}], False)
                    if (len(filtered_data) == 0):
                        pause(f"No data found with title or author={search_cond}")
                    else:
                        print_data(filtered_data)
                        pause()
            elif opt_menu == "2": #Search a ID
                search_cond = input("Enter the ID to search?\n") 
                try:
                    Id = int(search_cond)
                except ValueError:
                    pause("Error: the ID is not a number, please enter a number integer to search...")
                    continue
                if len(search_cond) > 0:
                    filtered_data = catalog_data #Reset all the conditions and use as input all the data of the catalog
                    cond_total = [{"Text#": Id}, {"<operator>": 'and' if (and_operator) else 'or'}]
                    filtered_data = get_filter_data(filtered_data, [{"Text#": Id}])
                    if (len(filtered_data)==0):
                        pause(f"No data found with ID={Id}")
                    else:
                        print_data(filtered_data)
                        pause()
            elif opt_menu =="3": #Add a author condition
                pass
            elif opt_menu =="4": #Add a title condition
                pass
            elif opt_menu =="5": #Add a language condition
                pass
            elif opt_menu =="6": #Switch operator <or> / <and> 
                and_operator = not and_operator
                pause(f"Operator changed to <{'and' if (and_operator) else 'or'}>...")           
            elif opt_menu =="7": #Reset all the conditions
                filtered_data = catalog_data #Reset all the conditions and use as input all the data of the catalog
                cond_total = []
                pause("All conditions reseted...")
            elif opt_menu =="8": #Execute query with conditions
                if (len(cond_total)>0):
                    filtered_data = get_filter_data(filtered_data, cond_total)
                    if (len(filtered_data)==0):
                        pause(f"No data found with with conditions: {cond_total}")
                    else:
                        print_data(filtered_data)
                        pause()
                    pass
                else:
                    pause("First select some conditions to show some result")
            elif opt_menu =="9": #Return to the main menu
                break
        if opt=="2": #Send ebook to mail
            pass
        if opt=="3": #See Statistics of request
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

