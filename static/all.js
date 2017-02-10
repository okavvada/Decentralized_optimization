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
        icon: "http://maps.google.com/mapfiles/ms/icons/green-dot.png",
        map: map
    });
}


var image = {
        url: '/static/images/dot.png', // image is 512 x 512
        scaledSize: new google.maps.Size(10, 10),     
    }; 

	google.maps.event.addListener(map, 'click', function(event) {
		placeMarker(event.latLng);
		var place_lat_lon = event.latLng
		$('#img').show(); 
		$('#img2').show();
		$.getJSON("/lat_lng", {
			lat: event.latLng.lat(),
			lng: event.latLng.lng()
		}, function(data) {
			map.data.addGeoJson(data);

			map.data.setStyle(function(feature) {
				var color = '#000';
				var myscale =  4;
			          if (feature.getProperty('accept') == 'yes') {
			            color = '#f00';
			            myscale =  8;
			          }
			          return ({
			            icon: { 
			  	path: google.maps.SymbolPath.CIRCLE, 
			  	strokeWeight: 0.5,
            	strokeColor: color,
			  	scale: myscale,
			  	fillColor: color,
			  	fillOpacity: 0.5
			  }
			        });
			      });

			//map.data.addGeoJson(data);
			
			//var html = "<ul><li>Houses: " + data.properties.houses + "</li><li>Population: " + data.properties.population + "</li><li>index: " + data.properties.index + "</li></ul>";
			var infowindow = new google.maps.InfoWindow();

			$('#img').hide();
			$('#img2').hide();
			//var contentString = html

  			// When the user clicks, open an infowindow
			map.data.addListener('mouseover', function(event) {
				index = event.feature.getProperty("index");
				floors = event.feature.getProperty("num_floor");
				sum_pop = event.feature.getProperty("SUM_pop");
				total_pop = event.feature.getProperty("population");
				total_buildings = event.feature.getProperty("houses");
				//energy = event.feature.getProperty("energy");
				accept = event.feature.getProperty("accept");
				var html = "<ul><b>Total Population: " + total_pop + "<br />Total Buildings: " + total_buildings + "</b><br /><li>index: " + index + "</li><li>floors: " + floors + "</li><li>Building_Pop: " + sum_pop + "</li></ul>";
				var contentString = html
      			infowindow.setContent(contentString);
      			infowindow.setPosition(event.latLng);
      			//infowindow.setOptions({pixelOffset: new google.maps.Size(10,10)});
      			infowindow.setOptions({disableAutoPan: true});
      			infowindow.open(map);
  			});
  			map.data.addListener('mouseout', function(event) {
  				infowindow.close();
  			}) 

		}) 
	}); 
}