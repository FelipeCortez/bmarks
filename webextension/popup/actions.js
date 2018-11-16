const activeBtn  = document.getElementById("add-active-button");
const allTabsBtn = document.getElementById("all-tabs-button");

activeBtn.onclick = function() {
  browser.runtime.sendMessage({command: "bookmark-current"});
  window.close();
};

allTabsBtn.onclick = function() {
  browser.runtime.sendMessage({command: "bookmark-all"});
  window.close();
};
