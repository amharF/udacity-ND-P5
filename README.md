# udacity-ND-P5
Configuring Linux Server + Deployment of udacity-ND-P3 'supermarket catalog app' onto this server


i. The IP address and SSH port so your server can be accessed by the reviewer:

IP address: 52.34.173.23
SSH port: 2200
SSH as new user: $ ssh grader@52.34.173.23 -p2200 -i ~/.ssh/udacity_key.rsa

ii. The complete URL to your hosted web application:

http://ec2-52-34-173-23.us-west-2.compute.amazonaws.com

iii. A summary of software you installed and configuration changes made.

software installed:

ntp: to change Ubuntu machine timezome to utc
apache2: webserver
git: version control
libapache2-mod-wsgi python-dev: Python additional libraries for serving Flask from Apache
python-pip: Python package installer
virtualenv: for installation of Flask
Flask: web framework
httplib2: http client library 
requests: http library to handle requests to Apache2
flask-seasurf: Flask extension for preventing cross-site request forgery (CSRF)
sqlalchemy: SQL Object Relational Mapper for Python
python-psycopg2: Python database apater for PostgreSQL
postgresql: database application

configuration changes made:

1) set-up development environment as per Udacity instructions: 
a) downloaded RSA key
b) changed persmissions to access key

2) created new Ubuntu user 'grader' gave superuser permissions

3) updated installed packages on Ubuntu:
a) updated package list
b) actually installed upgrades

4) configured ssh access:
a) changed port to 2200
b) allow new user grader
c) create new ssh key for grader

5) configured firewall to only allow incoming connections to port 2200, 80 and 123

6) set timezone to UTC

7) fixed error sudo: unable to resolve host

8) modified logger to provide more detail, set to Verbose

9) installed and modified Apache to serve mod_wsgi application

10) installed Git and change user/email configuration

11) made a Flask intuitive directory structure to store application files

12) downloaded files from Git to server and copied application files to correct Flask application directories. 
Renamed files as required

13) installed & activated virtual environment

14) created wsgi file, reference correct application path and placed at top level of application directory

15) installed Flask and configured virtual host '.conf' file:
a) handle requests from port 80
b) reference correct ServerName and ServerAdmin address
c) point to wsgi file
d) point to correct directories for template and static files
e) deactivate old default virtual host
f) activate new virtual host

16) installed all modules imported in main application file

Directory structure now looks like:

|--------FlaskApp
|----------------FlaskApp
|-----------------------static
|-----------------------templates
|-----------------------venv
|-----------------------__init__.py
|----------------flaskapp.wsgi

17) installed and configured PostgreSQL and added 'catalog' user to retrieve/create DB entries with password

18) create new client_secret file on console.developers.com to include new IP address and port

19) restared Apache

20) added summy users to database to check that content is protected from non autohirized users

iv. A list of any third-party resources you made use of to complete this project.

Digital Ocean
Github
Google
StackOverflow
Udacity discusion forum
Ubuntu documentation
