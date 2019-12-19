$(document).ready(function(){
  $("#add-new").click(function (){
    var counter=$('.entry-count').length+1;
    console.log('adding row: '+counter);
    var new_row= $('<div class="row-body" id="row-'+counter+'">'+
    '<span class="td-number"><input type="text" name="input_r'+counter+'" value='+counter+' class="entry-count" style="border:none; background-color: #fff;" readonly="readonly"></span>'+
    '<span class="td-sample"><input type="text" name="input_r'+counter+'_sample_id" id="input-r'+counter+'-sample-id"></span>'+
    '<span class="td-group"><input type="text" name="input_r'+counter+'_group_id" id="input-r'+counter+'-group-id"></span>'+
    '<span class="td-file1"><input type="text" name="input_r'+counter+'_file_1" id="input-r'+counter+'-file-1"></span>'+
    '<span class="td-file2"><input type="text" name="input_r'+counter+'_file_2" id="input-r'+counter+'-file-2"></span>'+
    '<span class="tbl-button"><a class="circle remove-new" id="remove-button-'+counter+'"><i class="fas fa-minus-circle"></i></a></span>'+
    '</div>');
    $("#tbl-wrapper").append(new_row);
console.log("Clicked add");
  });

  $("#tbl-wrapper").on("click", ".remove-new", function (){
    var ind = parseInt(($(this).attr('id')).substring(14));
    var counter=$('.entry-count').length;
    var i;

    console.log('removing row: '+ind);
    // Copy up the rows that are below the row we want to delete
    for(i=ind;i<counter;i++){
      $('#input-r'+i+'-sample-id').val($('#input-r'+(i+1)+'-sample-id').val());
      $('#input-r'+i+'-group-id').val($('#input-r'+(i+1)+'-group-id').val());
      $('#input-r'+i+'-file-1').val($('#input-r'+(i+1)+'-file-1').val());
      $('#input-r'+i+'-file-2').val($('#input-r'+(i+1)+'-file-2').val());
    }
    // Remove the last row
    if(counter>1){
      $('#row-'+counter).remove();
    }
    else{// If there is only one row left, just clear the entries without removing it
      $('#input-r1-sample-id').val('');
      $('#input-r1-group-id').val('');
      $('#input-r1-file-1').val('');
      $('#input-r1-file-2').val('');
    }
  });
});
