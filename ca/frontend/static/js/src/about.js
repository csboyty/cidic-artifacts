$(document).ready(function(){
    $("#directory").on("click","a",function(){
        var target=$(this).attr("href");
        var top=$(target).offset().top;
        //$("#directory a.active").removeClass("active");
        $("html,body").scrollTop(top);
        //$(this).addClass("active");

        return false;
    });
});