const baseURL = "https://bmarks.net/add/";

// shortcuts
browser.commands.onCommand.addListener((command) => {
  callCommandFunction(command);
});

// popup
browser.runtime.onMessage.addListener((message) => {
  callCommandFunction(message.command);
});

function callCommandFunction(command) {
  switch (command) {
  case "bookmark-current":
    bookmarkCurrentPage(); break;
  case "bookmark-all":
    bookmarkAllTabsOnWindow(); break;
  }
}

function createTabAndSendMessage(message) {
  browser.tabs.create({url: baseURL}).then((marksTab) => {
    browser.tabs.executeScript({code: ''}).then(() => {
      browser.tabs.sendMessage(marksTab.id, message);
    });
  });
}

function bookmarkCurrentPage() {
  browser.tabs.query({currentWindow: true, active: true}).then((tabs) => {
    let title = tabs[0].title;
    let url = tabs[0].url;

    createTabAndSendMessage({command: "insertCurrentTab", title: title, url: url});
  });
}

function bookmarkAllTabsOnWindow() {
  browser.tabs.query({currentWindow: true}).then((tabs) => {
    let description = tabs.map(tab => `- [${ tab.title }](${ tab.url })`).join("\\n");

    createTabAndSendMessage({command: "insertAllTabs", description: description});
  });
}
