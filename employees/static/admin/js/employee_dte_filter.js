(function($) {
    $(function() {
        $('#id_department').change(function() {
            var departmentId = $(this).val();
            var dteSelect = $('#id_dte');

            if (departmentId) {
                $.ajax({
                    url: '/api/departments/' + departmentId + '/dtes/',
                    data: {
                        format: 'json'
                    },
                    dataType: 'json',
                    success: function(data) {
                        dteSelect.empty();
                        dteSelect.append($('<option></option>').attr('value', '').text('---------'));
                        $.each(data, function(key, value) {
                            dteSelect.append($('<option></option>').attr('value', value.id).text(value.name));
                        });
                    }
                });
            } else {
                dteSelect.empty();
                dteSelect.append($('<option></option>').attr('value', '').text('---------'));
            }
        });

        // Trigger change on load if a department is already selected (for edit view)
        if ($('#id_department').val()) {
            $('#id_department').trigger('change');
        }
    });
})(django.jQuery);