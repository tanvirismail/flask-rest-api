python3 -m venv env
source env/bin/activate

pip3 install pipenv
pipenv shell
pipenv install flask flask-sqlalchemy flask-marshmallow marshmallow-sqlalchemy
