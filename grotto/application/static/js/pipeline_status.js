$(document).ready(function(){
  if ($("#pipe-status").text() !== 'complete'){
    $("#create-bdbag").attr("disabled", true);
  };

  $("#generate-report").click(function(){
    alert("Report generation can take a couple minutes depending on the size of the output data\nPlease be patient.");
  });
});
