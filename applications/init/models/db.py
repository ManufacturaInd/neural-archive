# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite')
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db = db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
#response.generic_patterns = ['*'] if request.is_local else []

response.generic_patterns = ['*.json','*.xml', '*.rss']

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key())
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables()

## configure email
mail=auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth,filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

from image import thumber

db.define_table('entry',
   # Field('title', unique=True),
   Field('title'),
   Field('author'),
   Field('language', comment='Separate multiple languages with commas, e.g. "English, German".'),
   Field('description'),
   Field('link'),

   Field('country'),
   Field('year', 'integer', label='Year of publication'),
   #Field('publication_date', comment='This is a legacy field. Use Year of publication instead.'),
   Field('image', 'upload'),
   Field('image_medium', 'upload'),
   Field('image_thumbnail', 'upload'),
   Field('image_name', writable=False, comment="Legacy field, don't mind this."),
   Field('isbn', label='ISBN'),
   Field('ean', label='EAN'),
   Field('pages', 'integer', label='Number of pages'),
   Field('publisher'),
   Field('type', comment='Use title case. Examples: "Catalogue", "Journal", "Book + CD".'),
   Field('issue', label='Issue number'),
   #Field('description', 'text'),
   Field('missed_data', 'text', writable=False),
   Field('pub_index', 'text', label='Index'),
   
   Field('created_on', 'datetime', default=request.now),
   #Field('created_by', db.auth_user, default=auth.user_id),
   
   format = '%(title)s',
   migrate = True, fake_migrate = True,
   # migrate = False,
   )

#db.define_table('comment',
#   Field('entry_id', db.entry),
#   Field('author'),
#   Field('email'),
#   Field('body', 'text'))

db.entry.title.requires = IS_NOT_IN_DB(db, db.entry.title)
db.entry.year.requires = IS_EMPTY_OR(IS_INT_IN_RANGE(1000,5000)) # futureproof ;o)

db.entry.created_on.writable = False
db.entry.id.represent = lambda id: A('View',_href=URL(r=request,f='show',args=(id)))

db.entry.image.requires = IS_EMPTY_OR(IS_IMAGE(extensions=["jpeg","png","gif"], minsize=(-1,-1)))
db.entry.image_medium.compute = lambda row: thumber(row.image, 300, 2000) 
db.entry.image_thumbnail.compute = lambda row: thumber(row.image, 85, 2000, name='thumbnail') 

#auth.settings.actions_disabled.append('register')
if request.controller != 'appadmin':
    auth.settings.actions_disabled +=['register']

#db.entry.id.readable=False

#db.comment.entry_id.requires = IS_IN_DB(db, db.entry.id, '%(title)s')
#db.comment.author.requires = IS_NOT_EMPTY()
#db.comment.email.requires = IS_EMAIL()
#db.comment.body.requires = IS_NOT_EMPTY()

#db.comment.entry_id.writable = db.comment.entry_id.readable = False
