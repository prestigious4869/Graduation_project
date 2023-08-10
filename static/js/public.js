$(function () {
    /* 点击 返回网页顶部 */
    $('a').attr('href','javascript:void(0)')
    $('#topButton').on('click', function () {
        goToTop()
    })

    /* 点击 退出登录 */
    $('#exitButton').on('click', function () {
        $.post({
            url: "http://127.0.0.1:5000/exit",
            contentType: "application/json",
            data: JSON.stringify(),
            success: function (response) {
                alert("退出成功")
                window.open("http://127.0.0.1:5000/", "_self")
            },
            error: (req) => {
                alert("Connection error")
            },
        })
    })

    // $.post({
    //     url: "http://127.0.0.1:5000/publicInfo",
    //     contentType: "application/json",
    //     data: JSON.stringify(),
    //     success: function (response) {
    //         get_data=JSON.parse(response)
    //         $('#userName').text(get_data[0].nickname)
    //         $('#userID').text(get_data[0].username)
    //     },
    //     error: (req) => {
    //         alert("Connection error")
    //     },
    // })
})
function goToTop() {
    var distance = $('html').scrollTop() + $('body').scrollTop();
    var height = $('html,body');
    var time = 70;
    var intervalTime = 1;
    var itemDistance = distance / (time / intervalTime);
    var intervalId = setInterval(function () {
        distance -= itemDistance;
        if (distance <= 0) {
            distance = 0;
            clearInterval(intervalId);
        }
        height.scrollTop(distance);
    }, intervalTime);
}