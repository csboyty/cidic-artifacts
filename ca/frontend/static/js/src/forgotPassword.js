$(document).ready(function(){
    $("#sendSms").click(function(){
        var el=$(this);
        var tel=$("#tel").val();
        if(!el.hasClass("disable")){
            if(tel){
                validCode.showValidCodeWindow();
            }else{
                $().toastmessage("showErrorToast",config.messages.enterTel);
            }

        }
    });


    $("#myForm").validate({
        rules: {
            tel: {
                required:true,
                maxlength:16
            },
            code:{
                required:true,
                rangelength:[4,4]
            }
        },
        messages: {
            tel: {
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",16)
            },
            code:{
                required:config.validErrors.required,
                rangelength:config.validErrors.rangLength.replace("${min}",4).replace("${max}",4)
            }
        },
        submitHandler:function(form){
            form.submit();
        }
    });
});