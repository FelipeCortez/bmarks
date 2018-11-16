const activeBtn  = document.getElementById("add-active-button");
const allTabsBtn = document.getElementById("all-tabs-button");

activeBtn.onclick = function() {
  bookmarkCurrentPage();
};

allTabsBtn.onclick = function() {
  bookmarkAllTabsOnWindow();
};
