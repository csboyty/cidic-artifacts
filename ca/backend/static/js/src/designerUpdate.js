var designerUpdate=(function(config,functions){

    return {
        submitForm:function(form){
            functions.showLoading();
            var formObj=$(form).serializeObject();

            $.ajax({
                url:$(form).attr("action"),
                dataType:"json",
                type:"post",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                success:function(response){
                    if(response.success){
                        //Functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccRedirect);
                        functions.timeoutRedirect("manager/designers/");
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        }
    };
})(config,functions);

$(document).ready(function(){


    //设置国籍
    if(country){
        $("#country").val(country);
    }

    functions.createQiNiuUploader({
        maxSize:config.uploader.sizes.img,
        filter:config.uploader.filters.img,
        uploadBtn:"uploadBtn",
        multiSelection:false,
        multipartParams:null,
        uploadContainer:"uploadContainer",
        fileAddCb:null,
        progressCb:null,
        uploadedCb:function(info,file,up){
            var path=info.url;
            $.get(path+"?imageInfo",function(data){
                //console.log(data);
                if(data.width==500&&data.height==500){
                    $("#imageUrl").val(path);

                    $("#image").attr("src",path);

                    $(".error[for='imageUrl']").remove();
                }else{
                    $().toastmessage("showErrorToast",config.messages.imageSizeError);
                }
            });
        }
    });
    functions.createQiNiuUploader({
        maxSize:config.uploader.sizes.img,
        filter:config.uploader.filters.img,
        uploadBtn:"uploadBgBtn",
        multiSelection:false,
        multipartParams:null,
        uploadContainer:"uploadBgContainer",
        fileAddCb:null,
        progressCb:null,
        uploadedCb:function(info,file,up){
            var path=info.url;
            $.get(path+"?imageInfo",function(data){
                //console.log(data);
                if(data.width==1920&&data.height==600){
                    $("#imageBgUrl").val(path);

                    $("#imageBg").attr("src",path);

                    $(".error[for='imageBgUrl']").remove();
                }else{
                    $().toastmessage("showErrorToast",config.messages.imageSizeError);
                }
            });
        }
    });



    $("#myForm").validate({
        ignore: [],
        rules:{
            image:{
                required:true
            },
            bg_image:{
                required:true
            },
            email:{
                required:true,
                maxlength:32,
                email:true
            },
            name:{
                required:true,
                maxlength:32
            },
            tel:{
                required:true,
                maxlength:32
            },
            address:{
                required:true,
                maxlength:128
            }
        },
        messages:{
            image:{
                required:config.validErrors.required
            },
            bg_image:{
                required:config.validErrors.required
            },
            email:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32),
                email:config.validErrors.email
            },
            name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            tel:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            address:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",128)
            }
        },
        submitHandler:function(form) {
            designerUpdate.submitForm(form);
        }
    });


});


