var designers=(function(config){
    return {
        showSome:function(){
            if($("#designersList li.hidden").length!=0){
                $("#designersList li.hidden").slice(0,config.perLoadCounts.scroll).
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
    common.initShow(designers.showSome);
    common.windowScroll(designers.showSome);
    common.initPagination(config.pageUrls.order);
});
