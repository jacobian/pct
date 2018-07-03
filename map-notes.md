I made the mapbox tileset I'm using by:

1. downloading the GPX tracks from https://www.pctmap.net/gps-url-loading/

2. striping out the side trails with gpsbabal:

    ```
    $ gpsbabel -i gpx -f CA_Sec_A_tracks.gpx -x track,name="CA Sec A" -o gpx -F CA_Sec_A_only.gpx
    ```

3. joining all the tracks into a single one:

    ```
    $ gpsbabel -i gpx -f CA_Sec_A_only.gpx \
               -i gpx -f CA_Sec_B_only.gpx \
               ...
               -o gpx -F pct-full.gpx
    ```

   I wrote a script to do this, and deleted it because I'm a dummy.

4. Uploaded this as a tileset to mapbox

5. Made a new map style (starting from outdoors), then adding the pct map as a line type.
