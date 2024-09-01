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

function triggerPrint(memoryId) {
  socket.emit('print', memoryId);
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
