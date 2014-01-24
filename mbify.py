#!/usr/bin/env python
#
# Test script to create a valid mbtiles file
# At the moment has settings hardcoded to a 'test' folder containing the tree
# 


import sqlite3, os

datafolder = 'test'
format = 'png'
metadata={'name': 'MbifyTest',
          'type' : 'baselayer',
          'version' : '0.1',
          'description' : 'Test tileset from mbify.py',
          'format' : format,
          'bounds' : '12.50861,55.655,12.604289,55.704289' }

conn = sqlite3.connect('test.mbtiles')
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
     
 