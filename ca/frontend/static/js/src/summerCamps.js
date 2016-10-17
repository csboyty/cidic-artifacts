var summerCamps=(function(config){
    return {
        showSome:function(){
            if($("#summerCampsList li.hidden").length!=0){
                $("#summerCampsList li.hidden").slice(0,config.perLoadCounts.scroll).
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
    common.initShow(summerCamps.showSome);
    common.windowScroll(summerCamps.showSome);
    common.initPagination(config.pageUrls.designer);
});
