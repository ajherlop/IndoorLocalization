#!/usr/bin/env python
###
### This web service is used in conjunction with App
### Inventor for Android. It stores and retrieves data as instructed by an App Inventor app and its TinyWebDB component.
### It also provides a web interface to the database for administration

### Author: Dave Wolber via template of Hal Abelson and incorporating changes of Dean Sanvitale

### Note-- updated for use with Python2.7 in App Engine, June 2013

import webapp2

import math
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.db import Key
from django.utils import simplejson as json

# DWW
import os
from google.appengine.ext.webapp import template
import urllib

# DEAN
import logging
import re

max_entries = 1000

class StoredData(db.Model):
  tag = db.StringProperty()
  value = db.TextProperty()
  date = db.DateTimeProperty(required=True, auto_now=True)


class StoreAValue(webapp2.RequestHandler):

  def store_a_value(self, tag, value):
  	if tag == "CurrentPosition":  #condicion para algoritmo
			distances = []
			ref = value  #cogemos (MAC,POW) de la posicion actual
			ref = ref[1:-1]
			# Toda esta parte es para adaptar los datos a listas
			a = ref[0:ref.find(']') + 1]
			ref = ref[ref.find(']')+ 2:]
			b = ref[0:ref.find(']') + 1]
			# ref = ref[ref.find(']')+ 2:]
			# c = ref[0:ref.find(']') + 1]
			# a = a[1:-1]
			aa = eval(a)
			# b = b[1:-1]
			# bb = b.split(',')
			bb= eval(b)
			# c = c[1:-1]
			# cc = c.split(',')
			# cc = eval(c)
			ref = [aa, bb]
			
			
			
			
			#este trozo el como el get de abajo comentado
			entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", 'locations').get()
			if entry:
				locationList = eval(entry.value)
			else:
				locationList = ""	
			##locationList = get_value(locations)                                           # cogemos la lista de posiciones que existen en la base de datos
			
			position = locationList.index('1')
			locationList.pop(position)
			position = locationList.index('2')
			locationList.pop(position)
			position = locationList.index('3')
			locationList.pop(position)
			position = locationList.index('4')
			locationList.pop(position)
			
			for i in range(len(locationList)):  #bucle para ir cogiendo todos los valores

				dist = 0
				#este trozo el como el get de abajo comentado
				entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", locationList[i]).get()
				if entry:
					comp = entry.value
					comp = comp[1:-1]
					## Toda esta parte es para adaptar los datos a listas
					d = comp[0:comp.find(']') + 1]
					comp = comp[comp.find(']')+ 2:]
					e = comp[0:comp.find(']') + 1]
					comp = comp[comp.find(']')+ 2:]
					f = comp[0:comp.find(']') + 1]
					# a = a[1:-1]
					# b = b[1:-1]
					# c = c[1:-1]
					# aa = eval(a)
					# bb = b.split(',')
					# cc = c.split(',')
					dd = eval(d)
					ee = eval(e)
					ff = eval(f)
					comp = [dd, ee, ff]
					
					
				else:
					comp = ""
				 ##comp = get_value(locationList[i])
				
				
				
				
				
				
				for j in range(len(ref[0])):
					if ref[0][j] in comp[0]: 
						powIndex = comp[0].index(ref[0][j])
						dist = dist + ((float(ref[1][j]) - comp[1][powIndex])**2) ##Donde coincida la mac (indice 0) coincide la potencia (indice 1)
						
				if dist == 0:
					dist = 10000
					distances.append(dist) ## Si no ha habido ninguna coincidencia, la distancia es enorme
				else:
					distances.append(math.sqrt(dist))
				
					
			#este trozo el como el get de abajo comentado
			minIndex = distances.index(min(distances))
			entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", locationList[minIndex]).get()
			if entry:
				final = entry.value
				final = final[1:-1]
				## Toda esta parte es para adaptar los datos a listas
				x = final[0:final.find(']') + 1]
				final = final[final.find(']')+ 2:]
				y = final[0:final.find(']') + 1]
				final = final[final.find(']')+ 2:]
				z = final[0:final.find(']') + 1]
				xx = eval(x)
				yy = eval(y)
				zz = eval(z)
				final = [xx, yy, zz]
			else:
				final = ""
				
			 ###final = get_value(locationList[minIndex])
			 
			# value = final[2]  ##valores xy de la posicion
			tag = 'CurrentPosition'
			value = '[%d,%d]' % (final[2][0], final[2][1])
			
			

  	store(tag, value)
	# call trimdb if you want to limit the size of db
  	# trimdb()
	
	# Send back a confirmation message.  The TinyWebDB component ignores
	# the message (other than to note that it was received), but other
	# components might use this.
	result = ["STORED", tag, value]
	
	# When I first implemented this, I used  json.JSONEncoder().encode(value)
	# rather than json.dump.  That didn't work: the component ended up
	# seeing extra quotation marks.  Maybe someone can explain this to me.
	
	if self.request.get('fmt') == "html":
		WriteToWeb(self,tag,value)
	else:
		WriteToPhoneAfterStore(self,tag,value)
	

  def post(self):
	tag = self.request.get('tag')
	value = self.request.get('value')
	self.store_a_value(tag, value)

class DeleteEntry(webapp2.RequestHandler):

  def post(self):
	logging.debug('/deleteentry?%s\n|%s|' %
				  (self.request.query_string, self.request.body))
	entry_key_string = self.request.get('entry_key_string')
	key = db.Key(entry_key_string)
	tag = self.request.get('tag')
	if tag.startswith("http"):
	  DeleteUrl(tag)
	db.run_in_transaction(dbSafeDelete,key)
	self.redirect('/')


class GetValueHandler(webapp2.RequestHandler):

  def get_value(self, tag):

    entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", tag).get()
    if entry:
       value = entry.value
    else: value = ""
  
    if self.request.get('fmt') == "html":
    	WriteToWeb(self,tag,value )
    else:
	WriteToPhone(self,tag,value)

  def post(self):
    tag = self.request.get('tag')
    self.get_value(tag)

  # there is a web ui for this as well, here is the get
  def get(self):
    # this did pump out the form
    template_values={}
    path = os.path.join(os.path.dirname(__file__),'index.html')
    self.response.out.write(template.render(path,template_values))


class MainPage(webapp2.RequestHandler):

  def get(self):
    entries = db.GqlQuery("SELECT * FROM StoredData ORDER BY date desc")
    template_values = {"entryList":entries}
    # render the page using the template engine
    path = os.path.join(os.path.dirname(__file__),'index.html')
    self.response.out.write(template.render(path,template_values))

#### Utilty procedures for generating the output

def WriteToPhone(handler,tag,value):
 
    handler.response.headers['Content-Type'] = 'application/jsonrequest'
    json.dump(["VALUE", tag, value], handler.response.out)

def WriteToWeb(handler, tag,value):
    entries = db.GqlQuery("SELECT * FROM StoredData ORDER BY date desc")
    template_values={"result":  value,"entryList":entries}  
    path = os.path.join(os.path.dirname(__file__),'index.html')
    handler.response.out.write(template.render(path,template_values))

def WriteToPhoneAfterStore(handler,tag, value):
    handler.response.headers['Content-Type'] = 'application/jsonrequest'
    json.dump(["STORED", tag, value], handler.response.out)




# db utilities from Dean

### A utility that guards against attempts to delete a non-existent object
def dbSafeDelete(key):
  if db.get(key) :	db.delete(key)
  
def store(tag, value, bCheckIfTagExists=True):
	if bCheckIfTagExists:
		# There's a potential readers/writers error here :(
		entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", tag).get()
		if entry:
		  entry.value = value
		else: entry = StoredData(tag = tag, value = value)
	else:
		entry = StoredData(tag = tag, value = value)
	entry.put()		
	
def trimdb():
	## If there are more than the max number of entries, flush the
	## earliest entries.
	entries = db.GqlQuery("SELECT * FROM StoredData ORDER BY date")
	if (entries.count() > max_entries):
		for i in range(entries.count() - max_entries): 
			db.delete(entries.get())

from htmlentitydefs import name2codepoint 
def replace_entities(match):
    try:
        ent = match.group(1)
        if ent[0] == "#":
            if ent[1] == 'x' or ent[1] == 'X':
                return unichr(int(ent[2:], 16))
            else:
                return unichr(int(ent[1:], 10))
        return unichr(name2codepoint[ent])
    except:
        return match.group()

entity_re = re.compile(r'&(#?[A-Za-z0-9]+?);')

def html_unescape(data):
    return entity_re.sub(replace_entities, data)
    
def ProcessNode(node, sPath):
	entries = []
	if node.nodeType == minidom.Node.ELEMENT_NODE:
		value = ""
		for childNode in node.childNodes:
			if (childNode.nodeType == minidom.Node.TEXT_NODE) or (childNode.nodeType == minidom.Node.CDATA_SECTION_NODE):
				value += childNode.nodeValue

		value = value.strip()
		value = html_unescape(value)
		if len(value) > 0:
			entries.append(StoredData(tag = sPath, value = value))
		for attr in node.attributes.values():
			if len(attr.value.strip()) > 0:
				entries.append(StoredData(tag = sPath + ">" + attr.name, value = attr.value))
		
		childCounts = {}
		for childNode in node.childNodes:
			if childNode.nodeType == minidom.Node.ELEMENT_NODE:
				sTag = childNode.tagName
				try:
					childCounts[sTag] = childCounts[sTag] + 1
				except:
					childCounts[sTag] = 1
				if (childCounts[sTag] <= 5):
					entries.extend(ProcessNode(childNode, sPath + ">" + sTag + str(childCounts[sTag])))
		return entries
		
def DeleteUrl(sUrl):
	entries = StoredData.all().filter('tag >=', sUrl).filter('tag <', sUrl + u'\ufffd')
	db.delete(entries[:500])
  

### Assign the classes to the URL's

app = webapp2.WSGIApplication ([('/', MainPage),
                           ('/getvalue', GetValueHandler),
			   ('/storeavalue', StoreAValue),
		           ('/deleteentry', DeleteEntry)

                           ])



