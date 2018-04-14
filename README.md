# Marks

A bookmarking tool made with Python 3 + Django 2.0. Running [here](https://bmarks.net/felipecortez).

## Features

- [x] Import bookmarks saved in the Netscape format
- [x] Tag completion in forms
- [x] Private marks with `private` tag
- [x] Private accounts
- [x] Descriptions with Markdown support
- [x] A friendly user guide (not so friendly yet)
- [x] A bookmarklet
- [x] Unlisted marks with dot prefix
- [x] Browser extension (Firefox only currently)
- [x] Bulk editing
- [ ] Wayback Archive Availability API integration
- [ ] JavaScriptless mode
- [ ] Export bookmarks

## Bookmarklet

```javascript:location.href='https://bmarks.net/add/?url='+encodeURIComponent(location.href)+'&name='+encodeURIComponent(document.title)```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
