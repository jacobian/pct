### Notes on how to get this running on Heroku:

Create the app and a postgres db:

```
heroku create
heroku addons:add heroku-postgresql:hobby-basic
```

Use a special GIS buildpack:

```
heroku buildpacks:set https://github.com/TrailStash/heroku-geo-buildpack
heroku buildpacks:add heroku/python
```

Initial push, config and database migration:

```
git push heroku master
heroku config:set DJANGO_SECRET_KEY: ...
heroku run python manage.py migrate
heroku run python manage.py load_halfmile
heroku run python manage.py load_spot
heroku run python manage.py createsuperuser
```

Set up the scheduler:

```
heroku addons:create scheduler:standard
heroku addons:open scheduler
# add a scheduled task for `python manage.py load_spot` -- hourly
# add a scheduled task for `python manage.py update_daily_stats` -- hourly or daily
```
