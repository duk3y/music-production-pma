# Music Review Application

## Steps to building project
1. Clone repo
2. Create a new virtual enviroment by running `python -m venv ./venv` and then activating it.  For MacOS, this is `source ./venv/bin/activate`.  For Windows, it is `.\venv\Scripts\activate`. Pycharm also has its own built-in venv that you could use instead.
3. Run "pip install -r requirements.txt" to install the correct dependencies.

## Accessing the App
1. To run it locally run "py manage.py runserver"
2. To see the app deployed from main navigate to "https://music-production-pm-app-da1846f20d32.herokuapp.com/"

## Migrations
1. Locally apply migrations by running "python manage.py makemigrations" to create your migration files
2. Apply migrations to local database by running "python manage.py migrate"
3. Since Heroku handles its own database once code is deployed to Heroku run "Heroku run python manage.py migrate" with the Heroku CLI (devops only has access to this) to affect non-local databases.

## Troubleshooting
1. In order for changes to be deployed to the heroku app from main, code changes must pass all tests in the workflow run. To see if your build pass navigate to "Actions" and click on the last workflow run to see if it suceeded/logs. Devops manager also has access to the build logs for Heroku if you need more extensive logs.
2. Many times issues occur when migrations are not fully ran, reference migrations above.