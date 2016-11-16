from wrangling_utils import *

print "*****************"
print "Connect to Db"
db = get_db()
print db.nyny.find_one()
print db.nyny.find_one({"address.postcode" : { "$exists" : True } })

print "Size of Db:"
size = db.nyny.count()
print size
print " "

print "*****************"
print "Checking zip codes:"
pipeline = make_zip_pipeline()
result = aggregate(db, pipeline)
#print result
print " " 
"""
Inspect records with bad zip codes
"""
print "*****************"
print " " 
print "Wrong lengths..."
wrong_length = [ rec['_id'] for rec in result if len(rec['_id']) != 5]
print wrong_length
print "*****************"
print "Wrong length examples:"
print "*"
for zip in (wrong_length[:2]):
    res = db.nyny.find_one({"address.postcode" : zip})
    pprint.pprint(res)
    print "*"
print " "

print "*****************"
print " " 
print "Wrong characters..."
wrong_start = [ rec['_id'] for rec in result if not (rec['_id'].startswith('11') or rec['_id'].startswith('10') ) ]
print wrong_start
print "******************"
print "Wrong characters examples:"
print "*" 
for zip in (wrong_start[:2]):
    res = db.nyny.find_one({"address.postcode" : zip})
    pprint.pprint(res)
    print "*"
print " " 
print "*****************"


print "******************"
print "Count unique values:"
get_count_distincts_fields = ['created.user', 'address.postcode', 'address.city', 'source']
print_count_distincts(get_count_distincts_fields)


print "******************"
print "Top values:"
get_top_fields = ['created.user', 'address.postcode', 'address.city']
print_tops(get_top_fields)


get_distincts = ["type", "address.state", "source", "cuisine", "leisure", "office", "service", "shop", "sport", "amenity"]
for field_name in get_distincts:
    print "**************"
    print "Distinct", field_name
    pprint.pprint (distinct_with_count(field_name))
    print " "

