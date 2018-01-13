(function($){
    $.fn.focusTextToEnd = function(){
        this.focus();
        var $thisVal = this.val();
        this.val('').val($thisVal);
        return this;
    }
}(jQuery));

var all_tags = "hey";

function get_all_tags() {
    $.ajax({
        url: root_url + 'api/tags/',
        dataType: 'json',
        success: function(data) {
            all_tags = data["tags"];
        }
    });
}

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for(i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if(sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

function populate_with_parameters() {
    if($("#id_name").val() == "" && $("#id_url").val() == "") {
        $("#id_url").val(getUrlParameter("url"));
        $("#id_name").val(getUrlParameter("name"));
    }
}

function filter_suggestions(prefix) {
    var list = $("#suggestions");
    if(prefix) {
        list.empty();

        for(i = 0; i < all_tags.length; ++i) {
            if(all_tags[i]["name"].startsWith(prefix)) {
                $("<li/>").text(all_tags[i]["name"] + " (" + all_tags[i]["num_marks"] + ")").appendTo(list);
            }
        }

        offset = $("#id_tags").position();
        input_height = $("#id_tags").height();
        $("#suggestions").css({'top' : (offset.top + 43) + 'px',
                               'left' : (offset.left) + 'px',
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
            $("#id_name").focusTextToEnd();
        }
    });
}

function get_title(url) {
    $.ajax({
        type: "POST",
        url: root_url + 'api/get_title/',
        data: {
        'url': url
        },
        dataType: 'json',
        success: function(data) {
            if(!("error" in data)) {
                if($("#id_name").val() == "") {
                    $("#id_name").val(he.decode(data["url"]));
                }
            } else {
                //
            }
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

function delete_mark(id) {
    $.post({
        url: root_url + 'api/delete_mark/' + id + '/',
        success: function(data) {
            console.log(data);
            location.reload();
        }
    });
}

function append_form(form, el) {
    el.parent().parent().append(form);
}

$(function() {
    populate_with_parameters();
    get_all_tags();
    var mark_id = 0;
    $("#filter").hide();

    $(".edit_btn").click(function(e) {
        e.preventDefault();
        if($("#edit_mark_form")) {
            $("#edit_mark_form").remove();
        }

        mark_id = $(this).attr("mark_id");
        edit_mark_form(mark_id, $(this));
        console.log("opa");
    });

    $(".delete_btn").click(function(e) {
        e.preventDefault();
        if(confirm('Are you sure?')) {
            mark_id = $(this).attr("mark_id");
            delete_mark(mark_id);
        }
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

    $(document).on("change", "#id_url", function(e) {
        if($("#id_name").val() == "") {
            get_title($("#id_url").val());
        }
    });

    $(document).on("change paste keyup", "#id_tags", function(e) {
        tags = $("#id_tags").val().split(",");
        last = tags[tags.length - 1].replace(/ /g,'');
        filter_suggestions(last);
    });

    $(document).on("focusout", "#id_tags", function(e) {
        $("#suggestions").css({'display': 'none'});
    });

    $(document).on("change paste keyup", "#filter", function(e) {
        var filter = $("#filter").val();
        $(".tag_name").each(function(index) {
            if($(this).text().indexOf(filter) != -1) {
                $(this).parent().show();
            } else {
                $(this).parent().hide();
            }
        });
    });

    $(document).keyup(function(event){
        var filter = $("#filter").val();

        if(event.key == '/') {
            $("#filter").show();
            $("#filter").focus();
        } else if(event.keyCode === 27) {
            // ESC
            $("#filter").val("").trigger("change");
            $("#filter").hide();
        } else if(event.keyCode === 13) {
            if(filter != '') {
                $(".tag_name:visible:first").focus();
            }
        }
    });
});
