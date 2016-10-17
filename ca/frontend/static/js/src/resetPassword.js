var resetPassword=(function(config,functions){
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
                        $().toastmessage("showSuccessToast",config.messages.optSuccessRedirect);
                        setTimeout(function(){
                            location.href="login";
                        },3000);
                    }else{
                        $().toastmessage("showErrorToast",response.info);
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
    $("#myForm").validate({
        rules: {
            password:{
                required:true,
                rangelength:[6, 20]
            },
            confirmPwd:{
                equalTo:"#password"
            }
        },
        messages: {
            password:{
                required:config.validErrors.required,
                rangelength:config.validErrors.rangLength.replace("${min}",6).replace("${max}",20)
            },
            confirmPwd:{
                equalTo:config.validErrors.equalTo
            }
        },
        submitHandler:function(form){
            resetPassword.submitForm(form);
        }
    });
});