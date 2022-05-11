// var url = 'https://data.gov.au/geoserver/vic-local-government-areas-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_bdf92691_c6fe_42b9_a0e2_a4cd716fa811&outputFormat=json';

// fetch(url)
//     .then(response => response.json())
//     .then(json => console.log(json) )

let map, heatmap;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 13,
    center: { lat: 37.775, lng: -122.434 },
  });
  heatmap = new google.maps.visualization.HeatmapLayer({
    data: getPoints(),
    map: map,
  });
}

// Heatmap data: 500 Points
function getPoints() {
  return [
    {location: new google.maps.LatLng(37.782551, -122.445368), weight: 205},
    
  ];
}

window.initMap = initMap;