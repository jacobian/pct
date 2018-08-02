### Notes on how to get this running on Heroku:

Create the app and a postgres db:

```
heroku create
heroku addons:add heroku-postgresql:hobby-basic
```

Build GIS libs:

```
heroku config:set BUILD_WITH_GEO_LIBRARIES=1
```

Initial push, config and database migration:

```
git push heroku master
heroku config:set DJANGO_SECRET_KEY=...
heroku config:set heroku config:set INATURALIST_CLIENT_ID=... INATURALIST_CLIENT_SECRET=... INATURALIST_USERNAME=... INATURALIST_PASSWORD=...
heroku run python manage.py migrate
heroku run python manage.py load_halfmile
heroku run python manage.py createsuperuser
```

Set up the scheduler:

```
heroku addons:create scheduler:standard
heroku addons:open scheduler
# add a scheduled task for `python manage.py load_spot` -- hourly
# add a scheduled task for `python manage.py update_daily_stats` -- hourly or daily
# add a scheduled task for `python manage.py load_inaturalist` -- hourly
```
