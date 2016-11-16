The code is inside the py scripts.
The sample file was made to 1/1000.
The xml was transformed to JSON to import to Mongo Db (2.4).
The JSON was imported to mongo using the mongo import utility.

-------------------------------------------------------------------------------------------------------------------------


Files
-----------

p3.pdf:
A pdf document containing your answers to the rubric questions. This file should document your data wrangling process.

ProjectFiles/*.py
Python code used in auditing and cleaning the dataset for the final project. 
  Prep: gen_sample_file.py - reads "osm/new-york_new-york.osm" and generates 1/1000 sample "osm/sample.osm"
  Step 1: check_osm_xml.py - Checks tags and street types in the osm xml file 'osm/sample.osm'
  Step 2: gen_osm_json_file.py - Sets the street types mapping and generates the json file
  Step 3: check_osm_json.py - Checks the generated json file for data types and duplicate tags
  Step 4: explore_osm_mongo.py - Runs queries on the database
  Utilities: wrangling_utils.py has the functions supporting above

chosen_area.txt
A text file containing a link to the map position you wrangled in your project, a short description of the area and a reason for your choice.

ProjectFiles/osm/sample.osm
An .osm file containing a sample part of the map region you used (around 1 - 10 MB in size).

references.txt
A text file containing a list of Web sites, books, forums, blog posts, github repositories etc that you referred to or used in this submission (Add N/A if you did not use such resources).

-------------------------------------------------------------------------------------------------------------------------



******************  MONGO IMPORT ****************************

C:\mongodb24\mongodb-win32-x86_64-2008plus-2.4.3\bin>mongoimport -d osm -c nyny --file C:\Users\Kathleen\Documents\udacity\wrangling\osm\new-york_new-york.osm.json

...
Sun Nov 13 22:47:16.005                 Progress: 2586676224/2621841121 98%
Sun Nov 13 22:47:16.005                         10880200        9411/second
Sun Nov 13 22:47:19.002                 Progress: 2595949478/2621841121 99%
Sun Nov 13 22:47:19.002                         10908500        9411/second
Sun Nov 13 22:47:22.005                 Progress: 2605725814/2621841121 99%
Sun Nov 13 22:47:22.005                         10936400        9411/second
Sun Nov 13 22:47:23.601 check 9 10951297
Sun Nov 13 22:47:23.639 imported 10951297 objects