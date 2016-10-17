var ordersRefund=(function(config,functions){

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.orderRefundGetAll,
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
                { "mDataProp": "status",
                    "fnRender":function(oObj){
                        return config.status.order[oObj.aData.status];
                    }},
                { "mDataProp": "created"},
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        return "<a class='check' href='"+oObj.aData.no+"'>查看</a>&nbsp;";
                    }}
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    name:"order_no",
                    value:$("#searchContent").val()
                },{
                    name:"status",
                    value:"order-apply-refund"
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
                                var status=response.aaData[i].code;
                                response.aaData[i]=response.aaData[i].Order;
                                response.aaData[i].status=status;
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
        check:function(id){
            var me=this;
            $.ajax({
                url:config.ajaxUrls.orderDetail.replace(":id",id),
                type:"get",
                dataType:"json",
                success:function(response){
                    if(response.success){
                        //load数据
                        var tpl=$("#detailTpl").html();
                        var html=juicer(tpl,response);
                        $("#detailBody").html(html);
                        $("#detailModal").modal("show");
                        me.formValidate();
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        refuseFormSubmit:function(form){
            var me=this;
            functions.showLoading();
            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                data:$(form).serializeObject(),
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        me.tableRedraw();
                        $("#detailModal").modal("hide");
                        $(form)[0].reset();
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        formValidate:function(){
            var me=this;
            $("#refuseForm").validate({
                ignore:[],
                rules:{
                    content:{
                        required:true,
                        maxlength:100
                    }
                },
                messages:{
                    content:{
                        required:config.validErrors.required,
                        maxlength:config.validErrors.maxLength.replace("${max}",100)
                    }
                },
                submitHandler:function(form) {
                    me.refuseFormSubmit(form);
                }
            });
        },
        yes:function(id){
            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.orderHandleRefund.replace(":id",id),
                type:"post",
                dataType:"json",
                data:{
                    result:1
                },
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        me.tableRedraw();
                        $("#detailModal").modal("hide");
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

    ordersRefund.createTable();

    $("#searchBtn").click(function(e){
        ordersRefund.tableRedraw();
    });

    $("#myTable").on("click","a.check",function(){
            ordersRefund.check($(this).attr("href"));
            return false;
        });

    $("#detailBody").on("click","#yes",function(){
        ordersRefund.yes($(this).data("order-id"));
    });

    $("#refuseForm").validate({
        ignore:[],
        rules:{
            content:{
                required:true,
                maxlength:100
            }
        },
        messages:{
            content:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",100)
            }
        },
        submitHandler:function(form) {
            ordersRefund.refuseFormSubmit(form);
        }
    });
});

