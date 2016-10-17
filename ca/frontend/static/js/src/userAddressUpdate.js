var userAddressUpdate=(function(config,functions){
    return {
        initSelectGroup:function(){
            // 设置全局默认值，需在引入 <script src="jquery.cxselect.js"></script> 之后，调用之前设置
            $.cxSelect.defaults.url = config.ajaxUrls.cities; // 提示：如果服务器不支持 .json 类型文件，请将文件改为 .js 文件
            $.cxSelect.defaults.nodata = '';
            $.cxSelect.defaults.firstValue = '';

            // selects 为数组形式，请注意顺序
            $('#selectGroup').cxSelect({
                selects: ['province','city','area'],
                nodata: '',
                required:false
            });
        },
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
                            window.location.href=document.getElementsByTagName('base')[0].href+
                                "accounts/"+userId+"/addresses";
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
    userAddressUpdate.initSelectGroup();

    $("#myForm").validate({
        ignore:[],
        rules:{
            fullName:{
                required:true,
                maxlength:32
            },
            phone:{
                required:true,
                maxlength:16
            },
            phone1:{
                required:true,
                maxlength:16
            },
            loc_address:{
                required:true,
                maxlength:64
            },
            loc_state:{
                required:true
            },
            loc_city:{
                required:true
            }
        },
        messages:{
            fullName:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            phone:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",16)
            },
            phone1:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",16)
            },
            loc_address:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",64)
            },
            loc_state:{
                required:config.validErrors.required
            },
            loc_city:{
                required:config.validErrors.required
            }
        },
        submitHandler:function(form) {
            userAddressUpdate.submitForm(form);
        }
    });
});