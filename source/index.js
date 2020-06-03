$(document).ready(function(){
  var clicked = false;
  $("#buttonId").click(function(){
    if (clicked) {
        return 0;
    }
    document.getElementById("buttonId").disabled = true;
    document.getElementById("buttonId").style.cursor = 'not-allowed';
    document.getElementById("loading").style.display = 'block';
    clicked = true;
    $.ajax({url: "http://127.0.0.1:5000/MaskDetector",
    error: function(xhr, status, error) {
        var err = eval("(" + xhr.responseText + ")");
    },
    success: function(result){
      document.getElementById("buttonId").disabled = false;
      document.getElementById("loading").style.display = 'none';
      document.getElementById("buttonId").style.cursor = 'pointer';
      clicked = false;
    }});
  });
});