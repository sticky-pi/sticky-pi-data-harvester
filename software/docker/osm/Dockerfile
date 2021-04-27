FROM overv/openstreetmap-tile-server

#"https://download.geofabrik.de/north-america/canada/british-columbia-latest.osm.pbf"
# time docker run -v /home/quentin/Desktop/british-columbia-latest.osm.pbf:/data.osm.pbf -v openstreetmap-data:/var/lib/postgresql/12/main docker_harvester_osm import

# Todo import at buildtime!
ARG OSM_DOWNLOAD_URL
ENV DOWNLOAD_PBF=${OSM_DOWNLOAD_URL}.pbf
#ENV DOWNLOAD_POLY=${OSM_DOWNLOAD_URL}.poly

RUN /run.sh import

#COPY british-columbia-latest.osm.pbf /var/lib/postgresql/12/main/british-columbia-latest.osm.pbf
#docker run \
#    -e DOWNLOAD_PBF=https://download.geofabrik.de/north-america/canada/british-columbia-latest.osm.pbf \
#    -e DOWNLOAD_POLY=https://download.geofabrik.de/north-america/canada/british-columbia-latest.osm.poly \
#                      https://download.geofabrik.de/north-america/canada/british-columbia-latest.osm.poly
#    -v openstreetmap-data:/var/lib/postgresql/12/main \
#    overv/openstreetmap-tile-server \
#    import
