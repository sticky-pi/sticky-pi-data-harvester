
function n(n){
    return n > 9 ? "" + n: "0" + n;
}

function secs_to_dhms(s){
    var seconds = parseInt(s, 10);

    var days = Math.floor(seconds / (3600*24));
    seconds  -= days*3600*24;
    var hrs   = Math.floor(seconds / 3600);
    seconds  -= hrs*3600;
    var mnts = Math.floor(seconds / 60);
    seconds  -= mnts*60;
    return days+"d" + n(hrs) + ":" + n(mnts) + ":" + n(seconds) + " ago";
}


function secs_to_human_durations(s){
    var seconds = parseInt(s, 10);
    var days = Math.floor(seconds / (3600*24));
    var hrs   = Math.floor(seconds / 3600);
    var mnts = Math.floor(seconds / 60);

    if(days >= 2){
        return days + " d ago"
    }
    if(hrs >= 2){
        return hrs + " h ago"
    }
    if(mnts >= 2){
        return mnts + " min ago"
    }
    return seconds + " s ago"
}

function timeConverter(UNIX_timestamp){
  var a = new Date(UNIX_timestamp * 1000);
  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var year = a.getFullYear();
  var month = months[a.getMonth()];
  var date = a.getDate();
  var hour = a.getHours();
  var min = a.getMinutes() < 10 ? '0' + a.getMinutes():  a.getMinutes();
  var sec = a.getSeconds() < 10 ? '0' + a.getSeconds():  a.getSeconds();
  var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;

  return time; //+ " (" + a.toISOString() +")";
}
//function timeConverter(UNIX_timestamp){
//  var a = new Date(UNIX_timestamp * 1000);
//  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
//  var year = a.getFullYear();
//  var month = months[a.getMonth()];
//  var date = a.getDate();
//  var hour = a.getHours();
//  var min = a.getMinutes() < 10 ? '0' + a.getMinutes():  a.getMinutes();
//  var sec = a.getSeconds() < 10 ? '0' + a.getSeconds():  a.getSeconds();
//  var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
//
//  return time + " (" + a.toISOString() +")";
//}
//console.log(timeConverter(0));
$(document).ready( function () {
//    console.log("test")

    var mymap = L.map('mapid').setView([51.505, -0.09], 3);

    var marker = L.marker([0,0]).addTo(mymap);
    var table = $('#devices').DataTable({
        "ajax": {   "url": "status",
                    "dataSrc" : function (json) {
//                        console.log(json);
                        date = timeConverter(json.time);
                        $("#harvester_time").html(date)
//                        console.log(json);
                        coords = json.gps_coordinates;
                        if(coords["lat"] === null){
                            $("#mapid").hide()
                            $("#harvester_gps").html("<b>unavailable!</b>");
                        }

                        else{

                            $("#mapid").show()
    //                        console.log(Math.round(json.time - coords["time"]));
                            gps_str = "Lat = " + coords["lat"] + ", Lng = " + coords["lng"] +
                                                     "<br>("+ Math.round(json.time - coords["time"]) + " s ago).";
                            if(coords["lat"]){
                                mymap.setView([coords["lat"], coords["lng"]]);
                                marker.setLatLng([coords["lat"], coords["lng"]]).update();
                                }

                            $("#harvester_gps").html(gps_str);
                        }
                        $("#harvester_disk").html(
                                        json.n_local_images +" images synced. " +
                                        Math.round(100 * json.disk_info["used"]/json.disk_info["total"]) + "% used");
                        out = json.devices;

                        now = Math.floor(Date.now() / 1000)
                        for (d in out){
                            out[d]['progress'] = "<i class='bi bi-download'></i> " + out[d].progress_uploading + "/" + out[d].progress_to_upload +
//                            + "<br>" +
                                                 " | <i class='bi bi-hand-thumbs-up'></i> "  + out[d].progress_skipping +
//                                                  + "/" + out[d].progress_to_skip +"<br>"+
                                                 " | <i class='bi bi-x-octagon-fill'></i> "    + out[d].progress_errors;

                            incomplete = out[d].progress_uploading + out[d].progress_skipping !=  out[d].progress_to_upload + out[d].progress_to_skip;
                            done = out[d]['status'] == "done";
                            out[d]['status'] = (out[d]['in_transaction'] == 1) ? "<i class='bi bi-arrow-clockwise' style='font-size: 2rem;'></i>" : "<i class='bi bi-check-all' style='font-size: 2rem;'></i>";
                            if(incomplete & done){
                                out[d]['status'] = "<i class='bi bi-x-square-fill' style='font-size: 2rem; color: red;'></i>"
                            }

                            out[d]['last_update'] = secs_to_human_durations(now - Math.floor(out[d].updated_time));
                            out[d]['status_progress'] =  out[d]['status'] + " ("+
                                                         out[d]['progress'] + ")<br>" +
                                                        out[d]['last_update']
                            console.log(out[d]['status_progress'])

                            out[d]['available_disk_space'] = out[d]['available_disk_space'] + "%"
//                            console.log(out[d]['last_image_thumbnail_path']);
                            last_img_timestamp = out[d]['last_image_timestamp']
                            out[d]['last_image'] = {"url": "static/sticky_pi_data/"+ out[d]['last_image_thumbnail_path'],
                                                     "timestamp": last_img_timestamp}
                        }

                        return out;
                    }},
            "columns":[
                {"data":"id", 'title': 'Device'},
                {"data":"status_progress", 'title': 'Data transfer'},
//                {"data":"last_update", 'title': 'Last connection'},
                {"data":"last_image", 'title': 'Last image'},
                {"data":"available_disk_space", 'title': 'Disk left'},
                {"data":"ip", 'title': 'IP addr.'},
                ],
             "columnDefs": [{ "targets": 2,
                              "render": function(data) {

                                now = Math.floor(Date.now() / 1000);
                                last_image_duration = secs_to_human_durations(now - Math.floor(out[d].updated_time));

                                return '<img class="last-image" src="'+data["url"]+'"><br>' + last_image_duration
                              }
                                 }],
            "rowCallback": function( row, data, index ) {
                if ( data["status"] === "syncing" ){
                        $('td', row).addClass("syncing-row");
                    }
                else if ( data["status"] === "done" ){
                        $('td', row).addClass("done-row");
                    }
                else{
                    $('td', row).addClass("error-row");
                }

                },
            "paging": false
        });


    setInterval( function () {
        table.ajax.reload( null, false ); // user paging is not reset on reload
    }, 1000 );


//    $.ajax({
//    dataType: "json",
//    url: "static/world.geo.json",
//    success: function(data) {
//        console.log(data);
//        var myCustomStyle = {
//            stroke: true,
//            fill: false,
//            fillColor: '#fff',
//            fillOpacity: 1
//        }
//        L.geoJson(data, {
//                        clickable: false,
//                        style: myCustomStyle
//                    }).addTo(mymap);
//        }
//    });

    L.tileLayer('osm_tile/{z}/{x}/{y}.png', {
                maxZoom: 18,
                attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
                id: 'base'
            }
        ).addTo(mymap);

} );