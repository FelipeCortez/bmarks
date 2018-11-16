browser.commands.onCommand.addListener((command) => {
  if (command == "bookmark-current") {
    bookmarkCurrentPage();
  } else if (command == "bookmark-all") {
    bookmarkAllTabsOnWindow();
  }
});
