$(function () {
    $('button').on('click', function () {
        var id = $("[name='id']").val()
        var username = $("[name='username']").val()
        var password1 = $("[name='userPassword1']").val()
        var password2 = $("[name='userPassword2']").val()
        /*两次输入的密码不同*/
        if (password1 != password2 || password1 == "") {
            alert("illegal password!")
            $("[name='userPassword1']").val("")
            $("[name='userPassword2']").val("")
        }
        else {
            data = {
                id: id,
                username: username,
                password: password1,
            }
            $.post({
                url: "http://127.0.0.1:5000/register",
                contentType: "application/json",
                data: JSON.stringify(data),
                success: function (response) {
                    //需要信息判断成功或失败
                    if(response == "success"){
                        alert("注册成功!")
                        $("[name='id']").val("")
                        $("[name='username']").val("")
                        $("[name='userPassword1']").val("")
                        $("[name='userPassword2']").val("")
                    }
                    else{
                        alert("注册失败!该用户名已被占用")
                        $("[name='id']").val("")
                        $("[name='username']").val("")
                        $("[name='userPassword1']").val("")
                        $("[name='userPassword2']").val("")
                    }
                },
                error: (response) => {
                    alert("Connection error")
                },
            })
        }
    })
})