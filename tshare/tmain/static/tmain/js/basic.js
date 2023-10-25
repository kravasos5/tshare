window.addEventListener("load", (event) => {
    $('button.close').click(function() {
        $(this).parent().remove();
    });
});