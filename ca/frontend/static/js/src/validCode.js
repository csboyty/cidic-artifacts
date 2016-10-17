var validCode=(function(config,functions){
    return {
        sendSms:function(captcha){
            var el=$("#sendSms");
            var tel=$("#tel").val();
            el.addClass("disable");
            $.ajax({
                url:config.ajaxUrls.sendSms,
                type:"post",
                dataType:"json",
                data:{
                    tel:tel,
                    captcha:captcha
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
        },
        refreshCode:function(){
            $("#captchaImg").attr("src",function(index,value){
                return value+"?noCache="+new Date().getTime();
            });
        },
        showValidCodeWindow:function(){
            $("#validCodeWindow").removeClass("hidden");
            this.refreshCode();
        }
    }
})(config,functions);

$(document).ready(function(){
    $("#validCodeForm").validate({
        onsubmit: true,
        onkeyup:false,
        rules: {
            captcha: {
                required:true,
                remote:config.ajaxUrls.checkValidCode
            }
        },
        messages: {
            captcha:{
                required:config.validErrors.required,
                remote:config.validErrors.validCode
            }

        },
        submitHandler:function(form){
            $("#validCodeWindow").addClass("hidden");
            validCode.sendSms($("#captchaInput").val());
            form.reset();
        }
    });
    $("#captchaImg").click(function(){
        validCode.refreshCode();
    });
});