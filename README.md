# bmarks

[![Build Status](https://travis-ci.org/FelipeCortez/bmarks.svg?branch=master)](https://travis-ci.org/FelipeCortez/bmarks)

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
- [x] [Browser extension](https://addons.mozilla.org/en-US/firefox/addon/bmarks/?src=userprofile) (Firefox only currently)
- [x] Bulk editing
- [x] Export bookmarks (JSON, CSV)
- [x] [Wayback Machine](https://archive.org/web/) Availability API integration
- [ ] Archive with full-text search
- [ ] Toggle between compact/one-line and spacious/multi-line views

## Bookmarklet

```javascript:location.href='https://bmarks.net/add/?url='+encodeURIComponent(location.href)+'&name='+encodeURIComponent(document.title)```

## Running with Docker

In a staging environment, run `export DJANGO_DEVELOPMENT=1` before starting your containers.

In the `app` folder, run `docker-compose up --build`.

To run the migrations, `docker-compose run web python3 manage.py migrate`.

The application should be up and running afterwards.

In a production environment, set `STATIC_ROOT`, run `collectstatic` and serve the static files with Nginx or Apache as mentioned in the [Django documentation](https://docs.djangoproject.com/en/2.2/howto/static-files/deployment/).

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
