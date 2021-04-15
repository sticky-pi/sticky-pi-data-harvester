
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

  return time + " (" + a.toISOString() +")";
}
//console.log(timeConverter(0));
$(document).ready( function () {
//    console.log("test")
    var table = $('#devices').DataTable({
        "ajax": {   "url": "status",
                    "dataSrc" : function (json) {
                        date = timeConverter(json.time);
                        $("#harvester_time").html(date)
                        console.log(json);
                        coords = json.gps_coordinates;
                        console.log(Math.round(json.time - coords["time"]));
                        gps_str = "Lat = " + coords["lat"] + ", Lng = " + coords["lng"] + " (Alt = " + coords["alt"] + "m)." +
                                                 " Updated "+ Math.round(json.time - coords["time"]) + " s ago.";

                        $("#harvester_gps").html(gps_str);
                        $("#harvester_disk").html(
                                        json.n_local_images +" images synced. " +
                                        Math.round(100 * json.disk_info["used"]/json.disk_info["total"]) + "% used");
                        out = json.devices;

                        now = Math.floor(Date.now() / 1000)
                        for (d in out){
                            out[d]['progress'] = out[d].progress_uploading + "/" + out[d].progress_to_upload +
                                                  " (skipped: " + out[d].progress_skipping + "/" + out[d].progress_to_skip + ")";
                            incomplete = out[d].progress_uploading + out[d].progress_skipping !=  out[d].progress_to_upload + out[d].progress_to_skip;
                            out[d]['status'] = (out[d]['in_transaction'] == 1) ? "syncing" : "done";
                            if(incomplete & out[d]['status'] == "done"){
                                out[d]['status'] = "incomplete!"
                            }

                            out[d]['last_update'] = secs_to_dhms(now - Math.floor(out[d].updated_time))
                        }
                        return out;
                    }},
        "columns":[
            {"data":"id", 'title': 'Device'},
            {"data":"ip", 'title': 'IP address'},
            {"data":"last_update", 'title': 'Last connection'},
            {"data":"status", 'title': 'Status'},
            {"data":"progress", 'title': 'Uploaded'},
            ]
        });


    setInterval( function () {
        table.ajax.reload( null, false ); // user paging is not reset on reload
    }, 1000 );
    var mymap = L.map('mapid').setView([51.505, -0.09], 13);
    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'your.mapbox.access.token'
}).addTo(mymap);
} );