

$(document).ready(function() {
    // Submit a new form using AJAX when the "submit" button is clicked
    console.log("ready");
    // call function to load all posts
    load_all_posts();
    $("#new_post_form").submit(function(event) {
        console.log("we are in the submit function");
        event.preventDefault();
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/new_post", true);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.onload = function() {
            if (this.status == 200) {
                // If succesful, append the new post to the page
                var post = document.createElement("div");
                post.classList.add("post");
                var post_html = JSON.parse(this.responseText);
                post.innerHTML = post_html;
                document.getElementById('user_feed').appendChild(post);
                // Clear the form for new post entry
                document.getElementById("new_post_form").reset();
            } else {
                alert("Error: " + this.responseText);
            }
        };
        xhttp.onerror = function() {
            console.log("Error: " + this.responseText);
        };
        xhttp.send($(this).serialize());
    });
});



// function to load all posts (aka global feed)
function load_all_posts() {
    console.log("we are in the load_all_posts function")
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/get_all_posts", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            var data = JSON.parse(this.responseText);
            // iterate through each post and append to the page
            for (var i = 0; i < data.length; i++){
                var post = document.createElement("div");
                post.classList.add("post");
                // post.innerHTML = '<p>${data[i].name} (${data[i].username})</p><p>${data[i].content}</p><p>${data[i].timestamp}</p>';
                post.innerHTML = `<p>${data[i].name} (${data[i].username})</p><p>${data[i].content}</p><p>${data[i].timestamp}</p>`;

                // append the post to the page within the user_feed div
                document.getElementById('user_feed').appendChild(post);
            }
        } else if (this.readyState == 4 && this.status != 200){
            console.log("Error: " + this.responseText);
        };
    }
    xhttp.send();
}