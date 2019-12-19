// Same as config_file_form.js only without the down and up arrow images

$(document).ready(function(){
  var animTime = 300,
      clickPolice = false;

  // Form fields should initially be hidden
  $('.acc-content').attr("height", 0);

  $(document).on('touchstart click', '.acc-btn', function(){
    if(!clickPolice){
       clickPolice = true;

      var currIndex = $(this).index('.acc-btn'),
          targetHeight = $('.acc-content-inner').eq(currIndex).outerHeight();

      $('.acc-btn h3').removeClass('selected');
      $('.acc-btn div').removeClass('open');
      $(this).find('h3').addClass('selected');
      $(this).find('div').addClass('open');

      $('.acc-content').stop().animate({ height: 0 }, animTime);
      $('.acc-content').eq(currIndex).stop().animate({ height: targetHeight }, animTime);

      setTimeout(function(){ clickPolice = false; }, animTime);
    }

  });

});
