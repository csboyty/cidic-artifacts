$(document).ready(function(){
    $('#slider').flexslider({
        animation: "slide",
        controlNav: true,
        directionNav:true,
        animationLoop: false,
        slideshow: false
    });

    $(window).scroll(function(){
        if($(window).scrollTop()>=$("#slider").height()){
            $("#header").removeClass("headerStatic");
        }else{
            $("#header").addClass("headerStatic");
        }
    });

});
