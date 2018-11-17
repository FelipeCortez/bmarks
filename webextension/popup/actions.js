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

for (let shortcutSpan of document.querySelectorAll(".shortcut")) {
  let rows = Array.from(shortcutSpan.innerText)
                   .map((char) => `<td>${ char }</td>`)
                   .join('');

  shortcutSpan.innerHTML = `<table><tr>${ rows }</tr></table>`;
}
