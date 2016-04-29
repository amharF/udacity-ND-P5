from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from catalog_database_setup import Base, Category, GroceryItem, User
from flask import session as login_session
import random
import string
from oauth2client import client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from flask.ext.seasurf import SeaSurf

app = Flask(__name__)

csrf = SeaSurf(app)

CLIENT_ID = json.loads(open('/var/www/FlaskApp/FlaskApp/client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Supermarket Catalog App"

# Connect to Database and create database session
engine = create_engine('postgresql://catalog:supermarket@localhost/supermarketcatalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


#authenticate through Google
@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/FlaskApp/FlaskApp/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connecte\
            d.'),200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']


    #see if users exists, if it doesnt make a new one
    user_id = getUserID(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-\
    webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


#user helper function
#create a new user in the database User table passing in the data from login_session
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

#retrieve user data from User table
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

#retrieve user email from User table
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

#DISCONNECT - Revoke a current user's token and reset their login_session from 
#Google

@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = client.OAuth2Credentials.from_json(login_session.get('credentials'))
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print "this is the credentials object %s" %credentials
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]


    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
            

    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

    

"""

#authenticate to Facebook
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchan\
    ge_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, 
        app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, 
    #let's strip out the information before the equals sign in our token
    
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200\
    &width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-\
    webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

#DISCONNECT - Revoke a current user's token and reset their login_session from
#Facebook
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

"""


#JSON APIs to view Supermarket category information

#return all categories
@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories = [c.serialize for c in categories])

#return all items in one single category
@app.route('/category/<int:category_id>/grocery/JSON')
def categoryGroceryJSON(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(GroceryItem).filter_by(category_id = 
        category_id).all()
    return jsonify(GroceryItems = [i.serialize for i in items])

#return one single item
@app.route('/category/<int:category_id>/grocery/<int:grocery_id>/JSON')
def groceryItemJSON(category_id, grocery_id):
    grocery_item = session.query(GroceryItem).filter_by(id = 
        grocery_id).one()
    return jsonify(grocery_item = grocery_item.serialize)


#XML APIs to view Supermarket category information

#return all categories
@app.route('/category/XML')
def categoriesXML():
    categories = session.query(Category).all()

    # Declare root node of XML 
    top = Element('Categories') 
    comment = Comment('XML Response with all categories')
    top.append(comment)

    # Loop through query responses and format as XML
    for c in categories:
        category = SubElement(top, 'category')
        category_id = SubElement(category, 'id')
        category_id.text = str(c.id)
        category_name = SubElement(category, 'name')
        category_name.text = str(c.name)

    return app.response_class(tostring(top), mimetype='application/xml')


#return all items in one single category
@app.route('/category/<int:category_id>/grocery/XML')
def categoryGroceryXML(category_id):
    category = session.query(Category).filter_by(id = category_id).all()
    items = session.query(GroceryItem).filter_by(category_id = 
        category_id).all()

    # Declare root node of XML 
    top = Element('Category') 
    comment = Comment('XML Response with a single category with all items within it')
    top.append(comment)
    
    # Loop through query responses and format as XML
    for c in category:
        grocery_category = SubElement(top, 'category')
        grocery_category_id = SubElement(grocery_category, 'id')
        grocery_category_id.text = str(c.id)
        grocery_category_name = SubElement(grocery_category, 'name')
        grocery_category_name.text = str(c.name)
        grocery_item = SubElement(grocery_category, 'item')
        for i in items:
            grocery_item_id = SubElement(grocery_item, 'id')
            grocery_item_id.text = str(i.id)
            grocery_item_name = SubElement(grocery_item, 'name')
            grocery_item_name.text = str(i.name)
            grocery_item_des = SubElement(grocery_item, 'description')
            grocery_item_des.text = str(i.description)
            grocery_item_price = SubElement(grocery_item, 'price')
            grocery_item_price.text = str(i.price)


    return app.response_class(tostring(top), mimetype='application/xml') 


#return one single item
@app.route('/category/<int:category_id>/grocery/<int:grocery_id>/XML')
def groceryItemXML(category_id, grocery_id):
    grocery_item = session.query(GroceryItem).filter_by(id = 
        grocery_id).all()
    
    # Declare root node of XML 
    top = Element('Item') 
    comment = Comment('XML Response with a single item with all its attributes')
    top.append(comment)

    for i in grocery_item:
        grocery_item_item = SubElement(top, 'item')
        grocery_item_id = SubElement(grocery_item_item, 'id')
        grocery_item_id.text = str(i.id)
        grocery_item_name = SubElement(grocery_item_item, 'name')
        grocery_item_name.text = str(i.name)
        grocery_item_des = SubElement(grocery_item_item, 'description')
        grocery_item_des.text = str(i.description)
        grocery_item_price = SubElement(grocery_item_item, 'price')
        grocery_item_price.text = str(i.price)
        
    return app.response_class(tostring(top), mimetype='application/xml') 


#Show all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.id))
    last_added = session.query(GroceryItem).order_by(desc(GroceryItem.id)).limit(5)

    if 'username' not in login_session:
        return render_template('publiccategories.html', categories = categories, 
        login_session = login_session, last_added=last_added)
    else:
        return render_template('categories.html', categories = categories, 
        login_session = login_session, last_added=last_added)

#Create a new category
@app.route('/category/new/', methods=['GET','POST'])
def newCategory():

    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        #add user ID from login_session to Category table   
        newCategory = Category(name = request.form['name'], 
            user_id = login_session['user_id']) 
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newcategory.html', 
            login_session = login_session)

#Edit a category
@app.route('/category/<int:category_id>/edit/', methods = ['GET', 'POST'])
def editCategory(category_id):
    
    if 'username' not in login_session:
        return redirect('/login')

    editedCategory = session.query(Category).filter_by(id=category_id).one()
    
    if editedCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized \
            to edit this category. Please create your own category in order \
            to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('showCategories'))
    else:
        return render_template('editcategory.html', category = editedCategory, 
            login_session = login_session)

#Delete a category
@app.route('/category/<int:category_id>/delete/', methods = ['GET', 'POST'])
def deleteCategory(category_id):
    
    if 'username' not in login_session:
        return redirect('/login')

    categoryToDelete = session.query(Category).filter_by(id=category_id).one()

    if categoryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized \
            to delete this category. Please create your own category in order \
            to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCategories', category_id = category_id))
    else:
        return render_template('deletecategory.html', category = 
            categoryToDelete, login_session = login_session)

#Show a category grocery
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/grocery/')
def showGrocery(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(GroceryItem).filter_by(category_id = category_id).all()
    creator = getUserInfo(category.user_id) 
    
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicgrocery.html', items = items, 
            category = category, creator = creator, login_session = login_session)
    else:
        return render_template('grocery.html', items = items, 
            category = category, creator = creator, login_session = login_session) 

#Create a new grocery item
@app.route('/category/<int:category_id>/grocery/new/', methods=['GET', 'POST'])
def newGroceryItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    
    category = session.query(Category).filter_by(id=category_id).one()
    
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
            to add grocery items to this category. Please create your own \
            category in order to add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newItem = GroceryItem(name=request.form['name'], 
                description=request.form['description'], price=request.form['price'], 
                item_image=request.form['item_image'], category_id=category_id, 
                user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Grocery Item %s Successfully Created' % (newItem.name))
        return redirect(url_for('showGrocery', category_id=category_id))
    else:
        return render_template('newgroceryitem.html', category_id=category_id, 
            login_session = login_session)

#Edit a grocery item
@app.route('/category/<int:category_id>/grocery/<int:grocery_id>/edit', 
    methods=['GET', 'POST'])
def editGroceryItem(category_id, grocery_id):
    if 'username' not in login_session:
        return redirect('/login')
    
    category = session.query(Category).filter_by(id=category_id).one()
    editedItem = session.query(GroceryItem).filter_by(id=grocery_id).one()
    
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
            to edit grocery items in this category. Please create your own \
            category in order to edit items.');}</script><body onload='myFunc\
            tion()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['item_image']:
            editedItem.item_image = request.form['item_image']
        session.add(editedItem)
        session.commit()
        flash('Grocery Item Successfully Edited')
        return redirect(url_for('showCategories', category_id=category_id))
    else:
        return render_template('editgroceryitem.html', 
            category_id=category_id, grocery_id=grocery_id, item=editedItem, 
            login_session = login_session)


#Delete a menu item
@app.route('/category/<int:category_id>/grocery/<int:grocery_id>/delete', 
    methods=['GET', 'POST'])
def deleteGroceryItem(category_id, grocery_id):
    if 'username' not in login_session:
        return redirect('/login')
    
    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(GroceryItem).filter_by(id=grocery_id).one()
    
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
            to delete grocery items from this category. Please create your \
            own category in order to delete items.');}</script><body onload='\
            myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Grocery Item Successfully Deleted')
        return redirect(url_for('showGrocery', category_id=category_id))
    else:
        return render_template('deletegroceryitem.html', item=itemToDelete, 
            login_session = login_session)



if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)
