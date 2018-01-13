function load_tags(prefix) {
    var list = $("#suggestions");
    if(prefix) {
        list.empty();

        $.ajax({
            url: root_url + 'api/tags/' + prefix,
            dataType: 'json',
            success: function(data) {
                list.empty();
                for(i = 0; i < data["tags"].length; ++i) {
                    $("<li/>").text(data["tags"][i]["name"] + " (" + data["tags"][i]["num_marks"] + ")").appendTo(list);
                }
            }
        });

        offset = $("#id_tags").position();
        input_height = $("#id_tags").height();
        $("#suggestions").css({'top' : (offset.top + 47) + 'px',
                               'display': 'block'});
    } else {
        $("#suggestions").css({'display': 'none'});
    }
}

function load_mark(id) {
    $.ajax({
        url: root_url + 'api/mark/' + id,
        data: {
        'id': id
        },
        dataType: 'json',
        success: function(data) {
            console.log(data);
        }
    });
}

function edit_mark_form(id, form) {
    $.ajax({
        url: root_url + 'block/mark/' + id,
        dataType: 'html',
        success: function(data) {
            append_form(data, form);
        }
    });
}

function get_title(url) {
    $.ajax({
        type: "POST",
        url: root_url + 'api/title/',
        data: {
        'url': url
        },
        dataType: 'json',
        success: function(data) {
            console.log(data);
        }
    });
}

function edit_mark(id) {
    $.post({
        url: root_url + 'block/mark',
        data: $("#editform" + id).serialize(),
        success: function(data) {
            console.log(data);
        }
    });
}

function append_form(form, el) {
    el.parent().parent().append(form);
}

$(function() {
    var mark_id = 0;

    $(".edit_btn").click(function(e) {
        e.preventDefault();
        if($("#edit_mark_form")) {
            $("#edit_mark_form").remove();
        }

        mark_id = $(this).attr("mark_id");
        edit_mark_form(mark_id, $(this));
    });

    $(document).on("submit", "#edit_mark_form", (function(e) {
        e.preventDefault();
        //console.log($(this).serialize());
        $.post({
            url: root_url + 'block/mark/' + mark_id + '/',
            data: $(this).serialize(),
            success: function(data) {
                location.reload();
            }
        });
    }));

    $("#select_all").click(function(e) {
        e.preventDefault();
        $(':checkbox').each(function() {
            this.checked = true;
        });
    });

    $("#deselect_all").click(function(e) {
        e.preventDefault();
        $(':checkbox').each(function() {
            this.checked = false;
        });
    });

    $("#tags_selected_form").submit(function(e) {
        e.preventDefault();

        $.post({
            url: root_url + 'edit_selection/',
            data: $(this).serialize(),
            success: function(data) {
                location.reload();
            }
        });
    });

    $("#show_search").click(function() {
        $("#search_form").show();
        $("#id_query").focus();
    });

    $(document).on("change paste keyup", "#id_tags", function(e) {
        tags = $("#id_tags").val().split(",");
        last = tags[tags.length - 1].replace(/ /g,'');
        load_tags(last);

    });

    $(document).on("focusout", "#id_tags", function(e) {
        $("#suggestions").css({'display': 'none'});
    });
});
