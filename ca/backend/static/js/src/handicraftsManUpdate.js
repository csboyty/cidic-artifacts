var handicraftsManUpdate=(function(config,functions){

    return {
        submitForm:function(form){
            functions.showLoading();
            var formObj=$(form).serializeObject();
            formObj.intro=tinyMCE.editors[0].getContent();

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
                        functions.timeoutRedirect("manager/craftsmans/");
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

    tinymce.init({
        selector: "#intro",
        height:300,
        toolbar1: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
        toolbar2: 'print preview media | forecolor backcolor emoticons',
        //image_advtab: true,
        plugins : 'link image preview fullscreen table textcolor colorpicker code'
    });


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
            name:{
                required:true,
                maxlength:32
            },
            tel:{
                required:true,
                maxlength:32
            },
            skills:{
                required:true,
                maxlength:64
            },
            resident_place:{
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
            name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            tel:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            skills:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",64)
            },
            resident_place:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",128)
            }
        },
        submitHandler:function(form) {
            handicraftsManUpdate.submitForm(form);
        }
    });


});


