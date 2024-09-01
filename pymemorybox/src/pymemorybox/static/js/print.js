const wsEndpoint = location.protocol + '//' + location.host;
var socket = io.connect(wsEndpoint);

$('#printButton').on('click', function(event) {
    console.log("Print button clicked !");
    triggerPrint($(this).data('memory'));
});

// Listen for notifications from the server
socket.on('notify_agent', function(data) {
    console.log('Agent notified:', data.message);
    // Here you can perform additional actions when the agent is notified
});

// Listen for notifications from the agent
socket.on('agent', function(data) {
  console.log('Received data from the agent');
  console.log(data);
  // Here you can perform additional actions when the agent is notified
});

function triggerPrint(memoryId) {
  //socket.emit('print', memoryId);

  socket.emit("print", memoryId, withTimeout((response) => {
    console.log("success!");
    console.log(response);
  }, () => {
    console.log("timeout!");
  }, 1000));

  console.log("Requested print for memory id ", memoryId);
  setPrintMessage("info", "Print request sent.");
}

function setPrintMessage(kind, message, duration=0) {
  $('#printAlert').show();
  $('#printAlert').removeClass();
  $('#printAlert').addClass('alert');
  $('#printAlert').addClass('alert-' + kind);
  $('#printAlert').text(message);
  if(duration > 0){
    $('#printAlert').delay(duration).queue(function(next){
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