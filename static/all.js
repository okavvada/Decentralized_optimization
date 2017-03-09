var map;

function initMap() {
	var styledMapType = new google.maps.StyledMapType(
	[
  {
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#f5f5f5"
      }
    ]
  },
  {
    "elementType": "labels.icon",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#616161"
      }
    ]
  },
  {
    "elementType": "labels.text.stroke",
    "stylers": [
      {
        "color": "#f5f5f5"
      }
    ]
  },
  {
    "featureType": "administrative.land_parcel",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#bdbdbd"
      }
    ]
  },
  {
    "featureType": "poi",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#eeeeee"
      }
    ]
  },
  {
    "featureType": "poi",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#757575"
      }
    ]
  },
  {
    "featureType": "poi.park",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#e5e5e5"
      }
    ]
  },
  {
    "featureType": "poi.park",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#9e9e9e"
      }
    ]
  },
  {
    "featureType": "road",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#ffffff"
      }
    ]
  },
  {
    "featureType": "road.arterial",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#757575"
      }
    ]
  },
  {
    "featureType": "road.highway",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#dadada"
      }
    ]
  },
  {
    "featureType": "road.highway",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#616161"
      }
    ]
  },
  {
    "featureType": "road.local",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#9e9e9e"
      }
    ]
  },
  {
    "featureType": "transit.line",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#e5e5e5"
      }
    ]
  },
  {
    "featureType": "transit.station",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#eeeeee"
      }
    ]
  },
  {
    "featureType": "water",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#c9c9c9"
      }
    ]
  },
  {
    "featureType": "water",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#9e9e9e"
      }
    ]
  }
], {name: 'Styled Map'});

	map = new google.maps.Map(document.getElementById('map'), {
		center: {
			lat: 37.750893,
			lng: -122.443439
		},
		zoom: 13, 
		mapTypeControlOptions: {
            mapTypeIds: ['roadmap', 'satellite', 'hybrid', 'terrain',
                    'styled_map']
          }		
	});

var i = 0;

	function placeMarker(location) {
    var marker = new google.maps.Marker({
        position: location, 
        icon: "http://maps.google.com/mapfiles/ms/icons/green-dot.png",
        map: map
    });
}

	function get_pop(feature){
		var pop = feature.getProperty('population');
	  	return pop
	};

	function get_houses(feature){
		var house = feature.getProperty('houses');
	  	return house
	};


var image = {
        url: '/static/images/dot.png',
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
				var color = '#6f786a';
				var myscale =  4;
			          if (feature.getProperty('accept') == 'yes') {
			            color = '#f00';
			            myscale =  8;
			          }
			          else if (feature.getProperty('accept') == 'no') {
			            color = '#000';
			            myscale =  7;
			          }
			          return ({
			            icon: { 
			  	path: google.maps.SymbolPath.CIRCLE, 
			  	strokeWeight: 0.5,
            	strokeColor: color,
			  	scale: myscale,
			  	fillColor: color,
			  	fillOpacity: 0.6
			  }
			        });

			      });

			var results_text = "<br /><u>Cluster " + i +"</u><br />Houses: " + data.features[1].properties.houses + "<br />Population: " + data.features[1].properties.population+ "<br />";
  			var results = document.getElementById('results');
			results.style.fontSize = "14px";
			var div = document.createElement('div');
			div.innerHTML = results_text;
			results.appendChild(div);

			var infowindow = new google.maps.InfoWindow();

			$('#img').hide();
			$('#img2').hide();

  			// When the user hovers, open an infowindow
			map.data.addListener('mouseover', function(event) {
				index = event.feature.getProperty("index");
				floors = event.feature.getProperty("num_floor");
				sum_pop_residential = Math.ceil(event.feature.getProperty("SUM_pop_residential"));
				sum_pop_commercial = Math.ceil(event.feature.getProperty("SUM_pop_commercial"));
				total_pop = event.feature.getProperty("population");
				total_buildings = event.feature.getProperty("houses");
				var html = "<u>Cluster " + i +"</u><br />floors: " + floors + "<br />Residential_Pop: " + sum_pop_residential + "<br />Commercial_Pop: " + sum_pop_commercial;
      			infowindow.setContent(html);
      			infowindow.setPosition(event.latLng);
      			infowindow.setOptions({disableAutoPan: true});
      			infowindow.open(map);
  			});

  			map.data.addListener('mouseout', function(event) {
  				infowindow.close();
  			})

		}) 

		i +=1;
	}); 

	var icons = {
        redDot: {
            name: 'connected building',
            icon: '/static/images/reddot.png'
        },
        greyDot: {
            name: 'unconnected building',
            icon: '/static/images/blackdot.png'
        },
        blackDot: {
            name: 'unassessed building',
            icon: '/static/images/greydot.png'
        }
        };

		var legend = document.getElementById('legend');
		legend.style.fontSize = "14px";
	    for (var key in icons) {
	      var type = icons[key];
	      var name = type.name;
	      var icon = type.icon;
	      var div = document.createElement('div');
	      div.innerHTML = '<img src="' + icon + '"> ' + name;
	      legend.appendChild(div);

    }

        map.controls[google.maps.ControlPosition.TOP_RIGHT].push(legend);
        map.controls[google.maps.ControlPosition.RIGHT_TOP].push(results);
		
		map.mapTypes.set('styled_map', styledMapType);
        map.setMapTypeId('styled_map');
      }
