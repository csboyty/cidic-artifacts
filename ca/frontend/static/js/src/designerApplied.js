var designerApplied=(function(config,functions){
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
                        form.reset();
                        $("#filename").html("");
                        $("#attachment").val("");
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
    functions.createQiNiuUploader({
        maxSize:config.uploader.sizes.all,
        filter:config.uploader.filters.zip,
        uploadBtn:"attachmentUpload",
        multiSelection:false,
        multipartParams:null,
        uploadContainer:"attachmentContainer",
        fileAddCb:null,
        progressCb:function(file){
            $("#filename").html(file.percent+"%");
        },
        uploadedCb:function(info,file,up){
            $("#filename").html(file.name);
            $("#attachment").val(info.url);
        }
    });

    $("#myForm").validate({
        rules: {
            name:{
                required:true,
                maxlength:20
            },
            tel:{
                required:true,
                maxlength:16
            },
            email: {
                email:true,
                maxlength:30
            },
            specialism:{
                required:true,
                maxlength:120
            },
            organization:{
                maxlength:32
            },
            graduate_institution:{
                maxlength:64
            },
            intro: {
                maxlength:500
            }
        },
        messages: {
            name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",20)
            },
            tel:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",16)
            },
            email: {
                email:config.validErrors.email,
                maxlength:config.validErrors.maxLength.replace("${max}",30)
            },
            specialism:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",120)
            },
            organization:{
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            graduate_institution:{
                maxlength:config.validErrors.maxLength.replace("${max}",64)
            },
            intro: {
                maxlength:config.validErrors.maxLength.replace("${max}",500)
            }
        },
        submitHandler:function(form){
            designerApplied.submitForm(form)
        }
    });
});