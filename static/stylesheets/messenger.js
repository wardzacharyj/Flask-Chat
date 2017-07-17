document.addEventListener("DOMContentLoaded", function(event) {

    var NO_RECENT_MSG = -1;

    var delete_room = document.getElementById('trash_can') != null;
    if(delete_room){
        document.getElementById('trash_can').addEventListener('click', deleteRoom);
    }

    function deleteRoom(){
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

    ////////////////////////////////////////////////////////////////////////////////////////////////

    var roomID = parseInt(window.location.pathname.replace('/room/',''));

    ////////////////////////////////////////////////////////////////////////////////////////////////

    var sender = document.getElementById('btn_send');
    sender.addEventListener('click', sendMessage);


    document.getElementById('message_input').onkeypress = function(e) {
        if (!e) e = window.event;
        var keyCode = e.keyCode || e.which;
        if (keyCode == '13'){
          sendMessage();
          return false;
        }
    };


    var leaveRoom = document.getElementById('leave_room');
    leaveRoom.addEventListener('click', exitRoom);

    ////////////////////////////////////////////////////////////////////////////////////////////////

    function sendMessage(){
        var messageInput = document.getElementById('message_input');

        if(messageInput.value.length > 0){
            var name_object = JSON.stringify({message: messageInput.value});

            var xhr = new XMLHttpRequest();
            xhr.open("POST", '/send/'+roomID, true);
            xhr.setRequestHeader('Content-Type', 'application/json');

            xhr.onload = function() {
                if(xhr.status !== 200){
                    alert('Request failed.  Returned status of ' + xhr.status);
                }
                else if (xhr.textContent === 'Failed') {
                    alert('Room Was Deleted');
                }
            };

            xhr.send(name_object);

            messageInput.value = '';
        }

    }

    ////////////////////////////////////////////////////////////////////////////////////////////////

    if("onhashchange" in window) {
        window.onhashchange = function(){
            window.location.href = window.location.protocol+'//'+window.location.host+'/home'
        }
    }


    function exitRoom(){

        var xhr = new XMLHttpRequest();
        xhr.open("POST", '/exit_room/'+roomID, true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        xhr.onload = function() {
            if(xhr.status !== 200){
                console.log(xhr.textContent);
                alert('Request failed.  Returned status of ' + xhr.status);
            }
            else if (xhr.textContent !== 'Failed') {
                alert('Leaving Room');
                window.location.href = window.location.protocol+'//'+window.location.host+'/home'
            }
        };

        xhr.send(null);

    }


    ////////////////////////////////////////////////////////////////////////////////////////////////


    // Clone and Delete
    var clonedInbound = document.getElementById('temp_inbound').cloneNode(true);
    var clonedOutbound = document.getElementById('temp_outbound').cloneNode(true);

    document.getElementById('message_holder').removeChild(document.getElementById('temp_inbound'));
    document.getElementById('message_holder').removeChild(document.getElementById('temp_outbound'));


    findLatestMessage(NO_RECENT_MSG);

    function findLatestMessage(mostRecentMessageId){
        poll_chat_rooms(mostRecentMessageId, findLatestMessage)
    }


    function poll_chat_rooms(mostRecentMessageId, callback){

        var name_object = JSON.stringify({most_recent_room_id: mostRecentMessageId});
        var xhr = new XMLHttpRequest();

        xhr.open("POST", '/get_messages/'+roomID, true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        xhr.onload = function() {

            console.log(xhr.responseText);

            var raw_response = JSON.parse(xhr.responseText);

            if(xhr.status !== 200){
                alert('Request failed.  Returned status of ' + xhr.status);
            }
            else if (raw_response.hasOwnProperty('error')) {
                alert('Room Was Deleted');
                window.location.href = window.location.protocol+'//'+ window.location.host +'/home'
            }
            else if(raw_response.hasOwnProperty('redirect')) {
                console.log('redirecting');
                console.log(raw_response['redirect']);
                window.location.href = window.location.protocol+'//'+ window.location.host + raw_response['redirect'];
            }
            else {
                updateChatRoomList(raw_response, callback);
            }
        };

        xhr.send(name_object);
    }

    function updateChatRoomList(raw_response, callback){
        // Update List

        var recentMessages = raw_response['recent_messages'];
        var mostRecentId = raw_response['most_recent_id'];

        var listHolder = document.getElementById('message_holder');

        for(var z = 0; z < recentMessages.length; z++){
            var message = recentMessages[z];

            // From User
            if(message['type'] === 'outbound'){
                var outBoundTemplate = clonedOutbound.cloneNode(true);

                outBoundTemplate.id = message['id'];
                var messageHolderOut = outBoundTemplate.querySelector('.out-bound-message');
                messageHolderOut.firstElementChild.textContent = message['message'];

                var header = outBoundTemplate.querySelector('.message-banner');
                header.firstElementChild.textContent = 'You';


                outBoundTemplate.classList.remove('hidden');
                listHolder.appendChild(outBoundTemplate);
            }
            // To User
            else {
                var inBoundTemplate = clonedInbound.cloneNode(true);
                inBoundTemplate.id = message['id'];
                var userName = inBoundTemplate.querySelector('.message-banner');
                userName.lastElementChild.textContent = message['sender_name'];
                var messageHolderIn = inBoundTemplate.querySelector('.in-bound-message');
                messageHolderIn.firstElementChild.textContent = message['message'];
                inBoundTemplate.classList.remove('hidden');
                listHolder.appendChild(inBoundTemplate);
            }

            /*
                var sep = document.createElement('hr');
                sep.classList.add('my-sep');
                sep.style.marginLeft = 32;
                sep.style.marginRight = 32;
                listHolder.appendChild(sep);
            */

        }

        setTimeout(function(){
            callback(mostRecentId);
        }, 1000);
    }

});

