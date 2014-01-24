#!/usr/bin/env python
#
# Test script to create a valid mbtiles file
# At the moment has settings hardcoded to a 'test' folder containing the tree
# 


import sqlite3, os
from optparse import OptionParser # optparse-modulet bruges til at tage imod
                                  # parametre fra kommandolinjen

# OptParse set-up
parser = OptionParser(usage="usage: %prog [options] directory output")
parser.add_option("-V", "--version", dest="version", default="1.0", help="Version of dataset")
parser.add_option("-f", "--format", dest="format", default="png", help="Format of dataset (png, jpg)")
parser.add_option("-n", "--name", dest="name", default="", help="Name of dataset")
parser.add_option("-d", "--description", dest="description", default="", help="Description of dataset")
parser.add_option("-b", "--bounds", dest="bounds", default="-180.0,-85,180,85", help="Bounds of dataset in WGS84")
parser.add_option("-a", "--attribution", dest="attribution", default="", help="Attribution string of dataset")

(options, args) = parser.parse_args()

if not args:
    parser.error("No variables specified")

if len(args)<2:
    parser.error("Not enough arguments")

datafolder = args[0]
format = options.format
if not options.name:
    options.name = args[1]
metadata={'name': options.name,
          'type' : 'baselayer', # TODO: Handle different kinds of layers
          'version' : options.version,
          'description' : options.description,
          'format' : options.format,
          'bounds' : options.bounds,
          'attribution': options.attribution }

conn = sqlite3.connect(args[1])
try:
   conn.execute('DROP TABLE metadata')
except:
   pass
try:
   conn.execute('DROP TABLE tiles')
except:
   pass

#Create metadata table
conn.execute('CREATE TABLE metadata (name text, value text);')

#Insert metadata
for k,v in metadata.items():
    conn.execute("INSERT INTO metadata(name,value) VALUES('%s','%s');" % (k,v))

#Create tiles table
conn.execute('CREATE TABLE tiles (zoom_level integer, tile_column integer, tile_row integer, tile_data blob);')
conn.execute('CREATE INDEX tiles_idx ON tiles(zoom_level, tile_column, tile_row);')

for d in os.walk(datafolder):
    parts = d[0].split(os.sep)
    if len(parts) == 3:
        z = int(parts[1])
        x = int(parts[2])
        for f in d[2]:
            fparts = f.split('.')
            if fparts[-1] == format:
                y = int(fparts[0])
                blob = open('%s/%d/%d/%s' % (datafolder,z,x,f),'rb').read()
                conn.execute('INSERT INTO tiles(zoom_level, tile_column, tile_row, tile_data) VALUES(?,?,?,?)',(z,x,y,sqlite3.Binary(blob),))
conn.commit()
conn.close()
     
 