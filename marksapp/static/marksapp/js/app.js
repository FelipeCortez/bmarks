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

function populateWithParameters() {
  if($("#id_name").val() == "" && $("#id_url").val() == "") {
    $("#id_url").val(getUrlParameter("url"));
    $("#id_name").val(getUrlParameter("name"));
  }
}

function filterSuggestions(prefix) {
  var list = $("#suggestions");
  if(prefix) {
    list.empty();

    for(i = 0; i < all_tags.length; ++i) {
      if(all_tags[i]["name"].startsWith(prefix)) {
        numberElement = $("<span/>").text(all_tags[i]["num_marks"]);
        numberElement.addClass("number");

        tagName = $("<span/>").text(all_tags[i]["name"]);
        tagName.addClass("tag-name");
        listElement = $("<li/>").append(tagName);
        listElement.append(numberElement);
        list.append(listElement);
      }
    }

    offset = $("#id_tags").offset();
    input_height = $("#id_tags").outerHeight();
    console.log(input_height);
    $("#suggestions").css({'top' : (offset.top + input_height) + 'px',
      'left' : (offset.left) + 'px',
      'display': 'block'});
  } else {
    $("#suggestions").css({'display': 'none'});
  }
}

function loadMark(id) {
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

function editMarkForm(id, form) {
  $.ajax({
    url: root_url + 'block/mark/' + id,
    dataType: 'html',
    success: function(data) {
      appendForm(data, form);
      $("#id_name").focusTextToEnd();
    }
  });
}

function getTitle(url) {
  $.ajax({
    type: "POST",
    url: root_url + 'api/getTitle/',
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

function editMark(id) {
  $.post({
    url: root_url + 'block/mark',
    data: $("#editform" + id).serialize(),
    success: function(data) {
      console.log(data);
    }
  });
}

function deleteMark(id) {
  $.post({
    url: root_url + 'api/deleteMark/' + id + '/',
    success: function(data) {
      console.log(data);
      location.reload();
    }
  });
}

function appendForm(form, el) {
  el.parent().parent().append(form);
}

$(function() {
  populateWithParameters();
  get_all_tags();
  var mark_id = 0;
  $("#filter").hide();

  $(".edit_btn").click(function(e) {
    e.preventDefault();
    if($("#editMarkForm")) {
      $("#editMarkForm").remove();
    }

    mark_id = $(this).attr("mark_id");
    editMarkForm(mark_id, $(this));
    console.log("opa");
  });

  $(".delete_btn").click(function(e) {
    e.preventDefault();
    if(confirm('Are you sure?')) {
      mark_id = $(this).attr("mark_id");
      deleteMark(mark_id);
    }
  });

  $(document).on("submit", "#edit-mark-form", (function(e) {
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

  $("#show-search").click(function() {
    $("#search-form").show();
    $("#id_query").focus();
  });

  $(document).on("change", "#id_url", function(e) {
    if($("#id_name").val() == "") {
      getTitle($("#id_url").val());
    }
  });

  $(document).on("change paste keyup", "#id_tags", function(e) {
    tags = $("#id_tags").val().split(",");
    last = tags[tags.length - 1].replace(/ /g,'');
    filterSuggestions(last);
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

  /*
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
    */
});
