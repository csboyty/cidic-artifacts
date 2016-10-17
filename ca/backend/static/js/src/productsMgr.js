var productsMgr=(function(config,functions){

    var childData={};
    var currentProId=0;

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.productsGetAll,
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
                { "mDataProp": "more",
                    "fnRender":function(oObj) {
                        return '<span class="detailController glyphicon glyphicon-plus"></span>';
                    }
                },
                { "mDataProp": "image",
                    "fnRender":function(oObj){
                        return "<img class='thumb' src='"+oObj.aData.image+"'>";
                    }},
                { "mDataProp": "name",
                    "fnRender":function(oObj){
                        return "<a target='_blank' href='../products/"+oObj.aData.id+"'>"+oObj.aData.name+"</a>";
                    }},
                { "mDataProp": "sell_type",
                    "fnRender":function(oObj){
                        return config.types.product[oObj.aData.sell_type];
                    }},
                { "mDataProp": "status",
                    "fnRender":function(oObj){
                        return config.status.product[oObj.aData.status];
                    }},
                { "mDataProp": "has_items",
                    "fnRender":function(oObj){
                        return oObj.aData.has_items?"是":config.messages.productCanNotShow;
                    }},
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        var string="";
                        if(oObj.aData.status==config.status.product["-1"]){
                            string='<a href="'+oObj.aData.id+'" data-target-status="1" class="soldOut">上架</a>';
                        }else{
                            string='<a href="manager/products/'+oObj.aData.id+'/update">修改</a>&nbsp;&nbsp;' +
                                '<a href="'+oObj.aData.id+'" class="addChild">添加子项</a>&nbsp;&nbsp;'+
                                '<a href="'+oObj.aData.id+'" data-target-status="-1" class="soldOut">下架</a>';
                        }

                        string+='&nbsp;<a href="'+oObj.aData.id+'" class="bindData">绑定信息</a>&nbsp;';

                        return string;
                    }
                }
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    name:"name",
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
                                response.aaData[i].opt="opt";
                                response.aaData[i].more="more";
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
        soldOut:function(id,status){
            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.productSoldOut.replace(":id",id),
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
        },
        showDetail:function(el){
            var me=this,
                tr = el.closest('tr')[0],
                id=currentProId=this.ownTable.fnGetData(tr)["id"];

            if ( this.ownTable.fnIsOpen(tr) ){
                el.removeClass('shown glyphicon-minus').addClass("glyphicon-plus");
                this.ownTable.fnClose( tr );
            }else{
                functions.showLoading();


                $.ajax({
                    url:config.ajaxUrls.proChildGetAll.replace(":id",id),
                    type:"get",
                    dataType:"json",
                    success:function(response){
                        if(response.success){
                            el.addClass('shown glyphicon-minus').removeClass("glyphicon-plus");
                            me.ownTable.fnOpen( tr, me.detailContent(response.product_items), 'details' );
                            for(var i= 0,len=response.product_items.length;i<len;i++){
                                childData[response.product_items[i].id]=response.product_items[i];
                            }

                            functions.hideLoading();
                        }else{
                            functions.ajaxReturnErrorHandler(response.error_code);
                        }

                    },
                    error:function(){
                        functions.ajaxErrorHandler();
                    }
                });

            }
        },
        detailContent:function(records){
            var string='<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;width:100%">' +
                '<tr><td>规格</td><td>价格</td><td>库存</td></tr>';

            //for循环添加tr
            for(var i= 0,length=records.length;i<length;i++){
                string+="<tr><td>"+records[i].spec+"</td><td>"+records[i].price+"</td>" +
                    "<td>"+records[i].quantity+"</td>" +
                    "<td><a href='"+records[i].id+"' class='editChild'>修改</a>&nbsp;" +
                    "<a href='"+records[i].id+"' class='deleteChild'>删除</a>&nbsp;" +
                    "<a href='"+records[i].id+"' class='updateInStore'>修改库存</a></td></tr>";
            }

            return string+"</table>";
        },
        updateInStoreFormSubmit:function(form){
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
                        $("#updateInStoreModal").modal("hide");
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        updateInStore:function(childId){
            $("#updateInStoreForm").attr("action",function(index,text){
                text=$(this).data("action");
                return text.replace(":proId",currentProId).replace(":itemId",childId);
            });
            $("#updateInStoreModal").modal("show");
        },
        addOrUpdateFormSubmit:function(form){
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
                        $("#addChildModal,#updateChildModal").modal("hide");
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        addChild:function(proId){
            $("#addChildForm").attr("action",function(index,text){

                text=$(this).data("action");
                return text.replace(":id",proId);
            });
            $("#addChildModal").modal("show");
        },
        deleteChild:function(itemId){
            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.proChildDelete.replace(":proId",currentProId).replace(":itemId",itemId),
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
        updateChild:function(childId){
            var data=childData[childId];

            $("#updateChildForm").attr("action",function(index,text){
                text=$(this).data("action");
                return text.replace(":proId",currentProId).replace(":itemId",childId);
            });

            $("#updateSpec").val(data.spec);
            $("#updatePrice").val(data.price);
            $("#updateChildModal").modal("show");
        },
        getAllThinsBinded:function(id){
            var me=this;
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.productBinds.replace(":id",id),
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
            $("#bHome").val(data.recommend);
            $(".selectedContainer").html("");

            //设置group
            if(data.group.length!=0){
                html=juicer(tpl,{
                    id:data.group[0][0],
                    name:data.group[0][1]
                });
                $("#selectedGroups").html(html);
            }
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
            //设置手工艺人
            if(data.craftsmans.length!=0){
                html="";
                for(var j= 0,length=data.craftsmans.length;j<length;j++){
                    html+=juicer(tpl,{
                        id:data.craftsmans[j][0],
                        name:data.craftsmans[j][1]
                    });
                }

                $("#selectedHandicraftsMans").html(html);
            }
            //设置设计灵感
            if(data.inspiration.length!=0){
                html=juicer(tpl,{
                    id:data.inspiration[0][0],
                    name:data.inspiration[0][1]
                });
                $("#selectedDesignIns").html(html);
            }
            //设置工作坊
            if(data.workshop.length!=0){
                html=juicer(tpl,{
                    id:data.workshop[0][0],
                    name:data.workshop[0][1]
                });
                $("#selectedWorkShops").html(html);
            }
            //设置夏令营
            if(data.activity.length!=0){
                html=juicer(tpl,{
                    id:data.activity[0][0],
                    name:data.activity[0][1]
                });
                $("#selectedSummerCamps").html(html);
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
        recommendFormSubmit:function(form){

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
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        bindProGroupsFormSubmit:function(form){
            functions.showLoading();
            var formObj=$(form).serializeObject();
            formObj.group_id=$("#selectedGroups .item").eq(0).data("id");

            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });

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
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        bindHandicraftsMansFormSubmit:function(form){
            functions.showLoading();
            var formObj=$(form).serializeObject();
            formObj.craftsman_ids=[];
            $("#selectedHandicraftsMans .item").each(function(index,el){
                formObj.craftsman_ids.push($(this).data("id"));
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
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });

        },
        bindDesignInsFormSubmit:function(form){
            functions.showLoading();
            var formObj=$(form).serializeObject();
            formObj.inspiration_id=$("#selectedDesignIns .item").eq(0).data("id");

            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        bindWorkShopsFormSubmit:function(form){
            functions.showLoading();
            var formObj=$(form).serializeObject();
            formObj.workshop_id=$("#selectedWorkShops .item").eq(0).data("id");

            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });

        },
        bindSummerCampsFormSubmit:function(form){
            functions.showLoading();
            var formObj=$(form).serializeObject();
            formObj.activity_id=$("#selectedSummerCamps .item").eq(0).data("id");

            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
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

    productsMgr.createTable();

    $("#searchBtn").click(function(e){
        productsMgr.tableRedraw();
    });

    $(".selectedContainer").on("click",".item",function(){
        $(this).remove();
    });

    $(".form-group").on("click",".item",function(){
        $(this).remove();
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
    $('#searchGroups').marcoPolo({
        url:config.ajaxUrls.productGroupsGetAll,
        param:"name",
        minChars:2,
        formatData:function(data){
            return data.aaData;
        },
        formatItem: function (data, $item) {
            return data.name;
        },
        onSelect: function (data, $item) {
            if($("#selectedGroups .item").length==0){
                var tpl=$("#selectedTpl").html();
                var html=juicer(tpl,data);
                $("#selectedGroups").append(html);
            }
        }
    });
    $('#searchDesignIns').marcoPolo({
        url:config.ajaxUrls.designInspirationsGetAll,
        param:"title",
        minChars:2,
        formatData:function(data){
            return data.aaData;
        },
        formatItem: function (data, $item) {
            data.name=data.title;
            return data.name;
        },
        onSelect: function (data, $item) {
            if($("#selectedDesignIns .item").length==0){
                var tpl=$("#selectedTpl").html();
                var html=juicer(tpl,data);
                $("#selectedDesignIns").append(html);
            }
        }
    });
    $('#searchWorkShops').marcoPolo({
        url:config.ajaxUrls.workShopsGetAll,
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
            $("#selectedWorkShops").append(html);
        }
    });
    $('#searchSummerCamps').marcoPolo({
        url:config.ajaxUrls.summerCampsGetAll,
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
            $("#selectedSummerCamps").append(html);
        }
    });
    $('#searchHandicraftsMans').marcoPolo({
        url:config.ajaxUrls.handicraftsMansGetAll,
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
            $("#selectedHandicraftsMans").append(html);
        }
    });

    $("#bindHome").submit(function(){
        productsMgr.recommendFormSubmit($(this));
        return false;
    });
    $("#bindDesigners").submit(function(){
        productsMgr.bindDesignersFormSubmit($(this));
        return false;
    });
    $("#bindDesignIns").submit(function(){
        productsMgr.bindDesignInsFormSubmit($(this));
        return false;
    });
    $("#bindProGroups").submit(function(){
        productsMgr.bindProGroupsFormSubmit($(this));
        return false;
    });
    $("#bindWorkShops").submit(function(){
        productsMgr.bindWorkShopsFormSubmit($(this));
        return false;
    });
    $("#bindSummerCamps").submit(function(){
        productsMgr.bindSummerCampsFormSubmit($(this));
        return false;
    });
    $("#bindHandicraftsMans").submit(function(){
        productsMgr.bindHandicraftsMansFormSubmit($(this));
        return false;
    });


    $("#myTable").on("click","a.soldOut",function(){
        if(confirm(config.messages.confirm)){
            productsMgr.soldOut($(this).attr("href"),$(this).data("target-status"));
        }
        return false;
    }).on("click",".detailController",function(){
            productsMgr.showDetail($(this));
    }).on("click","a.editChild",function(){
        productsMgr.updateChild($(this).attr("href"));
        return false;
    }).on("click","a.addChild",function(){
            productsMgr.addChild($(this).attr("href"));
            return false;
    }).on("click","a.deleteChild",function(){
            productsMgr.deleteChild($(this).attr("href"));
            return false;
    }).on("click","a.updateInStore",function(){
        productsMgr.updateInStore($(this).attr("href"));
        return false;
    }).on("click","a.bindData",function(){
            productsMgr.bindData($(this).attr("href"));
            return false;
        });

    /*$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        console.log(e.target.hash);
    });*/


    $("#addChildForm").validate({
        ignore:[],
        rules:{
            spec:{
                required:true,
                maxlength:32
            },
            price:{
                required:true,
                maxlength:6
            },
            quantity:{
                required:true,
                number:true,
                maxlength:6
            }
        },
        messages:{
            spec:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            price:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",6)
            },
            quantity:{
                required:config.validErrors.required,
                number:config.validErrors.number,
                maxlength:config.validErrors.maxLength.replace("${max}",6)
            }
        },
        submitHandler:function(form) {
            productsMgr.addOrUpdateFormSubmit(form);
        }
    });
    $("#updateChildForm").validate({
        ignore:[],
        rules:{
            name:{
                required:true,
                maxlength:32
            },
            price:{
                required:true,
                maxlength:12
            }
        },
        messages:{
            name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            price:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",12)
            }
        },
        submitHandler:function(form) {
            productsMgr.addOrUpdateFormSubmit(form);
        }
    });
    $("#updateInStoreForm").validate({
        ignore:[],
        rules:{
            inStore:{
                required:true,
                maxlength:6
            }
        },
        messages:{
            inStore:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",6)
            }
        },
        submitHandler:function(form) {
            productsMgr.updateInStoreFormSubmit(form);
        }
    });
});

