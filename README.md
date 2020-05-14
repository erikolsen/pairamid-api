# pairamid-api
A python backed for a pairing matrix app
Install dependencies
$ pip install -r requirements.txt
Start up DB
$ docker pull postgresql
$ docker run --rm --name pg-pairamid -e POSTGRES_PASSWORD=docker -d -p 5432:5432 postgres
Setup DB
$ flask db upgrade
Seed DB with sample data
$ flask add-users
$ flask add-pairs
Start app
$ flask run
