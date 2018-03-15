$.fn.focusTextToEnd = function(){
  this.focus();
  let $thisVal = this.val();
  this.val('').val($thisVal);
  return this;
};

const root_url = "/";
let params = new URLSearchParams(location.search);
let all_tags = "";
let selectedIdx = -1;
let lastPrefix = "";

function splitTags(string) {
  return string.trim().split(/[\s,]+/);
}

function changeParams(func) {
  func();
  window.history.replaceState({}, '', `${location.pathname}?${params}`);
}

function getAllTags() {
  $.ajax({
    url: root_url + 'api/tags/',
    dataType: 'json',
    success: function(data) {
      all_tags = data["tags"];
    }
  });
}

let getURLParameter = function getURLParameter(sParam) {
  let sPageURL = decodeURIComponent(window.location.search.substring(1)),
                                    sURLletiables = sPageURL.split('&'),
                                    sParameterName,
                                    i;

  for (i = 0; i < sURLletiables.length; i++) {
    sParameterName = sURLletiables[i].split('=');

    if (sParameterName[0] === sParam) {
      return sParameterName[1] === undefined ? true : sParameterName[1];
    }
  }
};

function populateWithParameters() {
  if ($("#id_name").val() == "" && $("#id_url").val() == "") {
    $("#id_url").val(getURLParameter("url"));
    $("#id_name").val(getURLParameter("name"));
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
    url: root_url + 'api/get_title/',
    data: {'url': url},
    dataType: 'json',
    success: function(data) {
      if (!("error" in data)) {
        if ($("#id_name").val() == "") {
          console.log(he.decode(data["url"]));
          $("#id_name").val(he.decode(data["url"]));
        }
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
    url: root_url + 'api/delete_mark/' + id + '/',
    success: function(data) {
      console.log(data);
      location.reload();
    }
  });
}

function bumpMark(id) {
  $.post({
    url: root_url + 'api/bump_mark/' + id + '/',
    success: function(data) {
      console.log(data);
      location.reload();
    }
  });
}

function appendForm(form, el) {
  el.parent().parent().append(form);
}

function filterSuggestions(prefix) {
  let list = $("#suggestions");
  if (prefix) {
    list.empty();

    for (i = 0; i < all_tags.length; ++i) {
      if (all_tags[i]["name"].startsWith(prefix) && all_tags[i]["name"] != prefix) {
        numberElement = $("<span/>").text(all_tags[i]["num_marks"]);
        numberElement.addClass("number");

        tagName = $("<a/>").text(all_tags[i]["name"]);
        tagName.addClass("tag-name");

        let listElement = $("<li/>").append(tagName);
        listElement.append(numberElement);

        list.append(listElement);
      }
    }

    if (list.children().length > 0) {
      offset = $("#id_tags").offset();
      input_height = $("#id_tags").outerHeight();
      $("#suggestions").css({'top' : (offset.top + input_height) + 'px',
                             'left' : (offset.left) + 'px',
                             'display': 'block'});
    } else {
      $("#suggestions").css({'display': 'none'});
    }
  } else {
    $("#suggestions").css({'display': 'none'});
  }
}

function completeWithSuggestedTag(selectedTag) {
  let tags = splitTags($("#id_tags").val());
  let last = tags[tags.length - 1].replace(/ /g,'');
  if (last[0] == "-") { last = last.substr(1); }

  $("#id_tags").val($("#id_tags").val() + selectedTag.slice(last.length - selectedTag.length));
  $("#suggestions").css({'display': 'none'});
  selectedIdx = -1;
}


$(function() {
  populateWithParameters();
  getAllTags();

  if (params.get("expand") == "all") {
    $(".description-container").show();
  }

  let mark_id = 0;
  $("#filter").hide();

  $("#suggestions").on("click", "li", function() {
    let fullTag = $(this).find("a").text();
    completeWithSuggestedTag(fullTag);
  });

  $(".edit_btn").click(function(e) {
    e.preventDefault();
    if ($("#editMarkForm")) {
      $("#editMarkForm").remove();
    }

    mark_id = $(this).attr("mark_id");
    editMarkForm(mark_id, $(this));
  });

  $(".delete_btn").click(function(e) {
    e.preventDefault();
    if (confirm('Are you sure?')) {
      mark_id = $(this).attr("mark_id");
      deleteMark(mark_id);
    }
  });

  $(".bump_btn").click(function(e) {
    e.preventDefault();
    mark_id = $(this).attr("mark_id");
    bumpMark(mark_id);
  });

  $(".info_btn").click(function(e) {
    e.preventDefault();
    mark_id = $(this).attr("mark_id");
    $(".description-container[mark_id='" + mark_id + "']").toggle();
  });

  $(".expand_all_btn").click(function(e) {
    e.preventDefault();
    $(".description-container").show();
    params.set("expand", "all");
    window.history.replaceState({}, '', `${location.pathname}?${params}`);
    changeParams(function() {
      params.set("expand", "all");
    }); // maybe a bit too clever
  });

  $(".collapse_all").click(function(e) {
    e.preventDefault();
    $(".description-container").hide();
    changeParams(function() {
      params.delete("expand");
    });
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
    if ($("#id_name").val() == "") {
      getTitle($("#id_url").val());
    }
  });

  // autocomplete ------------------

  $(document).on("keyup click focus", "#id_tags", function(e) {
    let tagsStr = $("#id_tags").val();

    // autocomplete should display when:
    // caret is on the last character
    // user is not selecting text
    if (tagsStr.substr(-1) != " " &&
        tagsStr.length == this.selectionStart &&
        this.selectionStart == this.selectionEnd) {
      let tags = splitTags(tagsStr);
      let last = tags[tags.length - 1].replace(/ /g, '');
      if (last[0] == "-") { last = last.substr(1); }
      if (last != lastPrefix) {
        filterSuggestions(last);
        selectedIdx = -1;
        lastPrefix = last;
      }
    } else {
      $("#suggestions").css({'display': 'none'});
    }
  });

  $(document).on("keydown", "#id_tags", function(e) {
    switch (e.keyCode) {
    case 40: // up
      suggestionsSelect(1);
      e.preventDefault();
      break;
    case 38: // down
      suggestionsSelect(-1);
      e.preventDefault();
      break;
    case 27: // esc
      e.preventDefault();
      $("#suggestions").css({'display': 'none'});
      break;
    case 13: // enter
      if ($("#suggestions").css("display") != "none") {
        e.preventDefault();
        completeWithSuggestedTag($("#suggestions").children().eq(selectedIdx).find("a").text());
        $("#suggestions").css({'display': 'none'});
      }
      break;
    default:
      break;
    }
  });

  function suggestionsSelect(direction) {
    let list = $("#suggestions");
    list.children().eq(selectedIdx).removeClass("selected");
    selectedIdx += direction;
    list.children().eq(selectedIdx).addClass("selected");
  }

  $(document).on("mousedown", "#suggestions", function(e) {
    // prevents input from blurring when clicking suggestions
    e.preventDefault();
  });

  $(document).on("focusout", "#id_tags", function(e) {
    $("#suggestions").css({'display': 'none'});
  });

  $(document).on("change paste keyup", "#filter", function(e) {
    let filter = $("#filter").val();
    $(".tag_name").each(function(index) {
      if ($(this).text().indexOf(filter) != -1) {
        $(this).parent().show();
      } else {
        $(this).parent().hide();
      }
    });
  });
});
