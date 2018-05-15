How/Where do I get geoJSON data for states, provinces, and administrative regions of non-US countries?
There is a good writeup on how to generate geoJSON from shapefiles here
http://vallandingham.me/shapefile_to_geojson.html

The steps below should take you from start to finish:

Install the Quantum GIS framework http://www.qgis.org/e/qgis.
If you are on Mac OS X, you can use this version http://www.kyngchaos.com/software
This will give you the ogr2ogr utility used for converting shapefiles to geoJSON
Download the shapefiles for your country from here http://www.gadm.org/country and unzip
For Canada, and possibly other countries, the shapefile with suffix 0 is for the country boundary and the suffix 1 is for the internal regions. Not sure if this naming is consistent across countries.
Upload the region level shapefile to MapShaper http://mapshaper.com/test/MapShaper.swf
You can skip this step if you don't care to optimize the size of your resulting geoJSON
Set the 'simplification level' slider in MapShaper to the desired level and export the simplified shapefile as 'Shapefile - Polygons'
Download .shp and .shx file to the local directory where you unzipped the original shapefiiles, replace the original files with the simplified ones.
Navigate to the local directory and run the command below, replacing <shapefile> with the actual name of the shapefile you want to convert.

ogr2ogr -f geoJSON regions.json <shapefile>.shp
You should now have the regions for your country in geoJSON format. Check to make sure there are paths defined in regions.json and that property fields were maintained (ex. region name).
---------------------------
---------------------------
This process is now simplified (July 2014) compared to the steps I see in the accepted answer. It now seems much easier to get this data. I at first floundered around the web hoping I could just download a bunch of standard maps in GeoJSON format, but came up empty other than standard US/Canada offerings. As of right now there doesn't seem to be a lot available in straight GeoJSON. Instead you take an older, widely used format to generate GeoJSON. This is easy, and a good path to take. We'll be working with shape files and converting them to GeoJSON.

First download a shape file for the geographic area you are interested in. A shapefile is a digital vector storage format for storing geometric location and associated attribute information. (http://en.wikipedia.org/wiki/Shapefile)

There are lots of sources of these. These are sources I found useful:

GADM - Download data by country or one giant file for the world. Each zip you download has multiple shape files inside starting at number 0 and increasing. The higher the number the higher the detail level. Like country, state, county, etc. (http://www.gadm.org/country)

Another download site (http://www.naturalearthdata.com/downloads/)

Download US State, County, Sub-County data as driven by the census bureau - http://census.ire.org/data/bulkdata.html
Once you have your shape file, drag and drop it into the webpage at http://www.mapshaper.org. Here you can drag a slider to change the vector resolution. My experience was that 10% resolution looked great still for web maps, 25% was near perfect. File size was greatly reduced, so I would recommend using it. My Massachusetts map went from 800kb of GeoJSON data to 80kb after reducing resolution.
Click the GeoJSON button on mapshaper and the file is automatically exported for you.
Optional - Once you have a shape file, you can edit it for free in a tool like Quantum GIS (QGIS).

You can also hand map GeoJSON data at this website. http://geojson.io/#map=2/20.0/0.0