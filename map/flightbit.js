mapboxgl.accessToken = 'pk.eyJ1IjoidGhvbWFzdmR2IiwiYSI6Ijk3M2Y1OWI0YmIyZDVjNWRhZmRiMzEzYTNiMjdhYjJiIn0.wmpaRiLCFUi8qRNLVrQsgg';

var bounds = [
    [-124.7844079, 24.7433195], // Southwest coordinates
    [-66.9513812, 49.3457868]  // Northeast coordinates
];

var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/thomasvdv/cj2kmlplu00162sozarhcw2ri',
    center: [-122.1521, 48.1631], // starting position
    zoom: 8, // starting zoom
    maxBounds: bounds // Restrict to USA
});

var toggleableLayerIds = [ 'tmp', 'dpt' ];

var hour = 6;
var a_fcst = 'tmp';

var hours = [
    '9 am',
    '10 am',
    '11 am',
    '12 am',
    '1 pm',
    '2 pm',
    '3 pm',
    '4 pm',
    '5 pm',
    '6 pm',
    '7 pm',
    '8 pm',
    '9 pm'
];

function filterBy(hour) {

    // TODO: Switch the layer here
     // Hide the current layer
    for (var j = 0; j < toggleableLayerIds.length; j++) {
        var id = toggleableLayerIds[j];
        for (var t = 1; t < 13; t++) {
            map.setPaintProperty(a_fcst + '_' + t, 'raster-opacity', 0);
        }
    }
    map.setPaintProperty(a_fcst + '_' + hour, 'raster-opacity', 0.5);
    this.hour = hour

    // Set the label to the hour
    document.getElementById('hour').textContent = hours[hour];
}


map.on('load', function () {
    for (var i = 0; i < toggleableLayerIds.length; i++) {
        var id = toggleableLayerIds[i];
        for (var t = 1; t < 13; t++) {
            var src = id + '_' + t
            map.addSource(src, {
                type: 'raster',
                url: 'mapbox://thomasvdv.' + src
            });
            map.addLayer({
                'id': src,
                'type': 'raster',
                'source': src,
                'layout': {
                    'visibility': 'visible'
                },
                'paint': {
                    'raster-opacity': 0
                },
                'source-layer': src
            },'water');
        }
    }
    // Set filter to first month of the year
    // 0 = January
    filterBy(hour);

    document.getElementById('slider').addEventListener('input', function(e) {
        var hour = parseInt(e.target.value, 10);
        filterBy(hour);
    });
});

map.addControl(new mapboxgl.NavigationControl());
map.addControl(new mapboxgl.GeolocateControl());

for (var i = 0; i < toggleableLayerIds.length; i++) {
    var id = toggleableLayerIds[i];

    var link = document.createElement('a');
    link.href = '#';
    link.className = '';
    link.textContent = id;

    link.onclick = function (e) {
        var clickedLayer = this.textContent;
        e.preventDefault();
        e.stopPropagation();

        // Hide the current layer
        for (var j = 0; j < toggleableLayerIds.length; j++) {
            var id = toggleableLayerIds[j];
            for (var t = 1; t < 13; t++) {
                map.setPaintProperty(a_fcst + '_' + t, 'raster-opacity', 0);
            }
        }

        // Reset the bottons state
        var buttons = document.getElementById('menu').childNodes;
        for (var k = 0; k < buttons.length; k++) {
            buttons[k].className = '';
        }

        var opacity = map.getPaintProperty(clickedLayer + '_' + hour, 'raster-opacity');

        if (opacity > 0) {
            map.setPaintProperty(clickedLayer, 'raster-opacity', 0);
            this.className = '';
        } else {
            this.className = 'active';
            map.setPaintProperty(clickedLayer + '_' + hour, 'raster-opacity', 0.5);
            a_fcst = clickedLayer.split('_')[0]
        }
    };

    var layers = document.getElementById('menu');
    layers.appendChild(link);
}
