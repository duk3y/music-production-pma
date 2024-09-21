# Music Review Application

## Prerequisites
- This app is compatible with Python 3.8 and 3.9. It is recommended to use one of those versions.

## Steps to building project
1. Clone repo
2. Create a new virtual enviroment by running `python -m venv ./venv` and then activating it.  For MacOS, this is `source ./venv/bin/activate`.  For Windows, it is `.\venv\Scripts\activate`. Pycharm also has its own built-in venv that you could use instead.
3. Run "pip install -r requirements.txt" to install the correct dependencies.

## Accessing the App
1. To run it locally run "py manage.py runserver"
2. Push your changes to main, when changes are pushed to main (and the changes pass all tests) the new code will be deployed to the heroku app. To see deployed app navigate to "https://music-production-pm-app-da1846f20d32.herokuapp.com/"

## Migrations
1. Locally apply migrations by running "python manage.py makemigrations" to create your migration files
2. Apply migrations to local database by running "python manage.py migrate"
3. Since Heroku handles its own database once code is deployed to Heroku run "Heroku run python manage.py migrate" with the Heroku CLI (devops only has access to this) to affect non-local databases.

## Static Files
1. If you add/update any static files, this includes CSS, Javascript, Images, run "python manage.py collectstatic" before pushing changes to main/deploying to heroku.

## Troubleshooting
1. In order for changes to be deployed to the heroku app from main, code changes must pass all tests in the workflow run. To see if your build passed navigate to "Actions" and click on the last workflow run to see if it suceeded/logs. It will then be deployed to Heroku where the application will be built - Devops has access to the logs for that process if you find that your changes are not being reflected in the heroku app.
2. Many times issues occur when migrations are not fully ran, reference migrations above.
3. Make sure to collect static files - not doing so can result in 404's and unexpected broken functionality, as static files won't be available in the Heroku app.
