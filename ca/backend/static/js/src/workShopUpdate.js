var workShopUpdate=(function(config,functions){
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
                        $().toastmessage("showSuccessToast",config.messages.optSuccRedirect);
                        setTimeout(function(){
                            window.location.href=document.getElementsByTagName('base')[0].href+"manager/workshops/";
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
            name:{
                required:true,
                maxlength:32
            },
            memo:{
                required:true,
                maxlength:100
            }
        },
        messages:{
            image:{
                required:config.validErrors.required
            },
            name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            memo:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",100)
            }
        },
        submitHandler:function(form) {
            workShopUpdate.submitForm(form);
        }
    });
});