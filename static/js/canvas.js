(function() {
  $("#prompt").hide();

  var canvas = document.getElementById("selectionDrawer");
  if (!canvas)
    return;
  var ctx = canvas.getContext("2d");
 
  var imgOrgHeight, imgOrgWidth;

  var canvasOffset = $("canvas").offset();
  var offsetX = canvasOffset.left;
  var offsetY = canvasOffset.top;

  var isDrawing = false;
  var startX, startY, endX, endY;
  var appends = 0;
  
  this.resizeCanvas = function() {
    var img = document.getElementById("calendarImg");
    imgOrgHeight = img.clientHeight;
    imgOrgWidth = img.clientWidth;
    if (imgOrgWidth > 960) {
      $("#calendarImg").width(960);
    };
    canvas.height = String(img.clientHeight);
    canvas.width = String(img.clientWidth);
    canvas.style.left = String((960 - canvas.width) / 2) + "px";
  }

  this.init = function() {
    resizeCanvas();
    offsetX = canvasOffset.left + (960 - canvas.width) / 2;
    offsetY = canvasOffset.top;

    $('img').on('dragstart', function(event) { 
      event.preventDefault(); 
    });

    $("canvas").on('mousedown', function (e) {
        handleMouseDown(e);
    }).on('mouseup', function(e) {
        handleMouseUp(e);
    }).on('mousemove', function(e) {
        handleMouseMove(e);
    });
  }

  this.handleMouseUp = function (e) {
    isDrawing = false;
    canvas.style.cursor = "default";
    
    endX = parseInt(e.clientX - offsetX);
    endY = parseInt(e.clientY - offsetY);
    var diffX = Math.abs(startX - endX);
    var diffY = Math.abs(startY - endY);
    var cols = diffX / 1080
    var rows = diffY / 1000

    if(diffX < 5 || diffY < 5){
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      return;
    };

    var img = document.getElementById("calendarImg");
    if (imgOrgWidth != img.clientWidth) {
      var x0, x1, y0, y1;
      var perc = startX*1.0 / img.clientWidth;
      startX = Math.round(perc * imgOrgWidth);
      perc = endX*1.0 / img.clientWidth;
      endX = Math.round(perc * imgOrgWidth);

      perc = startY*1.0 / img.clientHeight;
      startY = Math.round(perc * imgOrgHeight);
      perc = endY*1.0 / img.clientHeight;
      endY = Math.round(perc * imgOrgHeight);
    };

    var pic = $("#calendarImg").attr("src");
    console.log(pic);
    $.ajax({
      url: "/selection",
      type: "POST",
      data: JSON.stringify({
        "pic": pic,
        startX: startX,
        endX: endX, 
        startY: startY,
        endY: endY,
        rows: rows,
        cols: cols
      }),
      dataTypa: "json",
      contentType: "application/json",
      error: function() {
        alert("failed");
      },
      success: function(response) {
        console.log(response.results);
        // response = JSON.parse(response);
        console.log(response.results[0].end)

        for (var res in response.results){
          $("#summary").val(response.results[res].summary);
          $("#start").val(response.results[res].start);
          $("#end").val(response.results[res].end);
          $("#prompt").show();
        }

        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    });
  }

  this.handleMouseMove = function (e) {
    if (isDrawing) {
      endX = parseInt(e.clientX - offsetX);
      endY = parseInt(e.clientY - offsetY);       
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      //draw blue box
      ctx.fillStyle = "rgba(0, 50, 200, 0.3)";
      ctx.fillRect(startX, startY, endX - startX, endY - startY);

      //draw outline
      ctx.strokeStyle = "white";
      ctx.beginPath();
      ctx.rect(startX, startY, endX - startX, endY - startY);
      ctx.stroke();
    }
  }

  this.handleMouseDown = function (e) {
    canvas.style.cursor = "crosshair";    
    isDrawing = true;
    startX = parseInt(e.clientX - offsetX);
    startY = parseInt(e.clientY - offsetY);
    endY = parseInt(e.clientX - offsetX);
    endX = parseInt(e.clientY - offsetY);
  }

  this.init();
})();

function sendToGoogle(){
  
  var summary = $("#summary").val();
  var start = $("#start").val();
  var end = $("#end").val();

  var data = {
    "summary": summary,
    "start": {
      "dateTime": start + "-05:00"
    },
    "end": {
      "dateTime": end + "-05:00"
    }
  };

  var request = gapi.client.calendar.events.insert({
    'calendarId': 'primary',
    'resource': data
  });
  request.execute(function(resp) {
    if (!resp.error){
      alert("success!");
      $("#summary").val("");
      $("#start").val("");
      $("#end").val("");
    } else {
      alert("something went wrong, please try again");
    }
  });
}