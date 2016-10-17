var cart=(function(config,functions){
    return {
        submitForm:function(form){
            functions.showLoading();

            $("#address").val($("#addresses .active").data("address-id"));

            form.submit();
        }
    }
})(config,functions);

$(document).ready(function(){

    $("#submit").click(function(){
        if($("#addresses li").length==0){
            alert(config.messages.addAddress);
            return false;
        }else{
            cart.submitForm($("#myForm"));
        }
    });

    $("#addresses").on("click","li",function(){
        $("#addresses .active").removeClass("active");
        $(this).addClass("active");
    });
});
