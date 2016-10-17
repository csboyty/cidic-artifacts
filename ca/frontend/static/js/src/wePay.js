$(document).ready(function(){
    setInterval(function(){
        $.ajax({
            url:config.ajaxUrls.payResult.replace(":orderNo",orderNo),
            type:"get",
            dataType:"json",
            data:{
                uid:uid,
                pay_type:"WX"
            },
            success:function(data){
                if(data.trade_status){
                    if(data.trade_status=="TRADE_SUCCESS"||data.trade_status=="TRADE_FAILURE"){
                        location.href="orders/pay-result/"+orderNo+"?trade_status="+data.trade_status;
                    }
                }
            },
            error:function(data){

            }
        })
    },10000);

    function makeqrcode(url){
        var qr = qrcode(10, 'M');
        qr.addData(url);
        qr.make();
        var wording=document.createElement('p');
        wording.innerHTML = "扫我，扫我";
        var code=document.createElement('DIV');
        code.innerHTML = qr.createImgTag();
        var element=document.getElementById("qrcode");
        element.appendChild(wording);
        element.appendChild(code);
    }
    makeqrcode(code_url);
});