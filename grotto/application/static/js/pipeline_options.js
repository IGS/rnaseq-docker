$(document).ready(function(){

// Things that should be initially hidden
$(".old-cuff").hide();

  // Determine if we show or hide the Euk-only pipeline sections
  // Euk = Not checked, Prok = checked
  $("#pipeline-type").click(function (){
    if($("#pipeline-type").is(':checked')){
      $(".euk-only").hide();
      $("#use-tophat").removeAttr('value');
      $("#old-cufflinks").removeAttr('value');
      $("#isoform-analysis").removeAttr('value');
      $("#differential-isoform-analysis").removeAttr('value');
    } else {
      $(".euk-only").show();
    }
  });

  $("#alignment").click(function (){
    if($("#alignment").is(':checked') && !$("#build-indexes").is(':checked')){
      $(".index-file-div").show();
    } else {
      $(".index-file-div").hide();
    }

    if($("#alignment").is(':checked')){
      $(".file-type-div1").hide();
      $(".file-type-div2").hide();
      $(".file-type-div3").hide();
      $(".file-type-div4").hide();
      $(".file-type-div5").hide();
      $(".sorted-div1").hide();
      $(".sorted-div2").hide();
      $(".sorted-div3").hide();
      $(".sorted-div4").hide();
      $(".sorted-div5").hide();
      $(".count-div").hide();
    } else{
      if($("#visualization").is(':checked')){
        $(".file-type-div1").show();
        $(".sorted-div1").show();
      }
      if($("#rpkm-analysis").is(':checked')){
        $(".file-type-div2").show();
        $(".sorted-div2").show();
      }
      if($("#differential-gene-expression").is(':checked')){
        $(".file-type-div3").show();
        $(".sorted-div3").show();
        $('.count-div').show();
      }
      if($("#isoform-analysis").is(':checked')){
        $(".file-type-div4").show();
        $(".sorted-div4").show();
      }
      if($("#differential-isoform-analysis").is(':checked')){
        $(".file-type-div5").show();
        $(".sorted-div5").show();
      }
    }
  });
  $("#build-indexes").click(function (){
    if($("#build-indexes").is(':checked')){
      $(".index-div").hide();
    } else {
      if($("#alignment").is(':checked')){
        $(".index-div").show();
      } else {
        $(".index-div").hide();
      }
    }
  });

  $("#visualization").click(function (){
    if($("#visualization").is(':checked') && !($("#alignment").is(':checked'))){
      $(".file-type-div1").show();
      $(".sorted-div1").show();
    } else {
      $(".file-type-div1").hide();
      $(".sorted-div1").hide();
    }
  });

  $("#rpkm-analysis").click(function (){
    if($("#rpkm-analysis").is(':checked') && !($("#alignment").is(':checked'))){
      $(".file-type-div2").show();
      $(".sorted-div2").show();
    } else {
      $(".file-type-div2").hide();
      $(".sorted-div2").hide();
    }
  });

  $("#differential-gene-expression").click(function (){
    if($("#differential-gene-expression").is(':checked')){
      if(!($("#alignment").is(':checked'))){
        $(".file-type-div3").show();
        $(".sorted-div3").show();
        $(".count-div").show();
      }
      $(".comparison-groups-div1").show();
    } else {
      $(".file-type-div3").hide();
      $(".sorted-div3").hide();
      $(".count-div").hide();
      $(".comparison-groups-div1").hide();
    }
  });

  $("#isoform-analysis").click(function (){
    if($("#isoform-analysis").is(':checked')){
      if(!($("#alignment").is(':checked'))){
        $(".file-type-div4").show();
        $(".sorted-div4").show();
      }
      $(".include-novel-div").show();
    } else {
      $(".file-type-div4").hide();
      $(".sorted-div4").hide();
      $(".include-novel-div").hide();
    }
  });

  $("#differential-isoform-analysis").click(function (){
    if($("#differential-isoform-analysis").is(':checked')){
      if(! ($("#alignment").is(':checked')) ){
        $(".file-type-div5").show();
        $(".sorted-div5").show();
      }
      $(".use-ref-gtf-div").show();
      $(".comparison-groups-div2").show();
      $(".old-cuff").show();
    } else {
      $(".file-type-div5").hide();
      $(".sorted-div5").hide();
      $(".use-ref-gtf-div").hide();
      $(".comparison-groups-div2").hide();
      $(".old-cuff").hide();
      $("#old-cufflinks").removeAttr('value');
    }
  });

  $(".file-type").change(function (){
    $(".file-type").val($(this).val())
  });

  $(".sortedd").change(function (){
    $(".sortedd").val($(this).val())
  });

  $(".comparison-groups").change(function (){
    $(".comparison-groups").val($(this).val())
  });
});
