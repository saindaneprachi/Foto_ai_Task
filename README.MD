Project Title: Library Managemt System

Description: This project is django based application where DRF is used. It
 manages user, books creation as well borrow requests, their approval from
librarian, downloading user borrow history in csv format. It includes JWT based authentication

To run project:

1. Clone project
2. Create and activate virtual environment 
3. Install requirments from requirments.txt file
4. Makemigrations and Migrate
5. Create super user and make is_librarian field True using admin panel(Note: createsuper after applying migrations beacause i have used here 
AbstractUser, it doesn't reqiured, i can use here traditional way too)
6. Using postman hit endpoints first take tokens and then proceed.