function guidGenerator() {
    var S4 = function() {
        return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    };
    return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}

function display() {
    console.log("Loading");
    socket = io.connect('http://127.0.0.1:5000/');
    socket.on('photos', function(message) {
        if (message['faces'].length > 0){
            var root = document.getElementById("faces");
            if (root.childNodes.length > 4) {
                root.childNodes[root.childNodes.length - 1].remove();
            }
            var container = document.createElement("div");
            var quick = guidGenerator();
            container.id = quick;
            var newthing = document.createElement("h5");
            newthing.innerHTML = message['date'];
            document.getElementById("faces").insertBefore(container, document.getElementById("faces").firstChild);
            for (i = 0; i < message['faces'].length;i++) {
                var elem = document.createElement("img");
                elem.src = "/getcropped?id="+message['faces'][i];
                document.getElementById(quick).appendChild(newthing);
                document.getElementById(quick).appendChild(elem);
            }
        }
        document.getElementById('picture').src = "/photo?" + new Date().getTime();
    });
}
