# Marks

A bookmarking tool made with Python 3 + Django 1.10. Running [here](https://bmarks.net/felipecortez).

## Features

- [x] Import bookmarks saved in the Netscape format
- [x] Tag completion in forms
- [x] Private marks with `private` tag
- [x] Descriptions with Markdown support
- [x] A friendly user guide (not so friendly yet)
- [x] A bookmarklet
- [x] Unlisted marks with dot prefix
- [ ] Bulk editing
- [ ] Wayback Archive Availability API integration
- [ ] Browser extensions
- [ ] JavaScriptless mode

## Bookmarklet

```javascript:location.href='https://bmarks.net/add/?url='+encodeURIComponent(location.href)+'&name='+encodeURIComponent(document.title)```
