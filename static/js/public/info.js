$(function () {
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
    $.post({
        url: "http://127.0.0.1:5000/check_info",
        contentType: "application/json",
        data: JSON.stringify(),
        success: function (response) {
            var get_data = JSON.parse(response)
            $('#firstPartyName').text(get_data['first_name'])
            $('#firstPartyId').text(get_data['first_id'])
            $('#firstPartyTime').text(get_data['first_time'])
            $('#secondPartyName').text(get_data['second_name'])
            $('#secondPartyId').text(get_data['second_id'])
            $('#secondPartyTime').text(get_data['second_time'])
            $("#image").attr('src', "data:image/png;base64," + get_data['image'])
        },
        error: function () {
        }
    })
})