$(document).ready(function(){
    $("#myForm").validate({
        rules: {
            phone: {
                required:true,
                maxlength:16
            },
            password:{
                required:true,
                rangelength:[6, 20]
            }
        },
        messages: {
            phone: {
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",16)
            },
            password:{
                required:config.validErrors.required,
                rangelength:config.validErrors.rangLength.replace("${min}",6).replace("${max}",20)
            }
        },
        submitHandler:function(form){
            form.submit();
        }
    });
});