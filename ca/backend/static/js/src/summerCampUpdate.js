var summerCampUpdate=(function(config,functions){
    return{
        submitForm:function(form){
            var formObj=$(form).serializeObject();
            formObj.intro=tinyMCE.editors[0].getContent();
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
                            window.location.href=document.getElementsByTagName('base')[0].href+"manager/activities/";
                        },3000);
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
        maxSize:config.uploader.sizes.img,
        filter:config.uploader.filters.img,
        uploadBtn:"uploadBtn",
        multiSelection:false,
        multipartParams:null,
        uploadContainer:"uploadContainer",
        fileAddCb:null,
        progressCbk:null,
        uploadedCb:function(info,file,up){
            var path=info.url;
            $.get(path+"?imageInfo",function(data){
                //console.log(data);
                if(data.width==500&&data.height==500){
                    $("#imageUrl").val(path);

                    $("#image").attr("src",path);

                    $(".error[for='imageUrl']").remove();
                }else{
                    $().toastmessage("showErrorToast",config.messages.imageNot500x500);
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


    tinymce.init({
        selector: "#intro",
        height:300,
        toolbar1: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
        toolbar2: 'print preview media | forecolor backcolor emoticons',
        //image_advtab: true,
        plugins : 'link image preview fullscreen table textcolor colorpicker code'

    });

    $("#myForm").validate({
        ignore:[],
        rules:{
            image:{
                required:true
            },
            url:{
                required:true
            },
            year:{
                maxlength:12
            },
            bg_image:{
                required:true
            },
            name:{
                required:true,
                maxlength:32
            }
        },
        messages:{
            image:{
                required:config.validErrors.required
            },
            url:{
                required:config.validErrors.required
            },
            year:{
                maxlength:config.validErrors.maxLength.replace("${max}",12)
            },
            bg_image:{
                required:config.validErrors.required
            },
            name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            }
        },
        submitHandler:function(form) {
            summerCampUpdate.submitForm(form);
        }
    });
});