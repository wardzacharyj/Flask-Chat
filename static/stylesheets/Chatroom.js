document.addEventListener("DOMContentLoaded", function(event) {

    //////////////////////////////////////////////////////////////////////////////////////////
    //  ROOM CREATION
    //////////////////////////////////////////////////////////////////////////////////////////

    var create_room_form = document.getElementById('create_room_form');
    var btn_show_room_create = document.getElementById('btn_show_room_create');


    btn_show_room_create.addEventListener('click', showCreateForm);

    create_room_form.addEventListener('submit', hideRoomCreateFormAndSubmit);


    function showCreateForm(){
        btn_show_room_create.classList.add('hidden');
        create_room_form.classList.remove('hidden');
    }

    function hideRoomCreateFormAndSubmit(event){
        event.preventDefault();
        create_room_form.classList.add('hidden');
        btn_show_room_create.classList.remove('hidden');
        var formData = new FormData(create_room_form);
        var name = formData.get('input_create_chat_room');
        create_room(name);
        create_room_form.reset();
    }

    function create_room(room_name){
        var name_object = JSON.stringify({name: room_name});
        var xhr = new XMLHttpRequest();
        xhr.open("POST", '/create_room', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function() {
            if (xhr.status === 200 && xhr.responseText === 'Failed') {
                alert('Something went wrong.  Name is now ' + xhr.responseText);
            }
            else if (xhr.status !== 200) {
                alert('Request failed.  Returned status of ' + xhr.status);
            }
        };

        xhr.send(name_object);
    }

    //////////////////////////////////////////////////////////////////////////////////////////
    //  ROOM LISTENER
    //////////////////////////////////////////////////////////////////////////////////////////

    poll_chat_rooms();


    function poll_chat_rooms() {
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function() {
            if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
                var raw_json = JSON.parse(xmlHttp.responseText);
                console.log('Post Fired');
                updateChatRoomList(raw_json.my_rooms, raw_json.other_rooms, poll_chat_rooms);
            }
        };
        xmlHttp.open("GET", '/poll_rooms', true); // true for asynchronous
        xmlHttp.send(null);
    }

    function updateChatRoomList(myRooms, otherRooms, callback){


        var roomDrawer = document.getElementsByClassName('mdl-navigation');
        roomDrawer = roomDrawer[1];

        while (roomDrawer.childNodes.length > 2) {
            roomDrawer.removeChild(roomDrawer.lastChild);
        }


        if (myRooms.length !== 0){

            for(var z = 0; z < myRooms.length; z++){
                var myRoom = document.createElement('a');
                myRoom.classList.add('mdl-navigation__link');
                myRoom.classList.add('custom-hover');
                myRoom.textContent = myRooms[z].name;
                myRoom.href = '/room/'+myRooms[z].id;
                roomDrawer.appendChild(myRoom);
            }
        }

        ////////////////////////////////////////////////////////////

        var listHolder = document.querySelector("div.max-width");

        while (listHolder.firstChild) {
            listHolder.removeChild(listHolder.firstChild);
        }

        if(otherRooms.length !== 0){
            var unorderedList = document.createElement('ul');
            unorderedList.id = 'rooms_list';
            unorderedList.class = 'mdl-list';

            otherRooms.forEach(function(item){
                var listElement = document.createElement('li');
                listElement.classList.add('mdl-list__item');
                listElement.classList.add('mdl-list__item--two-line');

                    var iconHolder = document.createElement('span');
                    iconHolder.classList.add('mdl-list__item-primary-content');

                        var icon = document.createElement('i');
                        icon.classList.add('mdl-color--deep-purple-300');
                        icon.classList.add('material-icons');
                        icon.classList.add('mdl-list__item-avatar');
                        icon.classList.add('major-icon-font');
                        icon.textContent = 'people';
                        iconHolder.appendChild(icon);

                        var roomName = document.createElement('span');
                        roomName.classList.add('my-primary-font');
                        roomName.textContent = item.name;
                        iconHolder.appendChild(roomName);
                        ///
                        var roomOwner = document.createElement('span');
                        roomOwner.classList.add('mdl-list__item-sub-title');
                        roomOwner.classList.add('my-secondary-font');
                        roomOwner.textContent = item.owner_name;
                        iconHolder.appendChild(roomOwner);

                    listElement.appendChild(iconHolder);

                    var actionItem = document.createElement('span');
                    actionItem.classList.add('mdl-list__item-secondary-content');

                        var linkToRoom = document.createElement('a');
                        linkToRoom.classList.add('mdl-list__item-secondary-action');
                        linkToRoom.href = '/room/'+item.id;
                        actionItem.appendChild(linkToRoom);

                            var questionAnswer = document.createElement('i');
                            questionAnswer.classList.add('material-icons');
                            questionAnswer.classList.add('minor-icon-font');
                            questionAnswer.textContent = 'question_answer';
                            linkToRoom.appendChild(questionAnswer);

                    listElement.appendChild(actionItem);

                unorderedList.appendChild(listElement);

                var sep = document.createElement('hr');
                sep.classList.add('my-sep');

                unorderedList.appendChild(sep);

            });

            listHolder.appendChild(unorderedList);
        }
        else {
            var noRooms = document.createElement('h6');
            noRooms.classList.add('mdl-typography--display-1');
            noRooms.classList.add('mdl-typography--text-center');
            noRooms.classList.add('mdl-color-text--white');
            noRooms.style.fontSize = 16;
            noRooms.style.paddingTop = 55;
            noRooms.textContent = 'Nobody else has created any chat rooms';
            listHolder.appendChild(noRooms);
        }

        setTimeout(callback, 1000);
    }

});

