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
			
			//var html = "<ul><li>Houses: " + data.properties.houses + "</li><li>Population: " + data.properties.population + "</li><li>index: " + data.properties.index + "</li></ul>";
			var infowindow = new google.maps.InfoWindow();

			$('#img').hide();
			$('#img2').hide();

  			// When the user clicks, open an infowindow
			map.data.addListener('mouseover', function(event) {
				index = event.feature.getProperty("index");
				floors = event.feature.getProperty("num_floor");
				sum_pop = Math.ceil(event.feature.getProperty("SUM_pop"));
				total_pop = event.feature.getProperty("population");
				total_buildings = event.feature.getProperty("houses");
				accept = event.feature.getProperty("accept");
				var html = "<ul><b><font size="+ 3 + ">Total Population: " + total_pop + "<br />Total Buildings: " + total_buildings + "</font></b></li><li>floors: " + floors + "</li><li>Building_Pop: " + sum_pop + "</li></ul>";
      			infowindow.setContent(html);
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
        map.controls[google.maps.ControlPosition.RIGHT_TOP].push(legend);

      }
