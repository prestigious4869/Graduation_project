$(function () {
    // $('#searchButton').on('click', function(){
    //     $.post({
    //         url: "http://127.0.0.1:5000/orderForBusiness",
    //         contentType: "application/json",
    //         data: JSON.stringify(),
    //         /* 取到这个商家的全部订单 + 用户nickname */
    //         success: function (response) {
    //             minNo = 0
    //             maxNo = 4
    //             var get_data = JSON.parse(response)
    //             data = []
    //             totalNo = 0
    //             keyword = $("#searchInfo").val()
    //             get_data.forEach(element => {
    //                 if(keyword == "" || element.name.includes(keyword) || element.nickname.includes(keyword) || element.commit_time.includes(keyword))
    //                     totalNo = data.push(element)
    //             });
    //             showPage()
    //         },
    //         error: (req) => {
    //             alert("Connection error")
    //         },
    //     })
    // })
    /* 点击 下一页 */
    // $('#nextButton').on('click', function () {
    //     goToTop()
    //     if (maxNo < totalNo-1) {
    //         minNo = minNo + 5
    //         maxNo = maxNo + 5
    //         showPage()
    //     }
    // })
    /* 点击 上一页 */
    // $('#lastButton').on('click', function () {
    //     goToTop()
    //     if (minNo != 0) {
    //         minNo = minNo - 5
    //         maxNo = maxNo - 5
    //         showPage()
    //     }
    // })

    /* 获取用户信息 */
    $.post({
        url: "http://127.0.0.1:5000/personalInfo",
        contentType: "application/json",
        data: JSON.stringify(),
        success: function (response) {
            get_data = JSON.parse(response)
            $('#userName').text(get_data[0].name)
            $('#userID').text(get_data[0].userID)
        },
        error: (req) => {
            alert("Connection error")
        },
    })
    /* 获取用户的已有合同信息，待签署、待对方签署、已签署 */
    $.post({
        url: "http://127.0.0.1:5000/getExistSignatory",
        contentType: "application/json",
        data: JSON.stringify(),
        success: function (response) {
            get_data = JSON.parse(response)
            user_id = get_data["user_id"]
            get_data["waitme"].forEach(element=>{
                $("#itemList").append('<li id="item_1">\
                <div class="clearfix" style="width: 220px;">\
                    <p>合同:\
                        <span id="waitMeContractName">'+element.contract_name+'</span>\
                    </p>\
                    <div class="waitMePreview" style="margin-top: 5px; color: cadetblues; text-align: center;">预览</div>\
                </div>\
                <div class="clearfix" style="width: 220px;">\
                    <p>签署对象：\
                        <span id="waitMeTargetName">'+element.first_name+'</span>\
                    </p>\
                    <p style="padding-top: 10px;">签署对象id：\
                        <span id="waitMeTargetId">'+element.first_party_id+'</span>\
                    </p>\
                </div>\
                <div>\
                    <label for="contract">上传指纹</label>\
                    <input type="file" multiple="multiple" accept="image/jpeg" id="veinImage" name="image">\
                </div>\
                <div style="width: 100px;">\
                    <p>状态：\
                        <span id="contractState">待签署</span>\
                    </p>\
                </div>\
                <div style="width: 50px;">\
                    <form action="" class="buttonBlock clearfix">\
                        <button class="signButton" type="button">√</button>\
                        <!-- <button class="deleteButton" type="button">×</button> -->\
                    </form>\
                </div>\
            </li>')
            });
            get_data["waitother"].forEach(element=>{
                $("#itemList").append('<li id="item_1">\
                <div class="clearfix" style="width: 290px;">\
                    <p>合同:\
                        <span id="waitOtherContractName">'+element.contract_name+'</span>\
                    </p>\
                    <div class="waitOtherPreview" style="margin-top: 5px; color: cadetblues; text-align: center;">预览</div>\
                </div>\
                <div class="clearfix" style="width: 290px;">\
                    <p>签署对象：\
                        <span id="waitOtherTargetName">'+element.second_name+'</span>\
                    </p>\
                    <p style="padding-top: 10px;">签署对象id：\
                        <span id="waitOtherTargetId">'+element.second_party_id+'</span>\
                    </p>\
                </div>\
                <div style="width: 140px;">\
                    <p>状态：\
                        <span id="contractState">待对方签署</span>\
                    </p>\
                </div>\
            </li>')
            });
            var my_id = get_data["user_id"]
            get_data["finish"].forEach(element=>{
                var other_id = ""
                var other_name = ""
                if(element.first_party_id == my_id){
                    other_id = element.second_party_id
                    other_name = element.second_name
                }
                else{
                    other_id = element.first_party_id
                    other_name = element.first_name
                }
                $("#itemList").append('<li id="item_1">\
                <div class="clearfix" style="width: 290px;">\
                    <p>合同:\
                        <span id="finishContractName">'+element.contract_name+'</span>\
                    </p>\
                    <div class="finishPreview" style="display: inline-block; width: 100px; margin-top: 10px; color: cadetblues; text-align: center;">预览</div>\
                    <div class="scan" style="display: inline-block; width: 100px; margin-top: 10px; color: cadetblues; text-align: center;">扫描二维码</div>\
                </div>\
                <div class="clearfix" style="width: 290px;">\
                    <p>签署对象：\
                        <span id="finishTargetName">'+other_name+'</span>\
                    </p>\
                    <p style="padding-top: 10px;">签署对象id：\
                        <span id="finishTargetId">'+other_id+'</span>\
                    </p>\
                </div>\
                <div style="width: 140px;">\
                    <p>状态：\
                        <span id="contractState">已签署</span>\
                    </p>\
                </div>\
            </li>')
            });
        },
        error: (req) => {
            alert("Connection error")
        },
    })

    $('#upload').on('click', function () {
        var formdata = new FormData()
        formdata.append("contract", $('#image')[0].files[0])
        $.post({
            url: "http://127.0.0.1:5000/uploadContract",
            data: formdata,
            datatype: "text",
            cache: false,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response == "success") {
                    alert("上传成功");
                }
                else if (response == 'error') {
                    alert("上传失败，已上传过同名文件")
                }
                else{
                    alert("发生错误")
                }
                $('#image').val("")
            },
            error: function () {
                alert("上传失败");
            }
        })
    })

    $('#addButton').on('click', function () {
        $("#itemList").append('<li id="item_1">\
        <div class="clearfix" style="text-align: center;">\
            <input list="contract" placeholder="选择合同" class="contractInput">\
            <datalist name="itemType" id="contract" class="contractList">\
            </datalist>\
        </div>\
        <div class="clearfix" style="text-align: center;">\
            <input list="targetName" placeholder="选择对象姓名" class="targetNameInput">\
            <datalist name="itemType" id="targetName" class="targetNameList">\
            </datalist>\
            <input list="targetId" placeholder="选择对象ID" class="targetIdInput" style="margin: 5px;">\
            <datalist name="itemType" id="targetId" class="targetIdList">\
            </datalist>\
        </div>\
        <div>\
            <label for="contract">上传指纹</label>\
            <input type="file" multiple="multiple" accept="image/jpeg" id="veinImage" name="image">\
        </div>\
        <div style="width: 140px;">\
            <p>状态：\
                <span id="contractState"></span>\
            </p>\
        </div>\
        <div style="width: 100px;">\
            <form action="" class="buttonBlock clearfix">\
                <button class="changeButton" type="button">√</button>\
                <button class="deleteButton" type="button">×</button>\
            </form>\
        </div>\
    </li>')
        $.post({
            url: "http://127.0.0.1:5000/getSymbolInfo",
            contentType: "application/json",
            data: JSON.stringify(),
            success: function (response) {
                var get_data = JSON.parse(response)
                get_data["contractInfo"].forEach(element => {
                    $('#itemList li:last').find('.contractList').append('<option value="' + element.name + '">')
                })
                get_data["userInfo"].forEach(element => {
                    $('#itemList li:last').find('.targetNameList').append('<option value="' + element.name + '">')
                    $('#itemList li:last').find('.targetIdList').append('<option value="' + element.user_id + '">')
                })
            },
            error: (req) => {
                alert("Connection error")
            },
        })
    })

    /* 可根据id筛选姓名或根据姓名筛选id */
    $("body").on("propertychange input", ".targetNameInput", function () {
        
    })

    $("body").on("propertychange input", ".targetIdInput", function () {
        
    })

    $('body').on('click', '.deleteButton', function () {
        $(this).closest('#item_1').remove()
    })

    $('body').on('click', '#topButton', function(){
        goToTop()
    })

    /* 预览图片 */
    $('body').on('click', '.finishPreview', function () {
        var mode = "已签署"
        var contract_name = $(this).closest('#item_1').find("#finishContractName").text()
        var target_name = $(this).closest('#item_1').find("#finishTargetName").text()
        var target_id = $(this).closest('#item_1').find("#finishTargetId").text()
        data = {
            mode: mode,
            contract_name: contract_name,
            target_name: target_name,
            target_id: target_id
        }
        $.post({
            url: "http://127.0.0.1:5000/preview",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function (response) {
                if(response == "success")
                    window.open("http://127.0.0.1:5000/preview", "_self")
            },
            error: function () {
                alert("预览失败");
            }
        })
    })

    $('body').on('click', '.waitMePreview', function () {
        var mode = "待签署"
        var contract_name = $(this).closest('#item_1').find("#waitMeContractName").text()
        var target_name = $(this).closest('#item_1').find("#waitMeTargetName").text()
        var target_id = $(this).closest('#item_1').find("#waitMeTargetId").text()
        data = {
            mode: mode,
            contract_name: contract_name,
            target_name: target_name,
            target_id: target_id
        }
        $.post({
            url: "http://127.0.0.1:5000/preview",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function (response) {
                if(response == "success")
                    window.open("http://127.0.0.1:5000/preview", "_self")
            },
            error: function () {
                alert("预览失败");
            }
        })
    })

    $('body').on('click', '.waitOtherPreview', function () {
        var mode = "待对方签署"
        var contract_name = $(this).closest('#item_1').find("#waitOtherContractName").text()
        var target_name = $(this).closest('#item_1').find("#waitOtherTargetName").text()
        var target_id = $(this).closest('#item_1').find("#waitOtherTargetId").text()
        data = {
            mode: mode,
            contract_name: contract_name,
            target_name: target_name,
            target_id: target_id
        }
        $.post({
            url: "http://127.0.0.1:5000/preview",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function (response) {
                if(response == "success")
                    window.open("http://127.0.0.1:5000/preview", "_self")
            },
            error: function () {
                alert("预览失败");
            }
        })
    })

    /* 扫描二维码 */
    $('body').on('click', '.scan', function () {
        var contract_name = $(this).closest('#item_1').find("#finishContractName").text()
        var target_name = $(this).closest('#item_1').find("#finishTargetName").text()
        var target_id = $(this).closest('#item_1').find("#finishTargetId").text()
        data = {
            contract_name: contract_name,
            target_name: target_name,
            target_id: target_id
        }
        $.post({
            url: "http://127.0.0.1:5000/scan",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function (response) {
                if(response == "success")
                    window.open("http://127.0.0.1:5000/scan", "_self")
                else{
                    alert("出现错误")
                }
            },
            error: function () {
                alert("您无权查看此信息");
            }
        })
    })

    /* 提交合同申请 */
    $('body').on('click', '.changeButton', function () {
        var formdata = new FormData()
        formdata.append("contract_name", $(this).closest('#item_1').find(".contractInput").val())
        formdata.append("target_name", $(this).closest('#item_1').find(".targetNameInput").val())
        formdata.append("target_id", $(this).closest('#item_1').find(".targetIdInput").val())
        formdata.append("vein_image", $(this).closest('#item_1').find("#veinImage")[0].files[0])
        $.post({
            url: "http://127.0.0.1:5000/uploadSignRequest",
            data: formdata,
            cache: false,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response == "success") {
                    alert("上传成功");
                    window.location.reload();
                }
                else if(response == "matching error"){
                    alert("指静脉匹配失败")
                }
                else{
                    alert("发生错误")
                }
            },
            error: function () {
                alert("上传失败");
            }
        })
    })
    
    /* 签署待签署的合同 */
    $('body').on('click', '.signButton', function(){
        var formdata = new FormData()
        formdata.append("contract_name", $(this).closest('#item_1').find("#waitMeContractName").text())
        formdata.append("target_name", $(this).closest('#item_1').find("#waitMeTargetName").text())
        formdata.append("target_id", $(this).closest('#item_1').find("#waitMeTargetId").text())
        formdata.append("vein_image", $(this).closest('#item_1').find("#veinImage")[0].files[0])
        $.post({
            url: "http://127.0.0.1:5000/SignContract",
            data: formdata,
            cache: false,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response == "success") {
                    alert("签署成功");
                    window.location.reload();
                }
                else if(response == "matching error"){
                    alert("指静脉匹配失败")
                }
                else{
                    alert("发生错误")
                }
            },
            error: function () {
                alert("上传失败");
            }
        })
    })
})