const baseURL = "https://bmarks.net/add/";

function onGotAll(tabs) {
  let description = "";

  for (let tab of tabs) {
    description += `- [${ tab.title }](${ tab.url })\\n`;
  }

  let contentScript = `
    let tagsField = document.querySelector("#id_tags");
    tagsField.value = ".tab-collection";

    let descriptionField = document.querySelector("#id_description");
    descriptionField.value = "${ description }";
    descriptionField.style.height = (descriptionField.scrollHeight + 10) + "px";

    let titleField = document.querySelector("#id_name");
    titleField.focus();
  `;

  browser.tabs.create({url: baseURL})
    .then(() => { browser.tabs.executeScript({code: contentScript}); window.close(); });
}

function onGotActive(tabs) {
  let contentScript = `
    let urlField = document.querySelector("#id_url");
    urlField.value = "${ tabs[0].url }";

    let titleField = document.querySelector("#id_name");
    titleField.value = "${ tabs[0].title }";
    titleField.focus();
  `;

  browser.tabs.create({url: baseURL})
    .then(() => { browser.tabs.executeScript({code: contentScript}); window.close(); });
}

function bookmarkCurrentPage() {
  browser.tabs.query({currentWindow: true, active: true})
    .then(onGotActive);
}

function bookmarkAllTabsOnWindow() {
  browser.tabs.query({currentWindow: true})
    .then(onGotAll);
}
