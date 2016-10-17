var commentsMgr=(function(config,functions){
    var loadedData={};
    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.commentsGetAll,
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
                { "mDataProp": "content"},
                { "mDataProp": "author_nick_name"},
                { "mDataProp": "product_name",
                    "fnRender":function(oObj){
                        return "<a target='_blank' href='../products/"+oObj.aData.product_id+"'>"+oObj.aData["product_name"]+"</a>";
                    }},
                { "mDataProp": "reply",
                    "fnRender":function(oObj){
                        var string="";
                        if(oObj.aData.reply){
                            string=oObj.aData.reply.content;
                        }
                        return string;
                    }},
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        return '<a href="'+oObj.aData.id+'" class="reply">回复</a>&nbsp;' +
                            '<a href="'+oObj.aData.id+'" class="delete">删除</a>';
                    }
                }
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    name:"content",
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
                                loadedData[response.aaData[i].id]=response.aaData[i];
                                response.aaData[i].author_nick_name=response.aaData[i]["author.nick_name"];
                                response.aaData[i].product_name=response.aaData[i]["product.name"];
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
                url:config.ajaxUrls.commentsDelete.replace(":id",id),
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
        reply:function(id){
            $("#replyForm").attr("action",function(index,text){
                text=$(this).data("action");
                return  text.replace(":id",id);
            });
            $("#commentContent").text(loadedData[id].content);
            $("#replyModal").modal("show");
        },
        replyFormSubmit:function(form){
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
                        $("#replayModal").modal("hide");
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

    commentsMgr.createTable();

    $("#searchBtn").click(function(e){
        commentsMgr.tableRedraw();
    });

    $("#myTable").on("click","a.delete",function(){
        if(confirm(config.messages.confirmDelete)){
            commentsMgr.delete($(this).attr("href"));
        }
        return false;
    }).on("click","a.reply",function(){
            commentsMgr.reply($(this).attr("href"));
            return false;
        });

    $("#replyForm").validate({
        ignore:[],
        rules:{
            content:{
                required:true,
                maxlength:50
            }
        },
        messages:{
            content:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",50)
            }
        },
        submitHandler:function(form) {
            commentsMgr.replyFormSubmit(form);
        }
    });
});

