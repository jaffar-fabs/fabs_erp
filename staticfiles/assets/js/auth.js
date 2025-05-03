$(document).ready(function () {

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    $('#login-form-authenticate-form-id').submit(function (e) {
        e.preventDefault();
        var loginbtn = document.getElementById('login-btn');
        var formData = new FormData(this);
        console.log(formData);
        $.ajax({
            type: 'POST',
            url: '/login-authentication-check-secret-key-api',
            data: formData,
            processData: false,
            contentType: false,
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function (res) {
                loginbtn.removeAttribute('disabled', '');
                loginbtn.value = 'Sign In';
                if (res.status == 'success') {
                    if (res.login) {
                        location.href = '/agents-list';
                    }
                } else {
                    null;
                }
            },
            error: function (error) {
                loginbtn.removeAttribute('disabled', '');
                loginbtn.value = 'Login';
                location.href = '/admin';
            }
        });
    });
});