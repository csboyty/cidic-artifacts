var designInspirationUpdate=(function(config,functions){
    return{
        submitForm:function(form){
            var formObj=$(form).serializeObject();
            formObj.designer_ids=[];
            formObj.intro=tinyMCE.editors[0].getContent();
            $("#designers .item").each(function(index,el){
                formObj.designer_ids.push($(el).data("id"));
            });
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
                            window.location.href=document.getElementsByTagName('base')[0].href+"manager/inspirations/";
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
    tinymce.init({
        selector: "#intro",
        height:300,
        toolbar1: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
        toolbar2: 'print preview media | forecolor backcolor emoticons',
        //image_advtab: true,
        plugins : 'link image preview fullscreen table textcolor colorpicker code'

    });

    $('#searchDesigners').marcoPolo({
        url:config.ajaxUrls.designersGetAll,
        param:"name",
        minChars:2,
        formatData:function(data){
            return data.aaData;
        },
        formatItem: function (data, $item) {
            return data.name;
        },
        onSelect: function (data, $item) {
            var tpl=$("#designerTpl").html();
            var html=juicer(tpl,data);
            $("#designers").append(html);
        }
    });

    $("#designers").on("click",".item",function(){
        $(this).remove();
    });

    $("#myForm").validate({
        ignore:[],
        rules:{
            title:{
                required:true,
                maxlength:32
            },
            name:{
                required:true
            }
        },
        messages:{
            title:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            name:{
                required:config.validErrors.required
            }
        },
        submitHandler:function(form) {
            designInspirationUpdate.submitForm(form);
        }
    });
});