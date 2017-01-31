var map;

function initMap() {
	map = new google.maps.Map(document.getElementById('map'), {
		center: {
			lat: 37.750893,
			lng: -122.443439
		},
		zoom: 13
		
	});


	function placeMarker(location) {
    var marker = new google.maps.Marker({
        position: location, 
        map: map
    });
}

var image = {
        url: '/static/images/dot.png', // image is 512 x 512
        scaledSize: new google.maps.Size(10, 10),     
    }; 

	google.maps.event.addListener(map, 'click', function(event) {
		placeMarker(event.latLng);
		$('#img').show(); 
		$.getJSON("/lat_lng", {
			lat: event.latLng.lat(),
			lng: event.latLng.lng()
		}, function(data) {
			map.data.setStyle({
			  icon: image
			});
			map.data.addGeoJson(data); 
			var html = "<ul><li>Houses: " + data.properties.houses + "</li><li>Population: " + data.properties.population + "</li></ul>";
			var infowindow = new google.maps.InfoWindow();
			$('#img').hide();

  			// When the user clicks, open an infowindow
			map.data.addListener('mouseover', function(event) {
      			infowindow.setContent(html);
      			infowindow.setPosition(event.feature.getGeometry().getAt(0).getAt(0));
      			infowindow.setOptions({pixelOffset: new google.maps.Size(10,10)});
      			infowindow.open(map);
  			});
  			map.data.addListener('mouseout', function(event) {
  				infowindow.close();
  			}) 

		}) 
	}); 
}