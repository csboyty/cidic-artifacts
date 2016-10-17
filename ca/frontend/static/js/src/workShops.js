var workShops=(function(config){
    return {
        showSome:function(){
            if($("#workShopsList li.hidden").length!=0){
                $("#workShopsList li.hidden").slice(0,config.perLoadCounts.scroll).
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
    common.initShow(workShops.showSome);
    common.windowScroll(workShops.showSome);
    common.initPagination(config.pageUrls.designer);
});
