var userMgr=(function(config,functions){

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.userGetAll,
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
                { "mDataProp": "nick_name"},
                { "mDataProp": "email"},
                { "mDataProp": "tel"},
                { "mDataProp": "active",
                    "fnRender":function(oObj){
                        return config.status.user[oObj.aData.active];
                    }},
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        if(oObj.aData.active==config.status.user[true]){
                            return '<a href="'+oObj.aData.id+'" class="handle">禁用</a>';
                        }else{
                            return '<a href="'+oObj.aData.id+'" class="handle">激活</a>';
                        }

                    }
                }
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    "name":"content",
                    "value":$("#searchContent").val()
                });
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
                                response.aaData[i].opt="opt";
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
        handle:function(id){
            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.userDisable.replace(":id",id),
                type:"post",
                dataType:"json",
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

    userMgr.createTable();

    $("#searchBtn").click(function(e){
        userMgr.tableRedraw();
    });

    $("#myTable").on("click","a.handle",function(){
        userMgr.handle($(this).attr("href"));
        return false;
    });
});

