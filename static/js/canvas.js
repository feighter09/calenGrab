(function() {
  
  var canvas = document.getElementById("selectionDrawer");
  var ctx = canvas.getContext("2d");

  var canvasOffset = $("canvas").offset();
  var offsetX = canvasOffset.left;
  var offsetY = canvasOffset.top;

  var isDrawing = false;
  var startX, startY, endX, endY;
  
  this.resizeCanvas = function() {
    var img = document.getElementById("calendarImg");
    canvas.width = String(img.clientWidth);
    canvas.height = String(img.clientHeight);
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
    
    endX = parseInt(e.clientX - offsetX);
    endY = parseInt(e.clientY - offsetY);
    var diffX = Math.abs(startX - endX);
    var diffY = Math.abs(startY - endY);

    if(diffX < 5 || diffY < 5){
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    };
    canvas.style.cursor = "default";

    var pic = $("calendarImg").attr("src");
    $.ajax({
      url: "/selection",
      type: "POST",
      data: {
        pic: pic,
        startX: startX,
        endX: endX, 
        startY: startY,
        endY: endY
      },
      error: function() {
        alert("failed");
      },
      success: function() {
        alert("it worked!");
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
    endX = startX = parseInt(e.clientX - offsetX);
    endY = startY = parseInt(e.clientY - offsetY);
  }

  this.init();
})();