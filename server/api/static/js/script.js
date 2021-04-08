
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
$(document).ready( function () {
    console.log("test")
    var table = $('#devices').DataTable({
        "ajax": {   "url": "status",
                    "dataSrc" : function (json) {
                        out = json.devices;
                        console.log(json)
                        now = Math.floor(Date.now() / 1000)
                        for (d in out){
                            out[d]['progress'] = out[d].progress_uploading + "/" + out[d].progress_to_upload +
                                                  " (skipped: " + out[d].progress_skipping + "/" + out[d].progress_to_skip + ")";
                            out[d]['status'] = (out[d]['in_transaction'] == 1) ? "syncing" : "done";
                            out[d]['last_update'] = secs_to_dhms(now - Math.floor(out[d].updated_time))
                        }

                        console.log(out)
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

} );