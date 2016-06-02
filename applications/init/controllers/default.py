# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    # response.flash = "Welcome to the Neural Archive!"
    entries = db(db.entry.image != '').select(db.entry.ALL, orderby=~db.entry.created_on, limitby=(0,100))
    # entries = db().select(db.entry.ALL, orderby=~db.entry.created_on, limitby=(0,100))

    # divide the list into 10 lists
    entryset = []
    for x in chunks(entries, 10):
        entryset.append(x)
    return dict(entryset=entryset)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)

#@services.xmlrpc
def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

def feed():
    entries=db().select(db.entry.ALL).as_list()
    for i in range(len(entries)):
            # set link
            entries[i]['link'] = 'http://archive.neural.it/init/default/show/' + str(entries[i]['id'])
            for key in entries[i]:
                try:
                    entries[i][key] = entries[i][key].decode('utf8')
                except:
                    entries[i][key] = entries[i][key]
                

    return dict(title="Neural Archive",
                link="http://archive.neural.it/init/default/feed",
                description="Archive feed",
                entries=entries)
                
@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

def browse():
    if request.function == 'first':
        response.flash = "Entry created!"
    
    # paginate
    if len(request.args): 
        page = int(request.args[0])
    else: 
        page = 0
    items_per_page = 50
    limitby = (page*items_per_page, (page+1)*items_per_page+1)    
    
    # filter publication type
    pubtype = request.get_vars.get('pubtype')
    if pubtype:
        if pubtype == 'book':
            entries = db((db.entry.type == 'Book') |
                         (db.entry.type == 'Book + CD') | 
                         (db.entry.type == 'Book + DVD-ROM')).select(orderby=db.entry.title, limitby=limitby)
        elif pubtype == 'magazine':
            entries = db(db.entry.type == 'Magazine').select(orderby=db.entry.title, limitby=limitby)
        elif pubtype == 'catalogue':
            entries = db(db.entry.type == 'Catalogue').select(orderby=db.entry.title, limitby=limitby)                 
        elif pubtype == 'flyer':
            entries = db(db.entry.type == 'Flyer').select(orderby=db.entry.title, limitby=limitby)     
        elif pubtype == 'journal':
            entries = db(db.entry.type == 'Journal').select(orderby=db.entry.title, limitby=limitby)
        else:
            # invalid pubtype
            pubtype = None
            entries = db().select(db.entry.ALL, orderby=db.entry.title, limitby=limitby)
    else:
        entries = db().select(db.entry.ALL, orderby=db.entry.title, limitby=limitby)
    return dict(entries=entries, page=page, items_per_page=items_per_page, pubtype=pubtype)

@auth.requires_login()
def add():
    form = SQLFORM(db.entry, showid=False, 
                   submit_button="Add new publication").process()
    if form.accepted:
        session.flash = 'Created!'
        redirect(URL('show',args=form.vars.id))
    #form = crud.create(db.entry,
    #                   next=URL('show',args=request.args(0)),
    #                   message=T('New entry created!'))
    return dict(form=form)
    
def show():
    entry = db(db.entry.id==request.args(0)).select().first()
    #db.comment.image_id.default = image.id
    #form = SQLFORM(db.comment)
    #if form.process().accepted:
    #    response.flash = 'your comment is posted'
    #comments = db(db.comment.image_id==image.id).select()
    #return dict(image=image, comments=comments, form=form)
    return dict(entry=entry)
    
def show_html():
    entry = db(db.entry.id==request.args(0)).select().first()
    return dict(entry=entry)
    
def iframe_latest():
    entries = db()
    entries = entries(db.entry.image != '')
    entries = entries.select(orderby=~db.entry.created_on, limitby=(0,2))
    return dict(entries=entries)
    
@auth.requires_login()
def edit():
     this_entry = db.entry(request.args(0)) or redirect(URL('index'))
     form = SQLFORM(db.entry, record=request.args(0),
                    deletable=True, showid=False, 
                    submit_button="Update this publication").process()
     if form.accepted:
        if form.vars.delete_this_record: # form.vars.delete_this_record is True in case one submits form to delete a record
            session.flash = 'Publication deleted'
            redirect(URL('browse'))
        else:
            session.flash = 'Publication updated'
            redirect(URL('show',args=request.args(0)))
     #form = crud.update(db.entry, this_entry,
     #                   next=URL('show',args=request.args))
     return dict(form=form)

def search():
     db.entry.title.represent = lambda title, row: A(title,_href=URL(r=request,f='show',args=(row.id)))
     form, results = crud.search(db.entry,
                       queries = ['equals', 'contains', 'starts with', 'ends with', 'greater than', 'less than'],
                       query_labels={'equals': 'is',
                                     'contains':'contains',
                                     'starts with': 'starts with',
                                     'ends with': 'ends with',                                     
                                     'greater than':'later than',
                                     'less than':'earlier than'},
                       fields = ['id', 'title', 'pub_index', 'year', 'country', 'type', 'author', 'publisher'],
                       field_labels = {'title':'Title', 'pub_index':'Index', 'year':'Publication year',
                                       'country': 'Country', 'type': 'Publication Type', 'author': 'Author',
                                       'publisher': 'Publisher/Label'},
                       zero='Please choose',
                       chkall=True,
                       )

     columns = ['entry.id', 'entry.title', 'entry.pub_index', 'entry.year', 'entry.author', 'entry.country']
     headers = {
        'entry.id':{
        'label':T(' '),
        'class':'', #class name of the header
        'width':'5%', #width in pixels or %
        'truncate': 50, #truncate the content to...
        'selected': False #agregate class selected to this column
        },
        'entry.title':{
        'label':T('Title'),
        'class':'', #class name of the header
        'width':'25%', #width in pixels or %
        'truncate': 40, #truncate the content to...
        'selected': False #agregate class selected to this column
        },
        'entry.pub_index':{
        'label':T('Index'),
        'class':'', #class name of the header
        'width':'40%', #width in pixels or %
        'truncate': 50, #truncate the content to...
        'selected': False #agregate class selected to this column
        },
        'entry.year':{
        'label':T('Year'),
        'class':'', #class name of the header
        'width':'10%', #width in pixels or %
        'selected': False #agregate class selected to this column
        },
        'entry.author':{
        'label':T('Author(s)'),
        'class':'', #class name of the header
        'width':'5%', #width in pixels or %
        'truncate': 50, #truncate the content to...
        'selected': False #agregate class selected to this column
        },
        'entry.country':{
        'label':T('Country'),
        'class':'', #class name of the header
        'width':'5%', #width in pixels or %
        'selected': False, #agregate class selected to this column
        'truncate': 50, #truncate the content to...
        },
        'entry.type':{
        'label':T('Publication type'),
        'class':'', #class name of the header
        'width':'5%', #width in pixels or %
        'selected': False, #agregate class selected to this column
        'truncate': 50, #truncate the content to...
        },
        'entry.publisher':{
        'label':T('Publisher'),
        'class':'', #class name of the header
        'width':'5%', #width in pixels or %
        'selected': False, #agregate class selected to this column
        'truncate': 50, #truncate the content to...
        },
     }                       

     return dict(form=form, results=results)
     if results:
         #linkto=URL('show',args=request.args(0))
         #upload=URL('download',args=request.args(0))
         table = SQLTABLE(results,headers=headers, orderby=False, _class='sortable')

         return dict(form=form, table=table)
     else:
         return dict(form=form, table=None)

from random import randint
def random():
     random_entry = db().select(db.entry.ALL,orderby='<random>',limitby=(0,1))[0]
     return redirect(URL('show',args=(random_entry.id)))

def random_html():
     random_entry = db().select(db.entry.ALL,orderby='<random>',limitby=(0,1))[0]
     return redirect(URL('show_html',args=(random_entry.id)))
