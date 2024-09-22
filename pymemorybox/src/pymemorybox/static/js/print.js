const wsEndpoint = location.protocol + '//' + location.host;
const token = localStorage.getItem('token');
var socket = io.connect(wsEndpoint, {
    query: { token },
    transports: ["websocket"]
});


socket.on('connect', function() {
    console.log('Connected');
});

socket.on('connect_error', function(err) {
    console.error('Connection error:', err);
});

$('#printButton').on('click', function(event) {
    console.log("Print button clicked !");
    var print = true;
    if($(this).data('printed') == "True"){
        print = confirm('This picture has already been printed. Are you sure you want to print it again ?');
    }
    if(print){
        triggerPrint($(this).data('memory'));
    }
});

// // Listen for notifications from the server
// socket.on('notify_agent', function(data) {
//     console.log('Agent notified:', data.message);
//     // Here you can perform additional actions when the agent is notified
// });

// Listen for notifications from the agent
socket.on('agent_response', function(data) {
    console.log('Received data from the agent');
    console.log(data);
    setPrintMessage(data.request_id, data.message.type, data.message.message);
    // Here you can perform additional actions when the agent is notified
});

function triggerPrint(memoryId) {
    //socket.emit('print', memoryId);

    $('#printButton').prop("disabled", true);
    socket.emit("print", memoryId, withTimeout((response) => {
        setPrintMessage(response, "info", "Print request sent.");
    }, () => {
        setPrintMessage("UNKNOWN", "danger", "Server did not respond.");
    }, 5000));

    console.log("Requested print for memory id ", memoryId);
}

function setPrintMessage(uid, kind, message, duration=0) {

    var alertelem = $('[data-printid="'+uid+'"]');
    if (alertelem.length == 0) {
        console.log("Creating div");
        $("#printStatuses").append('<div data-printid="' + uid + '"></div>');
        alertelem = $('[data-printid="'+uid+'"]');
    }
    alertelem.removeClass();
    alertelem.addClass('alert');
    alertelem.addClass('alert-' + kind);
    alertelem.text(message);
    if(duration > 0){
        alertelem.delay(duration).queue(function(next){
        $(this).hide();
        next();
    });
    }
}



const withTimeout = (onSuccess, onTimeout, timeout) => {
    let called = false;

    const timer = setTimeout(() => {
        if (called) return;
        called = true;
        onTimeout();
    }, timeout);

    return (...args) => {
        if (called) return;
        called = true;
        clearTimeout(timer);
        onSuccess.apply(this, args);
    }
}