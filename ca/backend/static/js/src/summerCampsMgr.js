var summerCampsMgr=(function(config,functions){

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.summerCampsGetAll,
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
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        var string= '<a  href="manager/activities/'+oObj.aData.id+'/update">修改</a>&nbsp;' +
                            '<a href="'+oObj.aData.id+'" class="delete">删除</a>';

                        string+='&nbsp;<a href="'+oObj.aData.id+'" class="bindData">绑定信息</a>&nbsp;';
                        return string;
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
                url:config.ajaxUrls.summerCampDelete.replace(":id",id),
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
        getAllThinsBinded:function(id){
            var me=this;
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.summerCampBinds.replace(":id",id),
                type:"get",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                success:function(response){
                    if(response.success){
                        functions.hideLoading();

                        me.setBinds(response);

                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        setBinds:function(data){
            var tpl=$("#selectedTpl").html(),
                html;
            $(".selectedContainer").html("");

            //设置designers
            if(data.designers.length!=0){
                html="";
                for(var i= 0,len=data.designers.length;i<len;i++){
                    html+=juicer(tpl,{
                        id:data.designers[i][0],
                        name:data.designers[i][1]
                    });
                }

                $("#selectedDesigners").html(html);
            }
        },
        bindData:function(id){
            this.getAllThinsBinded(id);

            $(".myForm").attr("action",function(index,text){
                text=$(this).data("action");
                return text.replace(":id",id);
            });
            //load数据
            $("#bindModal").modal("show");
        },

        bindDesignersFormSubmit:function(form){
            functions.showLoading();
            var formObj=$(form).serializeObject();
            formObj.designer_ids=[];
            $("#selectedDesigners .item").each(function(index,el){
                formObj.designer_ids.push($(this).data("id"));
            });

            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
                        $("#bindModal").modal("hide");
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
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

    summerCampsMgr.createTable();

    $("#searchBtn").click(function(e){
        summerCampsMgr.tableRedraw();
    });
    $('#searchDesigners').marcoPolo({
        url:config.ajaxUrls.designersGetAll,
        param:"name",
        minChars:2,
        formatData:function(data){
            return data.aaData;
        },
        formatItem: function (data, $item) {
            return data.name;
        },
        onSelect: function (data, $item) {
            var tpl=$("#selectedTpl").html();
            var html=juicer(tpl,data);
            $("#selectedDesigners").append(html);
        }
    });
    $("#bindDesigners").submit(function(){
        summerCampsMgr.bindDesignersFormSubmit($(this));
        return false;
    });
    $(".selectedContainer").on("click",".item",function(){
        $(this).remove();
    });
    $("#myTable").on("click","a.delete",function(){
        if(confirm(config.messages.confirmDelete)){
            summerCampsMgr.delete($(this).attr("href"));
        }
        return false;
    }).on("click","a.bindData",function(){
            summerCampsMgr.bindData($(this).attr("href"));
            return false;
        });
});

