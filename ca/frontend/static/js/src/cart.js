var cart=(function(config,functions){
    var total=0;
    return {
        getAllItems:function(){
            var dataItems=[];
            $(".item").each(function(index,el){
                dataItems.push([$(this).data("item-id"),$(this).find(".quantity").text()]);
            });
            return dataItems;
        },
        delete:function(el){
            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.cartAddItem,
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(me.getAllItems()),
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        el.parents("tr").remove();
                        this.computeAll();
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }

                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        quantityChangeHandler:function(el){
            var quantityContainerEl=el.parent(".quantityContainer");
            var itemEl=el.parents(".item");
            var checked=itemEl.find(".checkItem").prop("checked");
            var price=Number(itemEl.find(".price").text());
            var subTotalEl=itemEl.find(".subTotal");
            var subTotal=Number(subTotalEl.text());
            var decrementEl=quantityContainerEl.find(".quantityCtrl:eq(0)");
            var count=Number(el.val());
            var increment,newSubTotal;

            if(count!=1){
                decrementEl.removeClass("disabled");
            }else{
                decrementEl.addClass("disabled");
            }
            newSubTotal=(price*count).toFixed(2);
            subTotalEl.text(newSubTotal);
            increment=newSubTotal-subTotal;
            this.updateAmount(increment);

            if(checked){
                this.updateAmount(increment);
            }
        },
        updateAmount:function(increment){
            var old=Number($("#amount").text());
            $("#amount").text((old+increment).toFixed(2));
        },
        quantityCtrlHandler:function(el){
            var type=el.data("type");
            var quantityContainerEl=el.parent(".quantityContainer");
            var itemEl=el.parents(".item");
            var checked=itemEl.find(".checkItem").prop("checked");
            var price=Number(itemEl.find(".price").text());
            var subTotalEl=itemEl.find(".subTotal");
            var countEl=quantityContainerEl.find(".quantity");
            var decrementEl=quantityContainerEl.find(".quantityCtrl:eq(0)");
            var incrementEl=quantityContainerEl.find(".quantityCtrl:eq(1)");
            var count=Number(countEl.val());
            var increment=0;
            var quantityTotal=parseInt(itemEl.find(".quantityTotal").text());

            if(type=="increment"){
                count++;
                if(count==quantityTotal){
                    incrementEl.addClass("disabled");
                }
                increment=price;
            }else{
                incrementEl.removeClass("disabled");
                count--;
                increment=-price;
            }

            countEl.val(count);

            if(count!=1){
                decrementEl.removeClass("disabled");
            }else{
                decrementEl.addClass("disabled");
            }

            subTotalEl.text((price*count).toFixed(2));
            if(checked){
                this.updateAmount(increment);
            }


        },
        updateCount:function(){
            $("#count").text($(".checkItem:checked").length);
        },
        checkAllHandler:function(el){
            if(el.prop("checked")){
                $(".checkItem,.checkAll").prop("checked",true);
                this.computeAll();
            }else{
                $(".checkItem,.checkAll").prop("checked",false);
                $("#amount").text("0.00");
            }

            this.updateCount();
        },
        checkItemHandler:function(el){
            var increment=0;
            var subTotal=Number(el.parents("tr").find(".subTotal").text());
            if(el.prop("checked")){
                increment=subTotal;
                if($(".checkItem:checked").length==$(".checkItem").length){
                    $(".checkAll").prop("checked",true);
                }
            }else{
                increment=-subTotal;
                $(".checkAll").prop("checked",false);
            }

            this.updateAmount(increment);

            this.updateCount();
        },
        computeAll:function(){
            var total= 0,subTotal;
            $(".item").each(function(index,el){
                subTotal=Number($(el).find(".subTotal").text());
                total+=subTotal;
            });

            $("#amount").text(total.toFixed(2));
        },
        unCheckAllHandler:function(){
            $(".checkItem").prop("checked",false);
            $("#amount").text("0.00");
        },
        submitForm:function(form){
            functions.showLoading();
            var items=[],trEl,error=false;
            $(".checkItem:checked").each(function(index,el){
                trEl=$(this).parents(".item");

                if(Number(trEl.find(".quantity").val()<=Number(trEl.find(".quantityTotal").text()))){
                    items.push([trEl.data("item-id"),Number(trEl.find(".quantity").val())]);
                }else{
                    error=true;
                    return false;
                }

            });
            $("#items").val(JSON.stringify(items));

            if(error){
                functions.hideLoading();
                $().toastmessage("showErrorToast",config.messages.quantityError);
                return false;
            }else{
                form[0].submit();
            }
        }
    }
})(config,functions);

$(document).ready(function(){
    $(".quantityCtrl").click(function(){
        if(!$(this).hasClass("disabled")){
            cart.quantityCtrlHandler($(this));
        }

    });
    $(".quantity").keyup(function(){
        if(parseInt($(this).val())>=1){
            cart.quantityChangeHandler($(this));
        }
    });

    $(".checkItem").click(function(){
        cart.checkItemHandler($(this));
    });

    $("#unCheckAll").click(function(){
        cart.unCheckAllHandler();
    });
    $(".checkAll").click(function(){
        cart.checkAllHandler($(this));
    });

    $("#cart").on("click",".delete",function(){
        if(confirm(config.messages.confirmDelete)){
            cart.delete($(this));
        }
        return false;
    });
    $("#submit").click(function(){
        if($(".checkItem:checked").length==0){
            $().toastmessage("showErrorToast",config.messages.noSelected);
        }else{
            cart.submitForm($("#myForm"));
        }

        return false;
    });
});
