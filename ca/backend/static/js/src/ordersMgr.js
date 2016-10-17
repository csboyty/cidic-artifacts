var ordersMgr=(function(config,functions){

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.ordersGetAll,
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
                { "mDataProp": "presell",
                    "fnRender":function(oObj){
                        return config.types.order[oObj.aData.presell];
                    }},
                { "mDataProp": "status",
                    "fnRender":function(oObj){
                        return config.status.order[oObj.aData.status];
                    }},
                { "mDataProp": "created"},
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        return "<a class='check' href='"+oObj.aData.no+"'>查看</a>";
                    }}
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    name:"order_no",
                    value:$("#searchContent").val()
                },{
                    name:"status",
                    value:$("#searchStatus").val()
                },{
                    name:"sell_type",
                    value:$("#searchType").val()
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
                                response.aaData[i].opt="";
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
        dispatchFormSubmit:function(form){
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
                        $("#detailModal").modal("hide");
                        me.tableRedraw();
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
            $("#dispatchForm").validate({
                ignore:[],
                rules:{
                    expressId:{
                        required:true,
                        maxlength:20
                    }
                },
                messages:{
                    expressId:{
                        required:config.validErrors.required,
                        maxlength:config.validErrors.maxLength.replace("${max}",20)
                    }
                },
                submitHandler:function(form) {
                    me.dispatchFormSubmit(form);
                }
            });
        }
    }
})(config,functions);

$(document).ready(function(){

    ordersMgr.createTable();

    $("#searchBtn").click(function(e){
        ordersMgr.tableRedraw();
    });

    $("#myTable").on("click","a.check",function(){
        ordersMgr.check($(this).attr("href"));
        return false;
    });
});

