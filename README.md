# Steps

- To create project: `django-admin startproject movie_scraper`
- `cd movie_scaper`
- To create app: `python manage.py startapp api`
- To run server: `python manage.py runserver`
- Migrate Database: `python manage.py migrate`
- Generate Migration for Schema: `python manage.py makemigrations api`
- Check SQL for your migration: `python manage.py sqlmigrate api <migration_name>`

## Setup

- From project root, run: `pip install -r requirements.txt`

Note: There is a one time use code `TYH6430QV` for creating admin user. Further, admin actions should be performed by user created using above code.
