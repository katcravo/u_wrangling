from wrangling_utils import *
filename = 'osm/sample.osm'

multis = check_for_unique_tags(filename + '.json')
print "Tags that occur in multiple locations in the document"
pprint.pprint(multis)

data_types = audit_data_types_in_file(filename + '.json')
print "Data Types in File:"
pprint.pprint(data_types)

print "Types associated with zip code:"
pprint.pprint(data_types['address.postcode'])