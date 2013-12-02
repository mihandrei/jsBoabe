U3 = {};

U3.ajax = function(url, on_done){
    function reqListener () {
      on_done(this.responseText);
    }

    var oReq = new XMLHttpRequest();
    oReq.onload = reqListener;
    oReq.open("get", url, true);
    oReq.send();
}

U3.ajaxes = function(urls, on_done){
    results = [];
    done = 0;

    function make_handler(i){
        return function (resp){
            results[i] = resp;
            done += 1;
            if (done == urls.length){
                on_done(results);
            }
        }
    }

    for (var i = 0; i < urls.length; i++) {
        U3.ajax(urls[i], make_handler(i));
    }
}