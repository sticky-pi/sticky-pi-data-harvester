
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

    var device_map = {};
    $.getJSON('static/device_map.json', function() {
        console.log( "success" );
        })
      .done(function(data) {
        console.log( "second success" );

        for(d in data){
            device_map[d] = data[d];
            }

      })
      .fail(function() {
        console.log( "error" );
      })

    var mymap = L.map('mapid').setView([51.505, -0.09], 3);

    var marker = L.marker([0,0]).addTo(mymap);
    var table = $('#devices').DataTable({
        "ajax": {   "url": "status",
                    "dataSrc" : function (json) {
                        date = timeConverter(json.time);
                        $("#harvester_time").html(date)
                        $("#harvester_core_temp").html(json.core_temperature)

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


                      $("#uploader_n_images").html(json.n_local_images);
                      $("#uploader_connection_status").html(json.cloud_uploader["connection_status"]);
                      $("#uploader_upload_status").html(json.cloud_uploader["upload_status"]);

                      log_text = json.cloud_uploader["logs"];
                      if (typeof log_text !== 'undefined' && log_text){
                        log_text = log_text.replace(/\n/g, "<br />");
                        $(".uploader_logs").html(log_text);
                        $('.uploader_logs').scrollTop($('.uploader_logs')[0].scrollHeight);
                      }
                      else{
                        log_text = "";
                      }

                        now = Math.floor(Date.now() / 1000);

                        for (d in out){
                            if(device_map[out[d]['id']])
                                out[d]["device_name"] = device_map[out[d]['id']];
                            else
                                out[d]["device_name"] = "undefined";

                            out[d]['progress'] = "<i class='bi bi-download'></i>&nbsp" + out[d].progress_uploading + "/" + out[d].progress_to_upload +
                                                 " | <i class='bi bi-hand-thumbs-up'></i>&nbsp"  + out[d].progress_skipping +
                                                 " | <i class='bi bi-x-octagon-fill'></i>&nbsp"    + out[d].progress_errors;

                            done = out[d].progress_uploading + out[d].progress_skipping ==  out[d].progress_to_upload + out[d].progress_to_skip;
                            error = out[d].progress_errors > 0;

                            out[d]['status_text'] = (out[d]['in_transaction'] == 1) ?
                                            "<i class='bi bi-arrow-clockwise' style='font-size: 2rem;'></i>" :
                                            "<i class='bi bi-check-all' style='font-size: 2rem;'></i>";
                            if(out[d]['in_transaction'] == 1){
                                out[d]['status_text'] = "<i class='bi bi-arrow-clockwise' style='font-size: 2rem;'></i>";
                                out[d]['status'] = "syncing"
                            }
                            else if(error || !done){
                                out[d]['status_text'] = "<i class='bi bi-x-square-fill' style='font-size: 2rem; color: red;'></i>";
                                out[d]['status'] = "error"
                            }
                            else{
                                out[d]['status_text'] = "<i class='bi bi-check-all' style='font-size: 2rem;'></i>";
                                out[d]['status'] = "done"
                            }


                            out[d]['last_update_human'] = secs_to_human_durations(now - Math.floor(out[d].updated_time));
                            out[d]['status_progress'] =  out[d]['status_text'] + " ("+
                                                         out[d]['progress'] + ")<br>" +
                                                        out[d]['last_update_human']

                            out[d]['device_str'] = "<a target='_blank'  rel='noopener noreferrer'   href='static/sticky_pi_data/images/" + out[d]['id'] + "/sticky_pi.log'"+ ">"+ out[d]['id'] + "</a>"
                            out[d]['available_disk_space'] = out[d]['available_disk_space'] + "%"
                            last_img_timestamp = out[d]['last_image_timestamp']
                            out[d]['last_image'] = {"url": "static/sticky_pi_data/images/"+ out[d]['last_image_thumbnail_path'],
                                                     "timestamp": last_img_timestamp}
                        }

                        return out;
                    }},
            "columns":[
                {"data":"device_str", 'title': 'Device'},
                {"data":"device_name", 'title': 'Name'},
                {"data":"status_progress", 'title': 'Data transfer'},
                {"data":"last_image", 'title': 'Last image'},
                {"data":"available_disk_space", 'title': 'Disk left'},
                {"data":"ip", 'title': 'IP addr.'},
                {"data":"updated_time", 'title': 'Last update'},
                {"data":"status", 'title': 'Status'},
                ],
             "order":[6, 'desc'],
             "columnDefs": [
             { "targets": 3,
                              "render": function(data) {
                                now = Math.floor(Date.now() / 1000);
                                last_image_duration = secs_to_human_durations(now - Math.floor(data['timestamp']));
                                out =  '<div class="thumbnail_container">' +
                                            '<a target="_blank"  rel="noopener noreferrer" href = "' +  data["url"].split('.').slice(0, -1).join('.') + '"><img class="last_image_thumbnail" src="'+data["url"]+'"></a>'+
                                            '<div class="text_in_thumbnail_bg"><div class="text_in_thumbnail">' +
                                                last_image_duration +
                                             '</div></div>' +
                                             '</div>';
//                                console.log(out);
                                return out;

                              }
                                 }
                                 ,
                                 { "targets": 6,
                                    "visible": false,
                                    "searchable": false
                                    }
                                 ],
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
            "paging": false,
            "searching": false
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
console.log("doc not ready")