window.addEventListener("load", (event) => {
    $('button.btn-delete').click(function() {
        let parent = $(this).parent().parent().parent();
        let ts_id = parent.attr('class').split(' ').splice(-1)[0];

        $('button#deletion-confirm').click(function() {
            let form_data = {};
            form_data['ts_id'] = ts_id;
            form_data['csrfmiddlewaretoken'] = csrf_token;

            $.ajax({
                url: '',
                type: 'post',
                data: form_data,
                data_type: 'json',
                success: function(response) {
                    parent.remove();
                    $('#modal-close').click();
                },
                error: function(response) {
                    console.log(response);
                }
            });
        });
    });
});