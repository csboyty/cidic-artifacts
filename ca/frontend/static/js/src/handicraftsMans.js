var handicraftsMans=(function(config){
    return {
        showSome:function(){
            if($("#handicraftsMansList li.hidden").length!=0){
                $("#handicraftsMansList li.hidden").slice(0,config.perLoadCounts.scroll).
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
    common.initShow(handicraftsMans.showSome);
    common.windowScroll(handicraftsMans.showSome);
    common.initPagination(config.pageUrls.designer);
});
