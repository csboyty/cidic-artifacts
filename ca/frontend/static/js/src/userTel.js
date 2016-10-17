var userTel=(function(config,functions){
    return{
        submitForm:function(form){
            var formObj=$(form).serializeObject();

            functions.showLoading();
            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                success:function(response){
                    if(response.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        }
    }
})(config,functions);
$(document).ready(function(){
    $("#sendSms").click(function(){
        var el=$(this);
        var tel=$("#tel").val();
        if(!el.hasClass("disable")){
            if(tel){
                if(tel!=oldTel){
                    validCode.showValidCodeWindow();
                }else{
                    $().toastmessage("showErrorToast",config.messages.newTel);
                }
            }else{
                $().toastmessage("showErrorToast",config.messages.enterTel);
            }

        }
    });



    $("#myForm").validate({
        rules: {
            tel: {
                required:true,
                maxlength:16,
                remote: config.ajaxUrls.checkTelExist
            },
            code:{
                required:true,
                rangelength:[4,4]
            }
        },
        messages: {
            tel:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",16),
                remote:config.validErrors.telExist
            },
            code:{
                required:config.validErrors.required,
                rangelength:config.validErrors.rangLength.replace("${min}",4).replace("${max}",4)
            }
        },
        submitHandler:function(form){
            userTel.submitForm(form);
        }
    });
});