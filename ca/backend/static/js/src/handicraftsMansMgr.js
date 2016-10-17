var handicraftsMansMgr=(function(config,functions){

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.handicraftsMansGetAll,
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
                { "mDataProp": "image",
                    "fnRender":function(oObj){
                        return "<img class='thumb' src='"+oObj.aData.image+"'>";
                    }},
                { "mDataProp": "name",
                    "fnRender":function(oObj){
                        return "<a target='_blank' href='"+oObj.aData.id+"'>"+oObj.aData.name+"</a>";
                    }},
                { "mDataProp": "income"},
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        return '<a href="'+oObj.aData.id+'" class="income">收入</a>&nbsp;' +
                            '<a href="manager/craftsmans/'+oObj.aData.id+'/update">修改</a>&nbsp;' +
                            '<a href="'+oObj.aData.id+'" class="delete">删除</a>';
                    }
                }
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    name:"name",
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
        delete:function(id){
            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.handicraftsManDelete.replace(":id",id),
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
        },
        updateIncomeFormSubmit:function(form){
            var me=this;
            functions.showLoading();
            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify($(form).serializeObject()),
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        me.tableRedraw();
                        $(form)[0].reset();
                        $("#updateIncomeModal").modal("hide");
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        income:function(id){
            $("#updateIncomeForm").attr("action",function(index,text){
                text=$(this).data("action");
                return text.replace(":id",id);
            });
            $("#updateIncomeModal").modal("show");
        }
    }
})(config,functions);

$(document).ready(function(){

    handicraftsMansMgr.createTable();

    $("#searchBtn").click(function(e){
        handicraftsMansMgr.tableRedraw();
    });

    $("#myTable").on("click","a.delete",function(){
        if(confirm(config.messages.confirmDelete)){
            handicraftsMansMgr.delete($(this).attr("href"));
        }
        return false;
    }).on("click","a.income",function(){
            handicraftsMansMgr.income($(this).attr("href"));
            return false;
        });

    $("#updateIncomeForm").validate({
        ignore:[],
        rules:{
            income:{
                required:true,
                maxlength:6
            }
        },
        messages:{
            income:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",6)
            }
        },
        submitHandler:function(form) {
            handicraftsMansMgr.updateIncomeFormSubmit(form);
        }
    });
});

