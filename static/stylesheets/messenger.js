document.addEventListener("DOMContentLoaded", function(event) {

    var delete_room = document.getElementById('trash_can') != null;
    if(delete_room){
        document.getElementById('trash_can').addEventListener('click', deleteRoom);
    }

    function deleteRoom(){
        console.log(window.location.protocol+'//'
                    + window.location.host +'/home');
        var xhr = new XMLHttpRequest();
        xhr.open("POST", document.getElementById('kill_room').getAttribute('href'), true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function() {
            if (xhr.status === 200 && xhr.responseText !== 'Success') {
                alert('Something went wrong. ' + xhr.responseText);
            }
            else if (xhr.status !== 200) {
                alert('Request failed.  Returned status of ' + xhr.status);
            }
            else {
                console.log('Trying to relocate');
                window.location.href = window.location.protocol+'//'
                    + window.location.host +'/home'
            }
        };

        xhr.send(null);
    }

});

// mdl-button mdl-js-button mdl-button--icon left-offset