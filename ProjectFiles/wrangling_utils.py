import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict
import json
import re


#filename = 'osm/sample.osm'
mapping = {}

"""
Get a list of all the tags and their count
"""

def count_tags(filename):
    osm_file = open(filename, "r")
    print ('opened_file')
    tagsdict = defaultdict (lambda: 0)
    #for event, elem in ET.iterparse(osm_file, events=('start', )):
    #    tagsdict[elem.tag]=tagsdict[elem.tag]+1
    
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end':
            tagsdict[elem.tag]=tagsdict[elem.tag]+1
            root.clear()
    return dict(tagsdict)


"""
check that the tag keys are valid chars
"""
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def check_tags(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    osm_file = open(filename, "r")
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, element in context:
        if event == 'end':
            if element.tag == "tag":
                key = element.attrib['k']
                whichCase = "other"
                if (lower.match(key)): whichCase = "lower"
                elif (lower_colon.match(key)): whichCase = "lower_colon"
                elif (problemchars.search(key)): whichCase = "problemchars"
                #print key, whichCase
                keys [whichCase] = keys [whichCase] + 1
        root.clear()
    return keys
        

"""
Audit Street Types
"""


street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
first_word_re = re.compile(r'^\w+', re.IGNORECASE)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Terrace", "Loop", "Highway", "Course", "Circle", "Way", "Crescent", "Walk",
           "Turnpike", "Bridge", "Causeway", "Gate", "Cove", "Alley", "Thruway", "Hill", "Piers", "Quadrangle",
            "Mews", "Path", "Run", "Expressway", "Freeway",
           "Broadway", "Bowery", ""]
expected_first = ["Avenue", "Route"]
extra_suffix = ["North", "East", "West", "South", "north", "EAST", ]


"""
Add street name to a list if the street type appears invalid
"""
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            #print 'Found', street_type
            if street_type_first(street_name): return
            else: street_types[street_type].add(street_name)

"""
Function to check street valid, where the street type is first, like 'Avenue B'
"""            
def street_type_first(street_name):
    #print 'Check first', street_name
    m = first_word_re.search(street_name)
    if m:
        if m.group() in expected_first:
            #print 'Found Street Type first for', street_name
            return True
    return False
            

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


"""
Review the file for invalid street types
"""
def audit_street_types_in_file(filename):
    street_types = defaultdict(set)
    osm_file = open(filename, "r")
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end':

            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if is_street_name(tag):
                        #print tag.attrib['k'], tag.attrib['v']
                        audit_street_type(street_types, tag.attrib['v'])
        root.clear()
    osm_file.close()
    return street_types


"""
Handle Scenarios where street type is followed by a suffix, such as South
"""    
def process_suffix (name, mapping):
    split_name = name.split(' ')
    if len(split_name) > 2 and split_name[-1] in extra_suffix:
        #print "Has a valid suffix ", name
        return update_name(name.rsplit(' ', 1)[0], mapping) + ' ' + split_name[-1] 
    return None

"""
Get an improved street name by replacing invalid street type where possible
"""
def update_name(name, mapping):
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        
        #print "Checking ", name
        if street_type in expected: pass
        elif street_type in mapping: 
            #print "Fixing name ", name
            name = street_type_re.sub(mapping[street_type], name)
            #print "Fixed name ", name
        else:
            processed_suffix = process_suffix(name, mapping)
            if processed_suffix != None: return processed_suffix
        
        return name     
   
# In[10]:


"""
This section is the start of the code for shaping the OSM XML to JSON
"""
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

"""
Constants for organizing the elements
"""
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
replace_tags = {'addr':'address', 'type':'type_as_specified'}
#has_value_and_children = ['hgv', 'name', 'building', 'railway', 'lanes', 'maxspeed', 'source', 'is_in', 'internet_access', ]
has_value_and_children = []


# In[11]:

"""
Process the top level attributes
"""
def process_attributes(element):
    attributes = {}
    created = {}
    pos = [None,None]

    for attribute in element.attrib:
        value = element.attrib[attribute]

        #organize elements specified in CREATED to a created element
        if attribute in CREATED:
            created[attribute] = value

        #organize the latitude and longitude to a pos [lat,long] element
        elif attribute == 'lat': 
            try:
                pos [0] = float(value)
            except ValueError:
                print "Not a float"                
        elif attribute == 'lon':
            try:
                pos [1] = float(value)
            except ValueError:
                print "Not a float"
                
        #default assignment 
        else: attributes[attribute] = value    

    #include the organized elements to the dict
    attributes['created'] = created
    #Note: Iteration 2: this check for None was introduced after initial nyny was analyzed
    if None not in pos: attributes['pos'] = pos
        
    return attributes    

def process_refs(element):
    node_refs = []
    for ref in element.iter("nd"):
        node_refs.append(ref.attrib['ref'])
    if len(node_refs) > 0 : return {"node_refs":node_refs}
    return {}

"""
Process the list the tag k, v attributes
"""
def process_tags(element, found_complex_tag):
    tags = {}
    for tag in element.iter("tag"):
        process_tag(tag.attrib['k'],tag.attrib['v'], tags, found_complex_tag)
    return tags


# In[12]:

"""
Translate one tag k, v attribute
"""
def process_tag (name, value, tags, found_complex_tag):
    #tags[name]=value
    #if (name.startswith('hgv')): print name, value
    try:
        if (name!= None and len(name)>0 and name.strip()!=':' and 
            name.strip()!='' and not problemchars.search(name)):
            
            levels = name.split(':')
            
            #extract the top level key and convert it as needed
            top = levels[0]
            top = replace_tags.get(top,top)
            
            #assign value if it's a top level attribute
            if len(levels) == 1: 
                if top not in tags: tags[top] = value
                else: 
                    print top, value, ' other value already found as ', tags[top]
                
            #add to address dict if there are two levels
            elif top=='address' and len(levels) == 2:
                if 'address' not in tags: tags['address']={}                    
                if not isinstance(tags['address'],dict): 
                    #print 'address:', name, value, ' overwriting simple value already found as ', tags['address']
                    tags['address']={}
                process_tag (levels[1],value,tags['address'], found_complex_tag)
                
            #add to a dict if there are multiple levels
            elif top!='address' and len(levels) > 1:
                if top in has_value_and_children: top = top + "_data"
                elif top in tags and not isinstance(tags[top],dict): 
                    #a root value was already found for this tag.
                    #print name, value, ' unexpected - simple value already found as ', top, tags[top]
                    found_complex_tag.add(top)
                    return
                if top not in tags: tags[top]={}                    
                process_tag (name.split(':', 1)[1], value, tags[top], found_complex_tag)
                
    except Exception, e:
        print "Failed: %s" % e
        print 'Exception', name, value
        pprint.pprint(tags)
        return


# In[13]:

"""
Modify the given tags dict and fix street name in address
"""
street_tags = ['street']
def fix_street(tags):
    if 'address' in tags:
        addr = tags['address']
        for key in addr:
            if key in street_tags:
                #print 'checking', addr[key]
                addr[key] = update_name(addr[key], mapping)


# In[14]:

"""
Translation method for convering one OSM XML entry to a dict as per specs
"""
def shape_element(element, found_complex_tag):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node['type']=element.tag        
        refs = process_refs(element)
        node.update(refs)
        attrs = process_attributes(element)    
        node.update(attrs)
        tags = process_tags(element, found_complex_tag)
        fix_street(tags)
        node.update(tags)
              
        #pprint.pprint( node )
        return node
    else:
        return None


# In[15]:

"""
Parse an OSM XML file and call shape_element for each entry,
the shaped element is written to a file in json format
"""
def check_has_value_and_children(file_in, pretty = False):
    #data = []
    found_complex_tag = set()
    osm_file = open(filename, "r")
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end':
            el = shape_element(elem, found_complex_tag)
        root.clear()
    return found_complex_tag

# In[16]:

"""
Parse an OSM XML file and call shape_element for each entry,
the shaped element is written to a file in json format
"""
def process_map(file_in, street_mapping, pretty = False):
    file_out = "{0}.json".format(file_in)
    #data = []
    mapping = street_mapping
    with codecs.open(file_out, "w") as fo:
        osm_file = open(file_in, "r")
        context = iter(ET.iterparse(osm_file, events=('start', 'end')))
        _, root = next(context)
        for event, elem in context:
            if event == 'end':
                el = shape_element(elem, set())
                if el:
                    #data.append(el)
                    if pretty:
                        fo.write(json.dumps(el, indent=2)+"\n")
                    else:
                        fo.write(json.dumps(el) + "\n")
            root.clear()
    #return data


"""
******************  ADDITIONAL AUDITS USING THE JSON FILE ****************************
"""

import json

"""
Extract the tags of a particular entry and add it to a set for tracking locations of a tag name
"""
def extract_tags(node,parent,tags):
    for key in node:
        if isinstance (node[key],dict): 
            extract_tags(node[key] , parent + key + ".", tags)
        else:
            if key not in tags: tags[key] = set()
            tags[key].add( parent+key )

"""
Iterate through a file with json entries and capture each tag name's location within documents
"""
def check_for_unique_tags(jsonFile):
    f = open(jsonFile)
    tags = defaultdict(set)
    for line in iter(f):
        #print line
        node = json.loads(line)
        extract_tags(node, '', tags)
    f.close()
    #pprint.pprint (dict(tags))
    multis = {k: v for k, v in (dict(tags)).items() if len(tags[k])>1}
    return multis
    

# In[ ]:

"""
These functions are for checking the data type.  
"""

def isfloat(value):
  try:
    float(value)
    return True
  except:
    return False

def isint(value):
  try:
    int(value)
    return True
  except:
    return False


def get_data_type(value):
    if value == "" or value == "NULL":
        return type(None)
    elif type(value) is list:
        return type([])
    elif isint(value):
        return type(int())
    elif isfloat(value):
        return type(float())
    else:
        return type(str())


def extract_data_types(node,parent,tags):
    for key in node:
        location = parent + key
        if isinstance (node[key],dict): 
            extract_data_types(node[key] , location + ".", tags)
        else:
            if location not in tags: tags[location] = set()
            tags[location].add( get_data_type(node[key]) )

def audit_data_types_in_file(jsonFile):
    f = open(jsonFile)
    tags = defaultdict(set)
    for line in iter(f):
        node = json.loads(line)
        extract_data_types(node, '', tags)
    f.close()
    return dict(tags)
   
"""
DB Utils
"""
def get_db():
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    # 'examples' here is the database name. It will be created if it does not exist.
    db = client.osm
    return db

def aggregate(db, pipeline):
    return [doc for doc in db.nyny.aggregate(pipeline)]


"""
Check Zip code
"""
def make_zip_pipeline():
    
    pipeline = [ 
        { "$match": { "address.postcode" : { "$exists" : True } } },
        { "$group" : { "_id": "$address.postcode", "count" : {"$sum" : 1 }}},
        { "$sort": {"_id":1 }} ]
    return pipeline

"""
Functions to get distinct values for a field and the count of each
"""

def make_distinct_with_count_pipeline( by_field ):    
    pipeline = [ 
        { "$match": { by_field : { "$exists" : True } } },
        { "$group" : { "_id": "$" + by_field , "count" : {"$sum" : 1 }}},
        { "$sort" : { "count": -1 }},
        { "$limit" : 20 } ]
    return pipeline

def distinct_with_count(field_name):
    db = get_db()
    pipeline = make_distinct_with_count_pipeline(field_name)
    result = aggregate(db, pipeline)
    return result

def make_countdistinct_pipeline( by_field ):
    pipeline = [
        { "$match": { by_field : { "$exists" : True } } },
        { "$group" : { "_id": "$" + by_field }},
        { "$group": { "_id": by_field, "count" : {"$sum" : 1 } } } ]
    return pipeline


def count_distinct(field_name):
    db = get_db()
    pipeline = make_countdistinct_pipeline(field_name)
    result = aggregate(db, pipeline)
    return result[0]


def print_count_distincts(fields):
    for field_name in fields:
        #pprint.pprint(get_top(field_name))
        count_dist = count_distinct(field_name)
        print "Distinct ", field_name, count_dist['_id'], ' - count', count_dist['count']


"""
Functions to get top value for a field and the count of each
"""

def make_get_top_pipeline( by_field ):    
    pipeline = [ 
        { "$match": { by_field : { "$exists" : True } } },
        { "$group" : { "_id": "$" + by_field , "count" : {"$sum" : 1 }}},
        { "$sort": { "count" :-1 }},
        { "$limit" : 1 } ]
    return pipeline

def get_top(field_name):
    db = get_db()
    pipeline = make_get_top_pipeline(field_name)
    result = aggregate(db, pipeline)
    return result[0]

def print_tops(fields):
    for field_name in fields:
        #pprint.pprint(get_top(field_name))
        top = get_top(field_name)
        print "Top", field_name, top['_id'], ' - count', top['count']
