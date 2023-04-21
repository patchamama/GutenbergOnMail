
import gspread
from google.oauth2.service_account import Credentials
import os
import urllib.request
import re
from datetime import date


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
catalog_data = []  # All data to work (of the sheet)
catalog_index = [] # Index to access directly to every element of the catalog {id} > {Text#}

def get_filter_data(data, filter=[], and_cond=True):
    """
    Filter all the data for the field condition especified in passed var filter
    """
    all_data = []
    if len(filter) > 0:
        for record in data:
            passConds = and_cond  # If True: <cond> and <cond>, if False: or
            for cond in filter:
                if "OPERATOR" in cond:
                    and_cond = cond["OPERATOR"] == "and"
                # print(f"--- {cond} / {filter} ---")
                for fieldcond, valcond in cond.items():
                    if (fieldcond != "OPERATOR"):
                        try:
                            if (isinstance(valcond, int)):
                                if and_cond:
                                    passConds = (record[fieldcond] == valcond) and (passConds)
                                else:  # or
                                    passConds = (record[fieldcond] == valcond) or (passConds)
                            else:  # is string
                                if and_cond:
                                    passConds = (valcond.lower() in record[fieldcond].lower()) and (passConds) 
                                else:  # or
                                    passConds = (valcond.lower() in record[fieldcond].lower()) or (passConds) 
                        except:
                            pass
            if (passConds):
                all_data.append(record)
        #print(f"{len(all_data)} records found...")
    else:
        all_data = data
    return all_data

def print_data(data):
    """
    Print the fields Id, Authors, Title, Language with table format to see the result tabulated in terminal
    """
    data_lang_stat = {}

    print('\n{:5s} | {:30s} | {:30s} | {:4s}'.format('Id', "Author", "Title", "Lang"))
    print(''.ljust(80, '-'))
    
    for record in data:
        vlang = record['Language']
        data_lang_stat[vlang] = (1) if (not vlang in data_lang_stat) else (data_lang_stat[vlang]+1)
        record['Title'] = str(record['Title']).replace("\n","") # Some record['Title'] are int
        print(f"{record['Text#']:5d} | {record['Authors'][:30]:30s} | {record['Title'][:30]:30s} | {record['Language']:4s}")
    if len(data_lang_stat) > 0:
        print("Languages found:", end =" ")
        for vlang, num in data_lang_stat.items():
            print(f"{vlang} ({num})", end =" ")
        print()

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
    global catalog_index, catalog_index
    """
    Return all the data of the Catalog/sheet
    """
    print("Pre-loading all books...")
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

def valid_email(email_address):
    """ 
    Validate if the email address is valid
    """
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return (re.fullmatch(regex, email_address))

def update_request_ebook_fname(worksheet_name, ebook_id, type_request):
    """
    Update request worksheet with the ebook_id request, 
    type_request: [terminal, mail] and date or request
    """ 
    data_to_save = []
    data_to_save.append(ebook_id)
    data_to_save.append(type_request)
    data_to_save.append(str(date.today()))
    print(f"Updating {worksheet_name} in worksheet...\n")
    worksheet_to_work = SHEET.worksheet(worksheet_name)
    worksheet_to_work.append_row(data_to_save)
    print(f"{worksheet_name} worksheet updated successfully\n")

def get_info_from_data(book_id):
    """ 
    Return the datas from a book_id in the catalog data
    """
    #    vdatapos = 0
    #if (len(catalog_index)==0): # Create index of data to access directly with id > Text#
    #    for record in data:
    #        print(record)
    #        vid = int(record["Text#"])
    #        print(vid)
    #        catalog_index[vid] = vdatapos
    #        vdatapos += 1
    pass

def show_request_statistics():
    global catalog_data, catalog_index
    """
    Check requested books and show statistics of the most searched books
    """ 
    requests_worksheet = SHEET.worksheet('requests')
    requests_vals = requests_worksheet.get_all_records()
    #print(requests_vals)

    #if (len(catalog_data) == 0):
    #    catalog_data = get_all_records(catalog)

    cant_books_req = {}
    for request_data in requests_vals:
        vid = request_data["Text#"]
        cant_books_req[vid] = (1) if not vid in cant_books_req else cant_books_req[vid]+1

    for vid in cant_books_req:
        print(f"{vid} - {cant_books_req[vid]}")

    #print(f"{record['Text#']:5d} | {record['Authors'][:30]:30s} | {record['Title'][:30]:30s} | {record['Language']:4s}")

    #print(cant_books_req) 
    #vid = record["Text#"]
    #catalog_index[vid] = vdatapos

    pause()


def send_ebook_mailto(email_address, ebook_id):
    """ 
    Send the ebook to the email address specified
    """
    #ebook_fname = download_ebook(ebook_id)
    update_request_ebook_fname("requests", ebook_id, "terminal")

    #os.remove(ebook_fname)


def clean_search(search_string):
    """ 
    Remove characters/symbols for better search: ()"'#-_[]...
    """
    for a in "()\"'#-_[]$!¿?=/&+%.,;":
        search_string = search_string.replace(a, " ")
    while "  " in search_string:
        search_string = search_string.replace("  ", " ")
    return search_string.lower().strip()

def get_conditions_pretty(conditions):
    """ 
    Returns the conditions in a more readable format
    """
    # print(conditions)
    str_conditions = ""
    cant_items = 0
    for items in conditions: # List of items with conditions [({'Authors': 'shakes'}, {'Title': 'shakes'}, {'OPERATOR': 'or'})]
        cant_items += 1
        cant_cond = 0
        srt_operator = "or"
        if cant_items > 1:
            str_conditions += " and " # by default the relation between conds add are "and"
        str_conditions += "("           
        for cond in items: # Every item with one cond: ({'Authors': 'shakes'}, {'Title': 'shakes'}, {'OPERATOR': 'or'}) 
            if "OPERATOR" in cond:
                srt_operator = ("and") if cond["OPERATOR"] == "and" else "or"
            for (fname, fval) in cond.items(): 
                if (fname != "OPERATOR"):
                    cant_cond += 1
                    if (cant_cond > 1):
                        str_conditions += " "+srt_operator+" "
                    str_conditions += f'{fname}="{fval}"'
        str_conditions += ")"
    return str_conditions

def show_menu(opt):
    """
    Show submenus and/or do actions of the menus selected
    """
    global catalog_data
    cond_total = []
    filtered_data = []
    and_operator = True
    while True:
        if opt=="1": #Search a book > filters
            if (len(catalog_data) == 0):
                catalog_data = get_all_records(catalog)
                filtered_data = catalog_data
            clear_terminal()
            print('|====== MAIN > SEARCH A BOOK (FILTER) ===================')
            if len(cond_total) > 0:
                print(f"|  Conditions: { get_conditions_pretty(cond_total) }")
                if len(filtered_data) == 1:
                    print(f"| Books found: {len(filtered_data)} (Id: {filtered_data[0]['Text#']}, Author: {filtered_data[0]['Authors']}, title: {filtered_data[0]['Title']}, lang:{filtered_data[0]['Language']})")
                    # print(f"   (Id: {filtered_data[0]['Text#']}, Author: {filtered_data[0]['Authors'][:30]}, title: {filtered_data[0]['Title'][:30]}, lang:{filtered_data[0]['Language']})")
                else:
                    print(f"| Books found: {len(filtered_data)}")
            else:
                print("|      No conditions")
            print( '|----- One condition (simple + Conditions reset) --------')
            print( '|      1. Search in any field (author or title)')
            print( '|      2. Search a book for ID-Number')
            if len(filtered_data) > 1: #Only use filter if there is more than 1 record/book found or not filters
                print( '|----- Multiple conditions (<AND> operator) -------------')
                print( '|      3. Add a author condition')
                print( '|      4. Add a title condition')
                print( '|      5. Add a language condition')
            print( '|--------------------------------------------------------')
            #if len(filtered_data) > 1: #Option to new version with many levels of conditions
            #    print(f'|      6. Change operator to <{"OR" if (and_operator) else "AND"}>')
            print( '|      6. Reset conditions')
            print( '|      7. Show results')
            print( '|--------------------------------------------------------')
            print( '|      8. Return to the main menu')
            if (len(filtered_data)==1):
                print( '|      9. Send the ebook to email')
            print( '|--------------------------------------------------------')
            opt_menu = input('| Select a option (press "q" to return to the main menu)?\n')
            if opt_menu == "1": #any field
                search_cond = input("Enter the author or title to search?\n")
                search_cond = clean_search(search_cond)
                if len(search_cond) > 0:
                    filtered_data = catalog_data #Reset all the conditions and use as input all the data of the catalog
                    cond_total.clear()
                    list_words_search = search_cond.split()
                    for word in list_words_search:
                        cond_val = {"Authors": word}, {"Title": word}, {"OPERATOR": "or"}
                        cond_total.append(cond_val)
                        filtered_data = get_filter_data(filtered_data, list(cond_val))
                    if (len(filtered_data) == 0):
                        pause(f"No data found with title or author={search_cond}")
                    else:
                        print_data(filtered_data)
                        pause()
            elif opt_menu == "2": #Search a ID
                search_cond = input("Enter the ID to search?\n") 
                search_cond = clean_search(search_cond)
                try:
                    Id = int(search_cond)
                except ValueError:
                    pause("Error: the ID is not a number, please enter a number integer to search...")
                    continue
                if len(search_cond) > 0:
                    filtered_data = catalog_data #Reset all the conditions and use as input all the data of the catalog
                    cond_total.clear()
                    cond_val = {"Text#": Id}, {"OPERATOR": "or"}
                    cond_total.append(cond_val)
                    filtered_data = get_filter_data(filtered_data, list(cond_val))
                    if (len(filtered_data)==0):
                        pause(f"No data found with ID={Id}")
                    else:
                        print_data(filtered_data)
                        pause()
            elif opt_menu =="3": #Add a author condition
                search_cond = input("Enter the author to search?\n")
                search_cond = clean_search(search_cond)
                if len(search_cond) > 0:
                    list_words_search = search_cond.split()
                    for word in list_words_search:
                        cond_val = {"Authors": word}, {"OPERATOR": "or"}
                        cond_total.append(cond_val)
                        filtered_data = get_filter_data(filtered_data, list(cond_val))
                    if (len(filtered_data) == 0):
                        pause(f"No data found with conditions: {cond_total}")
                    else:
                        print_data(filtered_data)
                        pause()
            elif opt_menu =="4": #Add a title condition
                search_cond = input("Enter the title to search?\n")
                search_cond = clean_search(search_cond)
                if len(search_cond) > 0:
                    list_words_search = search_cond.split()
                    for word in list_words_search:
                        cond_val = {"Title": word}, {"OPERATOR": "or"}
                        cond_total.append(cond_val)
                        filtered_data = get_filter_data(filtered_data, list(cond_val))
                    if (len(filtered_data) == 0):
                        pause(f"No data found with conditions: {cond_total}")
                    else:
                        print_data(filtered_data)
                        pause()
            elif opt_menu =="5": #Add a language condition
                search_cond = input("Enter the language to filter (en/es/fr/it)?\n")
                search_cond = clean_search(search_cond)
                if len(search_cond) > 0:
                    if " " in search_cond:
                        pause("Error: please type only one word. Example: en (to english)")
                        continue
                    cond_val = {"Language": search_cond}, {"OPERATOR": "or"}
                    cond_total.append(cond_val)
                    filtered_data = get_filter_data(filtered_data, list(cond_val))
                    if (len(filtered_data) == 0):
                        pause(f"No data found with conditions: {search_cond}")
                    else:
                        print_data(filtered_data)
                        pause()
            #elif opt_menu =="6": #Switch operator <or> / <and> 
            #    and_operator = not and_operator
            #    pause(f"Operator changed to <{'and' if (and_operator) else 'or'}>...")           
            elif opt_menu =="6": #Reset all the conditions
                filtered_data = catalog_data #Reset all the conditions and use as input all the data of the catalog
                cond_total = []
                pause("All conditions reseted...")
            elif opt_menu =="7": #Show results > filtered_data
                if (len(cond_total)>0):
                    print_data(filtered_data)
                    pause()
                else:
                    pause("First select some conditions to show some result")
            elif opt_menu =="8" or opt_menu =="q": #Return to the main menu
                break
            elif (len(filtered_data)==1) and (opt_menu =="9"): # Send a ebook if there is 1 book selected
                opt="2"
            else:
                if opt_menu != "":
                    pause(f'Error: Unknown option selected "{opt_menu}"')
        elif opt=="2": #Send ebook to mail
            if (len(filtered_data)==1):
                email_to = input("Enter the email address of the destiny?\n")
                email_to = email_to.strip()
                if valid_email(email_to):
                    send_ebook_mailto(email_to, filtered_data[0]["Text#"])
                else:
                    pause(f"Error: Invalid email address: {email_to}")
            else:
                pause("Please select some conditions and one book to send it (mail)")
                break
            opt="1" #Show the submenu 1 again
        elif opt=="3": #See Statistics of request
            show_request_statistics()
            break
        else:
            if opt != "":
                pause(f'Error: Unknown option selected on main menu: "{opt}"')
            break
        opt_menu=1 #Show the submenu 1 again
        
        


def prompt_options():
    """
    Show in terminal commandLine options and interactive menu
    """
    while True:
        clear_terminal()
        print('Vers. 0.16')
        print('|====== MAIN '+''.ljust(67, '='))
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
        option_sel = option_sel.strip()
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

