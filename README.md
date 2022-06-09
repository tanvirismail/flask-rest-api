python3 -m venv env
source env/bin/activate

pip3 install pipenv
pipenv shell
pipenv install flask flask-sqlalchemy flask-marshmallow marshmallow-sqlalchemy

## migrate
pip install Flask-Migrate
flask db init
flask db migrate -m "Initial migration."
flask db upgrade

## VALIDATION
pip install flask-wtf
pip install wtforms-json
pip install email_validator