$(function () {
    $('#loginButton').on('click', function () {
        data = {
            username: $("[name='userAccount']").val(),
            password: $("[name='userPassword']").val()
        }
        $.post({
            url: "http://127.0.0.1:5000/login",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function (response) {
                //失败需要错误信息，成功需要新网页
                if (response == "error") {
                    alert("用户名或密码错误!")
                    $("[name='userAccount']").val("")
                    $("[name='userPassword']").val("")
                }
                else if (response == "no vein") {
                    var upload_main = document.getElementById('upload_main');
                    var bg = document.getElementById('bg');
                    upload_main.style.display = "block";
                    bg.style.display = "block";

                    var closeBtn = document.getElementById('closeBtn');
                    closeBtn.onclick = function () {
                        upload_main.style.display = "none";
                        bg.style.display = "none";
                    }
                }
                else if (response == "success") {
                    window.open("http://127.0.0.1:5000/getContract", "_self")
                }
            },
            error: (response) => {
                alert("Connection error")
            },
        })
    })
    $('#upload_button').on('click', function () {
        var formdata = new FormData()
        formdata.append("vein", $('#vein')[0].files[0])
        $.post({
            url: "http://127.0.0.1:5000/uploadVein",
            data: formdata,
            datatype: "text",
            cache: false,  
            processData: false,  
            contentType: false,
            success : function(response) {
                if (response == "success") {
                    alert("上传成功");
                    var upload_main = document.getElementById('upload_main');
                    var bg = document.getElementById('bg');
                    upload_main.style.display = "none";
                    bg.style.display = "none";
                }
            },
            error:function(){
                alert("上传失败");
            }
        })
    })
    $('#registerButton').on('click', function () {
        window.open("http://127.0.0.1:5000/getNewUser", "_self")
    })
})