

$(document).ready(function (){
    console.log("hi");

    load_current_user_info();
});


function load_current_user_info(){
    console.log("in function load_current_user_info");
    load_current_user_name();
    load_current_user_posts();
}


function load_current_user_name(){
    console.log("in load_current_user_name() function")
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/get_current_user_name", true)
    xhttp.onreadystatechange  = function (){
        if (this.readyState == 4 && this.status == 200){
            var name = this.responseText
            console.log(name);
            var nameHeader = document.getElementById("current_user_name");
            nameHeader.innerHTML = "@" + name;
        } else if( this.readyState ==4 && this.status != 200) {
            console.log("Error: " + this.responseText);
        }
    };
    xhttp.send();
}

function load_current_user_posts(){
    console.log("in load_current_user_posts() function")
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/get_current_user_posts", true);
    xhttp.onreadystatechange = function (){
        if (this.readyState == 4 && this.status == 200){
            var data = JSON.parse(this.responseText);
            var user_feed = document.getElementById("current_user_feed");
            for (var i = 0; i < data.length; i++){
                var post = document.createElement("div");
                post.classList.add("post");

                var headerContainer = document.createElement("div");
                headerContainer.classList.add("headerContainer");

                console.log(data[i].name);
                var name = document.createElement("p");
                name.classList.add("name");
                name.innerHTML = `${data[i].name} (${data[i].username})`;
                headerContainer.appendChild(name);

                console.log(data[i].timestamp);
                var timestamp = document.createElement("p");
                timestamp.classList.add("timestamp");
                timestamp.innerHTML = data[i].timestamp;
                headerContainer.appendChild(timestamp);

                console.log(data[i].content);
                var content = document.createElement("p");
                content.classList.add("content");
                content.innerHTML = data[i].content;

                post.appendChild(headerContainer);
                post.appendChild(content);

                user_feed.appendChild(post);

                console.log("");
            }    
        } else if (this.readyState == 4 && this.status != 200){
            console.log("Error: " + this.responseText);
        }
    };
    xhttp.send();
}
