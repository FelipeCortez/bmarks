let baseURL = "https://bmarks.net";

function onGotAll(tabs) {
  let i = 0;
  let description = "";

  for (i = 0; i < tabs.length; ++i) {
    description += `- [${ tabs[i].title }](${ tabs[i].url })\n`;

    if (tabs[i].active) {
      let activeTab = tabs[i];
    }
  }

  var encodedUrl = baseURL + "/add/?name=" + "Tab collection" + "&description=" + encodeURIComponent(description) + "&tags=tab-collection";

  browser.tabs.create({
    url: encodedUrl
  });
}

function onGotActive(tabs) {
  var encodedUrl = baseURL + "/add/?name=" + encodeURIComponent(tabs[0].title) + "&url=" + encodeURIComponent(tabs[0].url);

  browser.tabs.create({
    url: encodedUrl
  });
}

function onError(error) {
  //
}

let active  = document.getElementById("addActiveButton");
let allTabs = document.getElementById("allTabsButton");

active.onclick = function() {
  browser.tabs.query({currentWindow: true, active: true}).then(onGotActive, onError);
};

allTabs.onclick = function() {
  browser.tabs.query({currentWindow: true}).then(onGotAll, onError);
};
