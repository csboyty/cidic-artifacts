var userOrders=(function(config,functions){
    return {
        orderReceipt:function(orderNo){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.orderReceipt.replace(":orderNo",orderNo),
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
        orderCancel:function(orderNo){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.orderCancel.replace(":orderNo",orderNo),
                type:"post",
                dataType:"json",
                data:{
                    cancel_text:""
                },
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
        }
    }
})(config,functions);
$(document).ready(function(){
    $(".status").text(function(index,text){
        return config.status.order[text];
    });

    common.initPagination(config.pageUrls.designer);

    $("#orders").on("click",".receipt",function(){
        userOrders.orderReceipt($(this).attr("href"));
        return false;
    }).on("click",".cancel",function(){
            userOrders.orderCancel($(this).attr("href"));
            return false;
        });
});