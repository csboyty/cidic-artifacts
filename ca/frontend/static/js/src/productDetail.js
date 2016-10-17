var productDetail=(function(config,functions){
    return {
        loginCallback:null,
        quantityCtrlHandler:function(el){
            var type=el.data("type");
            var quantityContainerEl=el.parent(".quantityContainer");
            var countEl=quantityContainerEl.find(".quantity");
            var decrementEl=quantityContainerEl.find(".quantityCtrl:eq(0)");
            var count=Number(countEl.val());

            if(type=="increment"){
                count++;
            }else{
                count--;
            }

            countEl.val(count);

            if(count!=1){
                decrementEl.removeClass("disabled");
            }else{
                decrementEl.addClass("disabled");
            }
        },
        initCart:function(){
            var items;

            paypal.minicart.render({
                parent:document.body,
                action:"carts",
                strings: {
                    button: '结算',
                    subtotal: '总计:',
                    discount: '折扣:',
                    empty: '您还没有选择商品'
                }
            });

            //清空购物车的所有数据，不从cookie中存储，所有数据都从后台获取
            paypal.minicart.cart.destroy();


            this.getCartItems();
        },
        getCartItems:function(){
            var me=this;
            $.ajax({
                url:config.ajaxUrls.cartItemsGetAll,
                type:"get",
                dataType:"json",
                success:function(data){
                    if(data.success){
                        var item;
                        for(var i= 0,len=data.items.length;i<len;i++){
                            item=data.items[i][0];
                            paypal.minicart.cart.add({
                                item_id:item.id,
                                item_name: item["product.name"]+"-------"+item.spec,
                                quantity:data.items[i][1],
                                amount: Number(item.price).toFixed(2),
                                currency_code: 'CNY'
                            });
                        }

                        paypal.minicart.cart.on("add",me.cartSave);
                        paypal.minicart.cart.on("remove",me.cartSave);
                        paypal.minicart.view.hide();
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(data){
                    functions.ajaxErrorHandler();
                }
            })
        },
        cartSave:function(){
            var items=paypal.minicart.cart.items();
            var dataItems=[];

            for(var i= 0,len=items.length;i<len;i++){
                if(items[i]._data.quantity){
                    dataItems.push([items[i]._data.item_id,items[i]._data.quantity]);
                }
            }
            $.ajax({
                url:config.ajaxUrls.cartAddItem,
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(dataItems),
                success:function(data){
                    if(data.success){

                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(data){
                    functions.ajaxErrorHandler();
                }
            });
        },
        cartAddItem:function(){
            if($("#specs .active").length==0){
                alert("请选择一个尺寸！");
            }else{
                paypal.minicart.cart.add({
                    item_id:$("#specs .active").data("item-id"),
                    item_name: productName+"-------"+$("#specs .active").text(),
                    quantity:$("#quantity").val(),
                    amount: Number($("#price").text()).toFixed(2),
                    currency_code: 'CNY'
                });
            }
        },
        setItemPrice:function(price){
            $("#price").text(price.toFixed(2))
        },
        setItemQuantity:function(quantity){
            $("#allQuantity").text(quantity);
        },
        getItemPrice:function(proId,itemId){
            var me=this;
            $.ajax({
                url:config.ajaxUrls.productItem.replace(":proId",proId).replace(":itemId",itemId),
                type:"get",
                dataType:"json",
                success:function(data){
                    if(data.success){
                        me.setItemPrice(data.item.price);
                        me.setItemQuantity(data.item.quantity);
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(data){
                    functions.ajaxErrorHandler();
                }
            })
        },
        postComments:function(content){
            var data={
                product_id:productId,
                content:content
            };
            var me=this;
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.commentPost.replace(":userId",currentUserId),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(data),
                success:function(data){
                    if(data.success){
                        functions.hideLoading();
                        me.showComment(content);
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(data){
                    functions.ajaxErrorHandler();
                }
            })
        },
        showComment:function(content){
            var tpl=$("#commentTpl").html();
            var html=juicer(tpl,{
                userImage:currentUserImage,
                nickName:currentUserNickName,
                content:content,
                created:functions.formatDate("y-m-d")
            });
            $("#comments").prepend(html);
        },
        loginFormSubmit:function(){
            var me=this;
            $.ajax({
                url:config.ajaxUrls.login,
                type:"post",
                dataType:"json",
                data:{
                    tel:$("#loginTel").val(),
                    password:$("#loginPassword").val()
                },
                success:function(data){
                    if(data.success){
                        if(me.loginCallback){
                            me.loginCallback();
                        }
                    }else{
                        $().toastmessage("showErrorToast",config.messages.loginError);
                    }
                },
                error:function(data){
                    functions.ajaxErrorHandler();
                }
            });
        }
    }
})(config,functions);
$(document).ready(function(){

    productDetail.initCart();

    $('#carousel').flexslider({
        animation: "slide",
        controlNav: false,
        animationLoop: false,
        slideshow: false,
        itemWidth: 120,
        asNavFor: '#slider'
    });

    $('#slider').flexslider({
        animation: "slide",
        controlNav: false,
        animationLoop: false,
        slideshow: false,
        sync: "#carousel"
    });


    $(".quantityCtrl").click(function(){
        if(!$(this).hasClass("disabled")){
            productDetail.quantityCtrlHandler($(this));
        }

    });

    $("#specs .spec").click(function(){
        $("#specs .active").removeClass("active");
        $(this).addClass("active");
        productDetail.getItemPrice(proId,$(this).data("item-id"));
        return false;
    });
    $('#addToCart').click(function (e) {
        e.stopPropagation();
        if($("#quantity").val()>parseInt($("#allQuantity").text())){
            $().toastmessage("showErrorToast",config.messages.quantityError);
        }else{
            productDetail.cartAddItem();
        }

    });

    $("#preSell").click(function(){
        var items=[];
        items.push([$("#specs .active").data("item-id"),parseInt($("#quantity").val())]);
        $("#items").val(JSON.stringify(items));
        if(!currentUserId){
            $("#popWindow").removeClass("hidden");
            productDetail.loginCallback=function(){
                functions.showLoading();
                $("#myForm").submit();
            };
        }else{
            functions.showLoading();
            $("#myForm").submit();
        }
    });

    $("#postComment").click(function(){
        var content=$("#commentContent").val();
        if(content){
            if(!currentUserId){
                $("#popWindow").removeClass("hidden");
                productDetail.loginCallback=function(){
                    window.location.reload();
                };
            }else{
                productDetail.postComments(content);
            }
        }
    });

    $("#myLoginForm").validate({
        rules: {
            phone: {
                required:true,
                maxlength:16
            },
            password:{
                required:true,
                rangelength:[6, 20]
            }
        },
        messages: {
            phone: {
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",16)
            },
            password:{
                required:config.validErrors.required,
                rangelength:config.validErrors.rangLength.replace("${min}",6).replace("${max}",20)
            }
        },
        submitHandler:function(form){
            productDetail.loginFormSubmit();
        }
    });

    $("#popWindowClose").click(function(){
        $("#popWindow").addClass("hidden");
    });

});
