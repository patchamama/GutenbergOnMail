# Gutenberg On Mail

Welcome to my third project of the [Code Institute](https://codeinstitute.net)!

I'm happy to meet my third challenge of the [Code Institute](https://codeinstitute.net) of Python Essentials. 

As a good lover of reading and books, I wanted to program something related to this. I remember the first e-ink book readers, like the first Kindles that came out at the end of 2007. This was a breakthrough to take reading to another level of socialization and platforms like [goodreads](https://www.goodreads.com/) emerged.

Even though more than a decade has passed since then. These technologies that facilitate reading and access to books are still not accessible to everyone on the planet. Although more and more people have access to smartphones with larger screens or low-cost computers such as the [One Laptop Per Child project] (https://laptop.org/) or the Raspberry Pi, internet access is still limited or slow in many areas, or restricted and censored (as happened to me for 30 years while I lived in Cuba where I only had access to email). 

This script aims to provide the first steps to facilitate the use of a tool to allow email access to e-books that do not have legal copyright issues. Therefore I have chosen the catalogs of books from [project Gutenberg] (https://www.gutenberg.org/) which is a library of over 70,000 free eBooks.

[Here is the demo version of my project, accessible from Heroku](https://gutenberg-on-mail.herokuapp.com/)
![Application example](https://github.com/patchamama/PP3-GutenbergOnMail/blob/main/doc/PP3-screenshot.png)

## The goal

The program aims to develop a tool that allows interaction from the terminal with the Project Gutenberg book catalog, making queries and allowing the selection of books that can be sent by email to a given address.

## Features


We have chosen from the book catalog the data fields that best facilitate searches by the most referenced fields: Text# (Id), Author, title, and language.

### One condition

To facilitate searches, two main options are provided (1 and 2) which allow you to search for books using the "author" or "title" as a search field, and as a second option, to choose a book if you know its "ID" (reference number in the catalog). In the example below, you would search for books with Shakespeare as title or author.

![Example of search for author or title](https://github.com/patchamama/PP3-GutenbergOnMail/blob/main/doc/example1.png)

433 books were found and as I am interested in the title "Othelo", I could have initially done the search with option 1 of "Shakespeare Othelo", but now I have the option to restart the search with the ID (option 2: 1531) or add a condition with the title field in option "4. Add a title condition". 

![Example of search for author or title](https://github.com/patchamama/PP3-GutenbergOnMail/blob/main/doc/example1.1.png)

![Example of search for Id](https://github.com/patchamama/PP3-GutenbergOnMail/blob/main/doc/example1.2.png)

The first lines show the conditions and number of books found. If only one book is selected (by adding more filter conditions or by searching by ID) it is possible to request the sending of the ebook by email (this option is not implemented at the moment) and no more conditions can be added when the minimum limit of books to be filtered is reached.

![Example of search for Id](https://github.com/patchamama/PP3-GutenbergOnMail/blob/main/doc/example1.3.png)

If one of the first two options is chosen, the previously set conditions are automatically reset (removed).

### Multiple conditions

 Several options are provided to add more conditions or filters in the searches related to the fields: title, author, and language. Several conditions can be added for each of these fields, even if a condition has already been set in option 1 above.


### Result or reset options

 Once all the filters have been completed, 4 options can be chosen. 

  - An option is provided to remove all conditions to choose a new book or to display the results of the books filtered according to the specified conditions.
  - It is possible to display the results after filtering the data according to the conditions that have been defined.
  - If there is only one book selected, you can request to send the book by email (this option is not fully implemented, as you can download the book but the possibility to send it by email is not yet available).
  - An option is also provided to display a statistic of the books chosen to be sent by email (for data protection reasons, the email is not stored). This option is always available (whether or not conditions are defined).

### Features Left to Implement

  - Integrate the application with some API (like Google API) for sending emails and thus add the possibility of sending ebooks in this way.
  - Process book requests by email (the application could access requests for book queries or specific book shipments).
  - Allow interaction with the script directly through the command line. Example: `python3 run.py [getebook Number]`. 


## Testing 

The following tests have been performed:
  - Direct input of different data in the different options (alphanumeric values, numbers, symbols).
  - The code has been tested in the Heroku app of the code institute https://pep8ci.herokuapp.com/
  

## Bugs

### Solved Bugs

At the moment of generating the queries, I used as reference a variable that contained the values of the search fields and in the case of several values, I needed to generate several variables for the different values and this did not happen because the values were always saved in the initial variable and not copied in the new variable. This was solved by making a copy of a new variable in a new memory location (without referencing the initial variable).

### Remaining Bugs

No additional errors have been detected

## Deployment

The project has been deployed using the terminal of Heroku. The Steps for deployment are:
  - Fork or clone this repository
  - Sign up in [Google Cloud Platform] (https://console.cloud.google.com/) to get the access key (credentials) to Google Spreadsheets API (https://docs.gspread.org/en/latest/oauth2.html)
  - Create a spreadsheet in Google Docs and import the CSV file from Project Gutenberg with all the catalogs that can be downloaded here: https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv
  - Click the share spreadsheet button and add the generated user in Google credentials (email account provided with parameters)
  - Log in to [Heroku](https://heroku.com)
  - Create a new app (on the dashboard > right menu "New" > Create new app > Enter the data )
  - Set the buildbacks to Python and NodeJS in this order
  - Connect the Heroku app to your repository (GitHub) (Deploy tab)
  - Deploy Branch" option > View

## Credits 

  - Code Institute for the provided study guides, examples (access to Google API), and access to the CI Python Linter (https://pep8ci.herokuapp.com/)
  - Project Gutenberg for access to the database and books: https://www.gutenberg.org
  - Clear the terminal Idea: https://stackoverflow.com/questions/2084508/clear-terminal-in-python
  - Ideas about how to validate better an email address: https://stackoverflow.com/questions/69412522/what-is-the-best-way-to-verify-an-email-address-if-it-actually-exist
