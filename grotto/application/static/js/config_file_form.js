/* 
Menu opening and closing code taken from
https://stackoverflow.com/questions/25168474/how-to-close-a-menu-by-clicking-on-it
*/

$(document).ready(function(){
  var animTime = 300,
      clickPolice = false;

  // Form fields should initially be hidden
  $('.acc-content').attr('height', 0);
  $('.acc-btn div:first').addClass('open');
  $('.acc-btn h3:first').addClass('selected');  

  $(document).on('touchstart click', '.acc-btn', function(){
    if(!clickPolice){
       clickPolice = true;

      var currIndex = $(this).index('.acc-btn'),
          targetHeight = $('.acc-content-inner').eq(currIndex).outerHeight(),
          expanded = $(this).find('h1').hasClass('selected');

          if(expanded) {
            $('.acc-btn h3').removeClass('selected');
            $('.acc-btn div').removeClass('open');
            $('.acc-btn img').attr("src","static/down-arrow.png");
            $('.acc-content').eq(currIndex).stop().animate({ height: targetHeight }, animTime);
            $('.acc-content').stop().animate({ height: 0 }, animTime);
          }else {
            $(this).find('h3').addClass('selected');
            $(this).find('div').addClass('open');
            $(this).find('img').attr("src","static/up-arrow.png");
            $('.acc-content').stop().animate({ height: 0 }, animTime);
            $('.acc-content').eq(currIndex).stop().animate({ height: targetHeight }, animTime);
          }
      setTimeout(function(){ clickPolice = false; }, animTime);
    }

  });

});
