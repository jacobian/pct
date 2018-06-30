### Notes on how to get this running on Heroku:

Create the app and a postgres db:

```
heroku create
heroku addons:add heroku-postgresql:hobby-basic
```

Initial push, config and database migration:

```
git push heroku master
heroku config:set DJANGO_SECRET_KEY: ...
