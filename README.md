# server

## Project setup

You need `python 3.8 +`  and [TMDB API key](https://developers.themoviedb.org/3/getting-started/introduction) to run this project.

## Instruction

1️⃣ **make Python virtual environment.** 

```
python -m venv venv
```

2️⃣ **activate virtual environment.**

WINDOWS

```
source venv/Scripts/activate
```

MAC

```
source venv/bin/activate
```

3️⃣ **install requirements**

```
pip install -r requirements.txt
```

4️⃣ **make `secrets.json` to your root directory. Your `secrets.json` needs to be like** 

```
{
  "SECRET_KEY": "django-insecure-{{YOUR_SECRET_KEY_HERE}}"
}
```

😒 **This little trick might help you.**

https://github.com/openwisp/ansible-openwisp2/blob/master/files/generate_django_secret_key.py

5️⃣ Put Your TMDB api key in `movies/views.py` at 23

```python
tmdb.API_KEY = 'YOUR_API_KEY_HERE'
```

6️⃣ **Make migrations, migrate, and GO!**

```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

