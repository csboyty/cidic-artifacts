var postUpdate=(function(config,functions){
    /**
     * 显示步骤对应的面板
     * @param {Number} stepId 需要显示的面板的id
     */
    function showStepPanel(stepId){
        $(".zyupStepPanel").addClass("zyupHidden");
        $(stepId).removeClass("zyupHidden");
        $(".zyupStepCurrent").removeClass("zyupStepCurrent");
        $(".zyupStep[href='"+stepId+"']").addClass("zyupStepCurrent");
    }
    return {
        uploadedMedia:{},
        uploadHandler:null,
        preview:function(){
            var tpl=$("#previewTpl").html(),
                files=[],html="";
            for(var obj in this.uploadedMedia){
                files.push(this.uploadedMedia[obj])
            }
            html=juicer(tpl,{
                title:$("#zyupTitleInput").val(),
                author:$("#zyupAuthorInput").val(),
                size:$("#zyupSizeInput").val(),
                explain:$("#zyupDescriptionTxt").val(),
                attachment_file:$("#zyupFileUrl").val(),
                analysis:$("#zyupAnalysisTxt").val(),
                preview:files[0]["media_file"],
                assets:files
            });
            $("#zyupPreview").html(html);
        },
        createThumbUploader:function(){
            functions.createQiNiuUploader({
                maxSize:config.uploader.sizes.all,
                filter:config.uploader.filters.img,
                uploadBtn:"zyupThumbUploadBtn",
                multipartParams:null,
                multiSelection:false,
                uploadContainer:"zyupThumbContainer",
                fileAddedCb:null,
                beforeUploadCb:null,
                progressCb:null,
                uploadedCb:function(info,file,up){
                    var path = info.url; //获取上传成功后的文件的Url

                    //判断是否是1：1
                    $.get(path+"?imageInfo",function(data){
                        //console.log(data);
                        if(data.width==510&&data.height==330){
                            $("#zyupThumb").attr("src",path);
                            $("#zyupThumbUrl").val(path);
                        }else{
                            $().toastmessage("showErrorToast",config.messages.imageSizeError);
                        }

                    });
                }
            });
        },
        createBgUploader:function(){
            functions.createQiNiuUploader({
                maxSize:config.uploader.sizes.all,
                filter:config.uploader.filters.img,
                uploadBtn:"zyupBgUploadBtn",
                multipartParams:null,
                multiSelection:false,
                uploadContainer:"zyupBgContainer",
                fileAddedCb:null,
                beforeUploadCb:null,
                progressCb:null,
                uploadedCb:function(info,file,up){
                    var path = info.url; //获取上传成功后的文件的Url

                    //判断是否是1：1
                    $.get(path+"?imageInfo",function(data){
                        //console.log(data);
                        if(data.width==1920&&data.height==600){
                            $("#zyupBg").attr("src",path);
                            $("#zyupBgUrl").val(path);
                        }else{
                            $().toastmessage("showErrorToast",config.messages.imageSizeError);
                        }

                    });
                }
            });
        },
        createFileUploader:function(){
            functions.createQiNiuUploader({
                maxSize:config.uploader.sizes.all,
                filter:config.uploader.filters.zip,
                uploadBtn:"zyupFileUploadBtn",
                multipartParams:null,
                multiSelection:false,
                uploadContainer:"zyupFileContainer",
                fileAddedCb:null,
                beforeUploadCb:null,
                progressCb:function(file){
                    $("#zyupFilename").text(file.name+"----"+file.percent+"%");
                },
                uploadedCb:function(info,file,up){
                    var path = info.url; //获取上传成功后的文件的Url

                    $("#zyupFilename").text(file.name);
                    $("#zyupFilenameValue").val(file.name);
                    $("#zyupFileUrl").val(path);

                }
            });
        },
        createUploader:function(){
            var me=this;
            me.uploadHandler=functions.createQiNiuUploader({
                maxSize:config.uploader.sizes.all,
                filter:config.uploader.filters.img,
                uploadBtn:"zyupUploadBtn",
                multipartParams:null,
                multiSelection:false,
                uploadContainer:"zyupStep2",
                filesAddedCb:function(files,up){
                    var tpl=$("#mediaItemTpl").html();

                    var html=juicer(tpl,{
                        fileId:files[0]["id"],
                        filename:files[0]["name"]
                    });

                    $("#zyupMediaList").append(html);
                },
                beforeUploadCb:null,
                progressCb:function(file){
                    $(".zyupUnCompleteLi[data-file-id='"+file.id+"']").find(".zyupPercent").text(file.percent+"%");
                },
                uploadedCb:function(info,file,up){
                    var path = info.url; //获取上传成功后的文件的Url

                    //判断是否是1：1
                    $.get(path+"?imageInfo",function(data){
                        //console.log(data);
                        if(data.width==600&&data.height==400){
                            $(".zyupUnCompleteLi[data-file-id='"+file.id+"']").find(".zyupPercent").
                                html("<img style='height:40px' src='"+path+"'>").
                                end().addClass("zyupMediaItem").removeClass("zyupUnCompleteLi");
                            $(".zyupDelete.zyupHidden").removeClass("zyupHidden");
                            me.uploadedMedia[file["id"]]={
                                media_filename:file.name,
                                media_file:path
                            }
                        }else{
                            $().toastmessage("showErrorToast",config.messages.imageSizeError.replace("${filename}",file.name));
                            $(".zyupUnCompleteLi[data-file-id='"+file.id+"']").remove();
                        }
                    });

                }
            });
        },
        deleteFile:function(el){
            var parentLi=$(el).parent("li"),
                fileId=parentLi.data("file-id");
            parentLi.remove();
            this.uploadedMedia[fileId]=undefined;
            delete this.uploadedMedia[fileId];
        },
        stepHandler:function(stepId){
            if(stepId!="#zyupStep1"){
                if($("#zyupTitleInput").val()==""||$("#zyupThumbUrl").val()==""||
                    $("#zyupBgUrl").val()==""){
                    $().toastmessage("showErrorToast",config.messages.stepOneUnComplete);
                    return false;
                }
            }

            if(stepId=="#zyupStep3"){

                //判断第二中的内容是否都已经填写完整。
                if($(".zyupMediaItem").length==0||$(".zyupUnCompleteLi").length!=0){
                    $().toastmessage("showErrorToast",config.messages.stepTwoUnComplete);
                    return false;
                }


                //显示
                //this.preview();
            }

            showStepPanel(stepId);

        },
        formSubmit:function(form){
            functions.showLoading();
            var files=[];
            for(var obj in this.uploadedMedia){
                files.push(this.uploadedMedia[obj]);
            }
            var formObj=$(form).serializeObject();
            formObj.profiles=files;
            formObj.parameters=tinyMCE.editors[0].getContent();
            formObj.content=tinyMCE.editors[1].getContent();
            $.ajax({
                url:$(form).attr("action"),
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                type:"post",
                success:function(response){
                    if(response.success){
                        //functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccRedirect);
                        setTimeout(function(){
                            window.location.href=document.getElementsByTagName('base')[0].href+"manager/products/";
                        },3000);
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        getPost:function(id){
            var me=this;
            $.ajax({
                url:config.ajaxUrls.productDetail.replace(":id",id),
                dataType:"json",
                type:"get",
                success:function(response){
                    if(response.success){
                        var length=response.product.detail.profiles.length;
                        for(var i=0;i<length;i++){
                            me.uploadedMedia[i+1]=response.product.detail.profiles[i];
                        }
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

    if(postId){
        postUpdate.getPost(postId);
    }

    tinymce.init({
        selector: "#zyupParamTxt",
        height:300,
        toolbar1: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
        toolbar2: 'print preview media | forecolor backcolor emoticons',
        //image_advtab: true,
        plugins : 'link image preview fullscreen table textcolor colorpicker code'

    });
    tinymce.init({
        selector: "#zyupContentTxt",
        height:300,
        toolbar1: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
        toolbar2: 'print preview media | forecolor backcolor emoticons',
        //image_advtab: true,
        plugins : 'link image preview fullscreen table textcolor colorpicker code'

    });

    //步骤控制
    $("#zyupTab a").click(function(){
        postUpdate.stepHandler($(this).attr("href"));

        return false;
    });

    $("#zyupMediaList").on("click",".zyupDelete",function(){
        postUpdate.deleteFile($(this));
    });

    postUpdate.createUploader();
    //postUpdate.createFileUploader();
    postUpdate.createThumbUploader();
    postUpdate.createBgUploader();

    $("#zyupForm").submit(function(){
        postUpdate.formSubmit($(this));
        return false;
    }).on("keydown",function(event){
            if(event.keyCode==13){
                return false;
            }
        })
});