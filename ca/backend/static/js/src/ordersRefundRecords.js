var ordersRefundRecords=(function(config,functions){

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.orderRefundRecordsGetAll,
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
                { "mDataProp": "no"},
                { "mDataProp":"refund_url",
                    "fnRender":function(oObj){
                        var string="";
                        if(oObj.aData.status=="-99"){
                            string=config.messages.refunding;

                            if(oObj.aData.refund_url){
                                string="<a href='"+oObj.aData.refund_url+"' target='_blank'>"+config.messages.refundInAli+"</a>";
                            }
                        }

                        return string;
                    }},
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        var string="";
                        if(oObj.aData.status!="-99"){
                            string= "<a class='refund' data-order-no='"+oObj.aData.no+"' href='"+oObj.aData.id+"'>退款</a>";
                        }

                        return string;
                    }}
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    name:"order_no",
                    value:$("#searchContent").val()
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
        refund:function(orderNo,id){
            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.orderRecordsHandle.replace(":orderNo",orderNo).replace(":id",id),
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

    ordersRefundRecords.createTable();

    $("#searchBtn").click(function(e){
        ordersRefundRecords.tableRedraw();
    });

    $("#myTable").on("click","a.refund",function(){
        if(confirm(config.messages.confirm)){
            ordersRefundRecords.refund($(this).data("order-no"),$(this).attr("href"));
        }
        return false;
    })
});

