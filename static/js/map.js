$(function () {

    // custom icons
    // could be more dynamic/dry, but w/e
    const instagram_icon = L.icon.glyph({
        'className': 'material-icons',
        'prefix': '',
        'glyph': 'camera_alt',
        'glyphSize': '24px'
    });
    const inat_icon = L.icon.glyph({
        'className': 'material-icons',
        'prefix': '',
        'glyph': 'search',
        'glyphSize': '24px'
    })
    const me_icon = L.divIcon({ iconSize: [36, 36], className: "me-icon" });

    const data = JSON.parse(document.getElementById('data').innerHTML);

    // TODO: shuold be a bit more dynamic given content, but this'll do for now
    let map = L.map('map').setView([43, -121.3], 6);

    let myTL = L.tileLayer('https://api.mapbox.com/styles/v1/jacobkaplanmoss/cjj50c28o02ve2so59rbgldz1/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiamFjb2JrYXBsYW5tb3NzIiwiYSI6ImNqYnNjbGRrcDB0MmIyd21rbXRzc3V0b3YifQ.4Kz9dKc86l528aaoiegTqA', {
        attribution: 'Maps: Mapbox, OpenStreetMaps. PCT line: Halfmile',
        maxZoom: 14
    });

    myTL.addTo(map);

    if (data.updates) {
        for (let [index, update] of data.updates.entries()) {
            if (update.location) {
                let icon = new L.Icon.Default();
                if (index == 0) {
                    icon = me_icon;
                } else {
                    if (update.type == 'instagrampost') {
                        icon = instagram_icon;
                    } else if (update.type == 'inaturalistobservation') {
                        icon = inat_icon;
                    }
                }

                let m = L.marker(update.location, { icon: icon });
                m.on('click', function (ev) {
                    let elem = $('#' + update.type + '-' + update.pk);

                    // unmark any previously-marked element
                    $(".mark").removeClass('mark');

                    // highlight the new element
                    elem.addClass('mark');

                    // zoom the map in on the point
                    map.flyTo(update.location, 10, { duration: 1.0 });

                    // scroll the page to the new element
                    let elem_offset = elem.offset().top;
                    let elem_height = elem.height();
                    let window_height = $(window).height();
                    let new_top = elem_offset - ((window_height / 2) - (elem_height / 2));
                    $('html, body').animate({ scrollTop: new_top }, 1000);
                })
                m.addTo(map);
            }
        }
    }
});
