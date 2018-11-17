function createCommandElement(name, shortcut, command) {
  var aElement = document.createElement("a");
  aElement.classList.add("button");

  var textElement = document.createElement("span");
  textElement.innerText = name;
  textElement.classList.add("text");
  aElement.appendChild(textElement);

  if (shortcut !== null) {
    var shortcutElement = document.createElement("span");
    shortcutElement.innerText = shortcut;
    shortcutElement.classList.add("shortcut");
    aElement.appendChild(shortcutElement);
  }

  aElement.onclick = () => {
    browser.runtime.sendMessage({command: command});
    window.close();
  };

  return aElement;
}

browser.commands.getAll().then((commands) => {
  const commandsElement = document.getElementById("commands");

  for (command of commands) {
    commandsElement.appendChild(createCommandElement(command.description, command.shortcut, command.name));
  }
});
