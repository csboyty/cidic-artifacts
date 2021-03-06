var userAddresses=(function(){
    return {
        setDefault:function(id){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.addressSetDefault.replace(":userId",userId).replace(":addressId",id),
                type:"post",
                dataType:"json",
                success:function(response){
                    if(response.success){
                        window.location.reload();
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        },
        delete:function(el){
            functions.showLoading();
            var id =el.data("id");
            $.ajax({
                url:config.ajaxUrls.addressDelete.replace(":userId",userId).replace(":addressId",id),
                type:"post",
                dataType:"json",
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
                        el.parents("li").remove();
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        }
    }
})();
$(document).ready(function(){
    $("#addresses").on("click",".setDefault",function(){
        userAddresses.setDefault($(this).data("id"));
    }).on("click",".delete",function(){
        if(confirm(config.messages.confirmDelete)){
            userAddresses.delete($(this));
        }
    });
});