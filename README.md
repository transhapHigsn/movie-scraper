# Steps

- To create project: `django-admin startproject movie_scraper`
- `cd movie_scaper`
- To create app: `python manage.py startapp api`
- To run server: `python manage.py runserver`
- Migrate Database: `python manage.py migrate`
- Generate Migration for Schema: `python manage.py makemigrations api`
- Check SQL for your migration: `python manage.py sqlmigrate api <migration_name>`

## Setup

- Create virtual environment, run: `virtualenv -p python3 .venv`
- To activate virtual environment, run: `source .venv/bin/activate`
- From project root, run: `pip install -r requirements.txt`
- Migrate Database, run: `cd movie_scraper && python manage.py migrate`
- Run server, run (from movie_scraper folder): `python manage.py runserver`
- To deactivate virtual environemnt, run: `source .venv/bin/deactivate`

Note: There is a one time use code `TYH6430QV` for creating admin user. Further, admin actions (adding new user permissions and scraping IMDB data) should be performed by user created using above code.

## Information related to APIs

- On use of apis `/api/create_admin_user`, `/api/login` and `/api/signup` , an authentication token is returned in response which should be used for futher api requests. Also, this token is valid for only 3 hours.

- APIs that does not require auth token are: `/api/login`, `/api/signup` and `/api/create_admin_user`.
- API `/api/create_admin_user` can only be used once for creating admin users. Once admin user is created, all the following requests to the api will give permission denied error.

- Admin user is responsible for providing permissions and scraping movie info from IMDB.
- To use authentication token, pass it as `jwt` header for all requests.
- API `/api/movie` is used by admin user to scrape and store movie data from IMDB. If a movie is already stored in the database, then it won't be stored next time. Before initiating scraping, provide `fetch_movies` permission to user using `/api/update_user_permission`.

- To view all movies stored, `/api/fetch_movies` is used.
- To fetch movie by title, `/api/fetch_movie_by_name` is used.

- To add or update watchlist and watched list, use `/api/update_movie_list`.
- To get watchlist/watched list, use `/api/get_movie_list`.

- To add or delete user permissions, use `/api/update_user_permission`.
- To get user permissions, use `/api/get_user_permission`

## Information related to Postman Collection

- All postman collections are in file `movie_scraper.postman_collection.json` located at root folder.
- Once token is generated from apis (`/api/create_admin_user`, `/api/login` and `/api/signup`) make sure to replace it in collection's header.
