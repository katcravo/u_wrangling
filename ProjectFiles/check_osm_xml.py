from wrangling_utils import *
filename = 'osm/sample.osm'

#View the tags in the file
tags = count_tags(filename)
print "Tags in " + filename
pprint.pprint(tags)    


tag_types = check_tags(filename)
print "Tag types in " + filename
pprint.pprint(tag_types)

unexpected_st_types = audit_street_types_in_file(filename)

#printing this way to ease creating a map by hand
print "Unexpected street types in " + filename
x = dict(unexpected_st_types)
for key in x:
    print '"'+ key + '" : "",'