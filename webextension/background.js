function onGot(tabs) {
  let tab = tabs[0];
  var encodedUrl = "https://bmarks.net/add/?url=" + encodeURIComponent(tab.url) + "&name=" + encodeURIComponent(tab.title);

  browser.tabs.create({
    url: encodedUrl
  });
}

function onError(error) {
  //
}

function openPage() {
  browser.tabs.query({currentWindow: true, active: true}).then(onGot, onError);
}

browser.browserAction.onClicked.addListener(openPage);
