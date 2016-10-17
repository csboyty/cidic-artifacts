var register=(function(config,functions){
    return {

    }
})(config,functions);
$(document).ready(function(){
    $("#sendSms").click(function(){
        var el=$(this);
        var tel=$("#tel").val();
        if(!el.hasClass("disable")){
            if(tel){
                if(validator.element($("#tel"))){
                    validCode.showValidCodeWindow();
                }
            }else{
                $().toastmessage("showErrorToast",config.messages.enterTel);
            }

        }
    });



    var validator=$("#myForm").validate({
        rules: {
            tel: {
                required:true,
                maxlength:16,
                remote:config.ajaxUrls.checkTelExist
            },
            code:{
                required:true,
                rangelength:[4,4]
            },
            password:{
                required:true,
                rangelength:[6, 20]
            },
            confirmPwd:{
                equalTo:"#password"
            },
            agree:"required"
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
            },
            password:{
                required:config.validErrors.required,
                rangelength:config.validErrors.rangLength.replace("${min}",6).replace("${max}",20)
            },
            confirmPwd:{
                equalTo:config.validErrors.equalTo
            },
            agree:config.validErrors.agree

        },
        submitHandler:function(form){
            form.submit();
        }
    });

    //显示协议
    $("#agreement").click(function(){
        var href=$(this).attr("href");

        $.ajaxSetup ({
            cache: false //关闭AJAX相应的缓存
        });

        $("#content").load(href+" #agreementBody",function(){
            $("#agreementWindow").removeClass("hidden");
            //$(window).scrollTop(0);
        });

        return false;
    });

    $("#agree").click(function(){
        $("#agreementWindow").addClass("hidden");
        $("#agreeInput").prop("checked",true);
    });


    $(".popWindow .close").click(function(){
        $(".popWindow").addClass("hidden");
    });
});