var designerAppliedMgr=(function(config,functions){

    var loadedData={};

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.designerAppliesGetAll,
            "bInfo":true,
            "bLengthChange": false,
            "bFilter": false,
            "bSort":false,
            "bAutoWidth": false,
            "iDisplayLength":config.perLoadCounts.table,
            "sPaginationType":"full_numbers",
            "oLanguage": {
                "sUrl":config.dataTable.langUrl
            },
            "aoColumns": [
                { "mDataProp": "name"},
                { "mDataProp": "email"},
                { "mDataProp": "tel"},
                { "mDataProp": "status",
                    "fnRender":function(oObj){
                        return config.status.Apply[oObj.aData.status];
                    }},
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        var string= "<a class='check' href='"+oObj.aData.id+"'>查看</a>&nbsp;";

                        if(oObj.aData.oldStatus==0){
                            string+='<a href="'+oObj.aData.id+'" data-target-status="1" class="handle">同意</a>&nbsp;' +
                                '<a href="'+oObj.aData.id+'" data-target-status="-1" class="handle">拒绝</a>';
                        }

                        return string;
                    }}
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    name:"query",
                    value:$("#searchContent").val()
                },{
                    name:"status",
                    value:$("#searchStatus").val()
                })
            },
            "fnServerData": function(sSource, aoData, fnCallback) {

                //回调函数
                $.ajax({
                    "dataType":'json',
                    "type":"get",
                    "url":sSource,
                    "data":aoData,
                    "success": function (response) {
                        if(response.success===false){
                            functions.ajaxReturnErrorHandler(response.error_code);
                        }else{
                            var json = {
                                "sEcho" : response.sEcho
                            };

                            for (var i = 0, iLen = response.aaData.length; i < iLen; i++) {
                                response.aaData[i].opt="";
                                response.aaData[i].oldStatus=response.aaData[i].status;
                                loadedData[response.aaData[i].id]=response.aaData[i];
                            }

                            json.aaData=response.aaData;
                            json.iTotalRecords = response.iTotalRecords;
                            json.iTotalDisplayRecords = response.iTotalDisplayRecords;
                            fnCallback(json);
                        }

                    }
                });
            },
            "fnFormatNumber":function(iIn){
                return iIn;
            }
        });

        return ownTable;
    }

    return {
        ownTable:null,
        createTable:function(){
            this.ownTable=createTable();
        },
        tableRedraw:function(){
            this.ownTable.fnSettings()._iDisplayStart=0;
            this.ownTable.fnDraw();
        },
        check:function(id){
            var tpl=$("#detailTpl").html();
            var html=juicer(tpl,loadedData[id]);
            $("#detailBody").html(html);
            $("#detailModal").modal("show");
        },
        handle:function(id,status){
            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.designerApplyHandle.replace(":id",id),
                type:"post",
                dataType:"json",
                data:{
                    status:status
                },
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        me.ownTable.fnDraw();
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

    designerAppliedMgr.createTable();

    $("#searchBtn").click(function(e){
        designerAppliedMgr.tableRedraw();
    });

    $("#myTable").on("click","a.check",function(){
        designerAppliedMgr.check($(this).attr("href"));
        return false;
    }).on("click","a.handle",function(){
            if(confirm(config.messages.confirm)){
                designerAppliedMgr.handle($(this).attr("href"),$(this).data("target-status"));
            }
            return false;
        });
});

