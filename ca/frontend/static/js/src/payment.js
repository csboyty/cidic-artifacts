$(document).ready(function(){
    $("#payTypes").on("click","li",function(){
        $("#payTypes .active").removeClass("active");
        $("#payTypes input:checked").prop("checked",false);
        $(this).addClass("active");
        $(this).find("input").prop("checked",true);
    });

    $("#submit").click(function(){
        $("#myForm").submit();
        setTimeout(function(){
            $("#resultWindow").removeClass("hidden");
        },3000);
    });

    $("#failed").click(function(){
        $("#resultWindow").addClass("hidden");
    })
});