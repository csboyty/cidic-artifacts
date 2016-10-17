var userProfile=(function(config,functions){
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
                        window.location.reload();
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
        uploadBtn:"photoUpload",
        multiSelection:false,
        multipartParams:null,
        uploadContainer:"photoContainer",
        fileAddCb:null,
        progressCb:null,
        uploadedCb:function(info,file,up){

            var path=info.url;
            $("#photoUrl").val(path);
            $("#photo").attr("src",path);
        }
    });

    $("#myForm").validate({
        rules: {
            nick_name:{
                required:true,
                maxlength:20
            },
            email: {
                email:true,
                maxlength:30,
                remote:{
                    url: config.ajaxUrls.checkEmailExist,     //后台处理程序
                    type: "get",               //数据发送方式
                    dataType: "json",           //接受数据格式
                    data: {                     //要传递的数据
                        email:function() {
                            var value=$("#email").val();
                            return value==oldEmail?"":value;
                        }
                    }
                }
            }
        },
        messages: {
            nick_name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",20)
            },
            email: {
                email:config.validErrors.email,
                maxlength:config.validErrors.maxLength.replace("${max}",30),
                remote:config.validErrors.emailExist
            }
        },
        submitHandler:function(form){
            userProfile.submitForm(form)
        }
    });
});