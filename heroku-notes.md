### Notes on how to get this running on Heroku:

Create the app and a postgres db:

```
heroku create
heroku addons:add heroku-postgresql:hobby-basic
```

Need a special buildpack for gis:

```
heroku buildpacks:set https://github.com/cyberdelia/heroku-geo-buildpack.git
heroku buildpacks:add heroku/python
```

