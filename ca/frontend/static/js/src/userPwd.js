var userPwd=(function(config,functions){
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
    $("#sendValidCode").click(function(){
        var el=$(this);
        if(!el.hasClass("disable")){
            el.addClass("disable");
            $.ajax({
                url:config.ajaxUrls.sendSms,
                type:"post",
                dataType:"json",
                data:{
                    tel:tel
                },
                success:function(data){
                    if(data.success){

                        var i=120;
                        var interval=setInterval(function(){
                            el.html(i+"秒后重发");
                            i--;

                            if(i<=0){
                                el.html("发送验证码").removeClass("disable");
                                clearInterval(interval);
                            }
                        },1000);
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                        el.removeClass("disable");
                    }
                },
                error:function(data){
                    functions.ajaxErrorHandler();
                    el.removeClass("disable");
                }
            })
        }
    });

    $("#myForm").validate({
        rules: {
            phone: {
                required:true,
                number:true
            },
            validCode:{
                required:true,
                rangelength:[4,4]
            },
            password:{
                required:true,
                rangelength:[6, 20]
            },
            confirmPwd:{
                equalTo:"#password"
            }
        },
        messages: {
            phone: {
                required:config.validErrors.required,
                number:config.validErrors.number
            },
            validCode:{
                required:config.validErrors.required,
                rangelength:config.validErrors.rangLength.replace("${min}",4).replace("${max}",4)
            },
            password:{
                required:config.validErrors.required,
                rangelength:config.validErrors.rangLength.replace("${min}",6).replace("${max}",20)
            },
            confirmPwd:{
                equalTo:config.validErrors.equalTo
            }
        },
        submitHandler:function(form){
            userPwd.submitForm();
        }
    });
});