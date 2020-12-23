function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault()

        // var signature = $("#signature").val();
        // var nick_name = $("#nick_name").val();
        // var gender = $(".gender").val()
        // var gender = $(".base_info").find('input:radio:checked').val();
        var username = $("#username").val();
        var age = $("#age").val();
        var school = $("#school").val();
        var sex = $(".base_info").find('input:radio:checked').val();

        if (!username) {
            alert('请输入昵称')
            return
        }
        if (!sex) {
            alert('请选择性别')
        }

        // TODO 修改用户信息接口
        var params = {
            "username": username,
            "age": age,
            "school": school,
            "sex": sex,
        }

        $.ajax({
            url: "/base_info",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    // 更新父窗口内容
                    $('.user_center_name', parent.document).html(params['username'])
                    $('#nick_name', parent.document).html(params['username'])
                    $('.input_sub').blur()
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })
})