var map;

electricity_mixes = {
  'SFPUC': 0.08,
  'US': 0.506,
  'CA': 0.287,
  'NGCC': 0.395,
  'Coal': 1.1,
  'Lignin': 0.01,
  'WECC': 0.48,
  'MRO': 0.81,
  'SPP': 0.85,
  'TRE': 0.59,
  'SERC': 0.63,
  'RFC': 0.69,
  'NPCC': 0.31,
  'FRCC': 0.54,
  'Custom': 0.506
}

function electricitymixSelect() {
  var myList=document.getElementById("myList");
  var electricity_region = myList.options[myList.selectedIndex].value;
  var electricity_GHG = electricity_mixes[electricity_region];
  set_value = document.getElementById("custom_mix_value");
  set_value.value = electricity_GHG;
  return electricity_GHG
}


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
], {name: 'Grayscale'});

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


var image = {
        url: '/static/images/dot.png',
        scaledSize: new google.maps.Size(10, 10),     
    }; 

var metric = 'energy';

var controlTextCost = document.getElementById('controlTextCost');
var controlUICost = document.getElementById('controlUICost');
	controlUICost.appendChild(controlTextCost);
	controlUICost.addEventListener('click', function() {
		controlTextCost.style['font-weight'] = 'bold';
		controlTextEnergy.style['font-weight'] = 'normal';
		controlTextGHG.style['font-weight'] = 'normal';
		metric = 'cost';
		return metric
}); 
	controlUICost.addEventListener('mouseover', function() {
		controlUICost.style['background-color'] = '#efefef';
	});
	controlUICost.addEventListener('mouseout', function() {
		controlUICost.style['background-color'] = '#fff';
	});

var controlTextEnergy = document.getElementById('controlTextEnergy');
var controlUIEnergy = document.getElementById('controlUIEnergy');
	controlUIEnergy.appendChild(controlTextEnergy);
	controlUIEnergy.addEventListener('click', function() {
		controlTextEnergy.style['font-weight'] = 'bold';
		controlTextCost.style['font-weight'] = 'normal';
		controlTextGHG.style['font-weight'] = 'normal';
		metric = 'energy';
		return metric
}); 
	controlUIEnergy.addEventListener('mouseover', function() {
		controlUIEnergy.style['background-color'] = '#efefef';
	});
	controlUIEnergy.addEventListener('mouseout', function() {
		controlUIEnergy.style['background-color'] = '#fff';
	});

var controlTextGHG = document.getElementById('controlTextGHG');
var controlUIGHG = document.getElementById('controlUIGHG');
	controlUIGHG.appendChild(controlTextGHG);
	controlUIGHG.addEventListener('click', function() {
		controlTextGHG.style['font-weight'] = 'bold';
		controlTextCost.style['font-weight'] = 'normal';
		controlTextEnergy.style['font-weight'] = 'normal';
		metric = 'GHG';
		return metric
}); 
	controlUIGHG.addEventListener('mouseover', function() {
		controlUIGHG.style['background-color'] = '#efefef';
	});
	controlUIGHG.addEventListener('mouseout', function() {
		controlUIGHG.style['background-color'] = '#fff';
	});


var a = 7;
var b = -0.18;
var c = 0;
var d = 0;
var direct = 0;
var electricity_GHG_val = electricitymixSelect()

document.getElementById("value_a").onchange = function() {
    a = document.getElementById("value_a").value;
    return a
}
document.getElementById("value_b").onchange = function() {
    b = document.getElementById("value_b").value;
    return b
}
document.getElementById("value_c").onchange = function() {
    c = document.getElementById("value_c").value;
    return c
}
document.getElementById("value_d").onchange = function() {
    d = document.getElementById("value_d").value;
    return d
}

document.getElementById("direct_val").onchange = function() {
    direct = document.getElementById("direct_val").value;
    return direct
}

document.getElementById("custom_mix_value").onchange = function() {
    electricity_GHG_val = document.getElementById("custom_mix_value").value;
    return electricity_GHG_val
}

document.getElementById("myList").onchange = function() {
    electricity_GHG_val = electricitymixSelect()
    return electricity_GHG_val
}


	google.maps.event.addListener(map, 'click', function(event) {
		placeMarker(event.latLng);
		var place_lat_lon = event.latLng
		$('#img').show(); 
		$('#img2').show();
		$.getJSON("/lat_lng", {
			lat: event.latLng.lat(),
			lng: event.latLng.lng(),
			metric: metric,
			a: a,
			b: b,
			c: c,
			d: d,
			direct: direct,
      electricity_GHG: electricity_GHG_val
		}, function(data) {
			map.data.addGeoJson(data);


			map.data.setStyle(function(feature) {
				var color = '#42e2f4';
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

			var results_text = "<br /><u>Cluster " + i +"</u> (" + metric + ")<br />Houses: " + data.features[1].properties.houses + "<br />Population: " + data.features[1].properties.population+ "<br />";
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
        
        map.controls[google.maps.ControlPosition.TOP_CENTER].push(controlUIEnergy);
		map.controls[google.maps.ControlPosition.TOP_CENTER].push(controlUICost);
		map.controls[google.maps.ControlPosition.TOP_CENTER].push(controlUIGHG);
		
		map.mapTypes.set('styled_map', styledMapType);
        map.setMapTypeId('roadmap');
}
