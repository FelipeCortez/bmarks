(function() {
  if (window.hasRun) {
    return;
  }

  window.hasRun = true;

  function insertAllTabs(description) {
    let tagsField = document.querySelector("#id_tags");
    tagsField.value = ".tab-collection";

    let descriptionField = document.querySelector("#id_description");
    descriptionField.value = description;
    descriptionField.style.height = (descriptionField.scrollHeight + 10) + "px";

    let titleField = document.querySelector("#id_name");
    titleField.focus();
  }

  function insertCurrentTab(title, url) {
    let urlField = document.querySelector("#id_url");
    urlField.value = url;

    let titleField = document.querySelector("#id_name");
    titleField.value = title;
    titleField.focus();
  }

  browser.runtime.onMessage.addListener((message) => {
    if (message.command === "insertAllTabs") {
      insertAllTabs(message.description);
    } else if (message.command === "insertCurrentTab") {
      insertCurrentTab(message.title, message.url);
    }
  });
})();
