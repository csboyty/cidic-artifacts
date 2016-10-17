var products=(function(config){
    return {
        showSome:function(){
            if($("#productsList li.hidden").length!=0){
                $("#productsList li.hidden").slice(0,config.perLoadCounts.scroll).
                    removeClass("hidden").addClass("show");
            }else{
                $('#ownPagination').removeClass("hidden");
                return false;
            }

            return true;
        }
    }
})(config);
$(document).ready(function(){
    common.initShow(products.showSome);
    common.windowScroll(products.showSome);
    common.initPagination(config.pageUrls.designer);
});
