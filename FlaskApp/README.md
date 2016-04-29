# udacity-ND-P3

Welcome to my supermarket app. This app contains various grocery items which are grouped into different categories. As as logged in user you can read, create, update and delete items or even entire categories. As a non-logged in user you can only read items and categories. 


How to use this app:

1) Download the Github repository udacity-ND-P3 to your local machine

2) Within the Github respository you will find the file catalog_database_setup.py. In your console enter the command: python catalog_datbase_setup.py. This will create the empty database.

3) Within the Github respository you will find the file lotsofcategories.py. SPECIAL NOTE: please modify the user1 variable on line 22 to include your own Google credentials if you want to be able to edit/delete categories and grocery items in the app before create your own. In your console enter the command: python lotsofcategories.py. This will create entries for all the empty database tables.

4) Within the Github respository you will find the main file application.py. In your console enter the command: python application.py

5) The app is set up to work on port 8000, so http://localhost:8000/ in your browser to view the app. It is recommended to use the incognito mode of yoru browser for testing purposes. 

6) You can now view all categories and click into each to view its contents. Because you are not logged in there is not much you can do but view content. Let's log in!

7) In the top right hand side of the screen click 'Log in here'. You will have the option to authenticate to Google or Facebook. I have chosen to use the Google authenticator as I have a Google account to test with so please use this. 
Once logged in you can view existing categories and grocery items, but you cannot edit these because these were created by me

8) Click on 'add category' and you'll be prompted to enter the required form information then click 'save' or click 'cancel' if you change your mind. Once saved this category will belong to you so that you can now edit or delete it. 

9) If you do not like the name of the category you just created you can edit it or delete it altogether. Click into the category and you will see the buttons 'edit category' and 'delete category' respectively. Click 'save' to confirm the change or 'cancel' if you change your mind. 

10) Now you can create a grocery item within the category you just created. Click on the newly created category and then click on 'add grocery item' where you will be prompted to enter the required form data. Click 'create' to confirm or 'cancel' if you change your mind. Once create you will be directed back to the main all categories page. Scroll to the bottom where you will  see under 'Our newest items' the item name and price of the item you just added.

11) If at any point you would like to use the API endpoints for JSON you can find these at:
-http://localhost:8000/category/JSON (where 'JSON' is case sensitive!). To retrieve the data for categories
-http://localhost:8000/category/<int:category_id>/grocery/JSON. To retrieve the data for all items in a single category
-http://localhost:8000/category/<int:category_id>/grocery/<int:grocery_id>/JSON. To retieve the data for a single item in a category

12) If at any point you would like to use the API endpoints for XML you can find these at:
-http://localhost:8000/category/XML (where 'XML' is case sensitive!). To retrieve the data for categories
-http://localhost:8000/category/<int:category_id>/grocery/XML. To retrieve the data for all items in a single category
-http://localhost:8000/category/<int:category_id>/grocery/<int:grocery_id>/XML. To retieve the data for a single item in a category

13) Once you are finished using the app you can click on 'Log out here' where you will be deauthenticated. 


Explanation of repository structure

This respository consists of:

1) this README file

2) application.py where the main file code exitst. This contains the Flask app set up and all of the Flask route functions

3) catalog_database_setup.py. This contains all of the database model classes definitions. Some clases have also been serialized to provide JSON API endpoints. 

4) catalog_database_setup.pyc is an auto generated shadow file of catalog_database_setup.py. You can ignore this. 

5) lotsofcategories.py. database has already been setup but if for whatever reason it become corrupted or disfunctional you can delete the database, run catalog_database_setup.py again and then run this file to re-populate the database records for each table. Be sure however to change the 'user1' variable to match your own Google login credentials. 

6) client_secrets.json; this file contains the client secret to authorize access to Google authentication service. I will remove this file a week after my project submission date as it contains sensitive data. But for the sake of making my project reviewable I have added it here. 

7) fb_client_secrets.json; this file is not used in this project as I do not use Facebook. If however you want to modify the app to use the FB login service you would need to capture the client secret in this file. 

8) supermarketcatalog.db is the actual database 

9) /templates; this folder contains all of the html templates used to generate all pages of the app. 

10) /static; folder contains all of the static images used on the respective pages of the app. For the initial setup I have included images for each item already. But for all newly created grocery items you will have to enter a valid web url for the image. Please be sure to use royalty free images:)


Thanks for using my app. Any questionr or feedback please send me a message on @amharF on Github!


