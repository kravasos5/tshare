window.addEventListener("load", (event) => {
    function balance_updater(new_balance) {
        $('#balance').text('Баланс: ' + new_balance);
    };

    $('.end-rent').click(function() {
        var parent = $(this).parent().parent().parent()
        let id = parent.attr('class').split(' ').splice(-1)[0];
        form_data = {
            'csrfmiddlewaretoken': csrf_token,
            'rent_id': id
        };
        $.ajax({
           url: '',
           data: form_data,
           type: 'POST',
           success: function(response) {
                parent.remove();
                balance_updater(response.new_balance);
           },
           error: function(response) {}
        });
    });
});