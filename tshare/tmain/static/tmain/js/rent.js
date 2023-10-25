window.addEventListener("load", (event) => {
    $('.btn-rent').click(function() {
        var parent = $(this).parent().parent().parent()
        let id = parent.attr('class').split(' ').splice(-1)[0];
        form_data = {
            'csrfmiddlewaretoken': csrf_token,
            'ts_id': id
        };
        $.ajax({
           url: '',
           data: form_data,
           type: 'POST',
           success: function(response) {
                parent.remove();
           },
           error: function(response) {}
        });
    });
});