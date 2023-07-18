from flask import Flask, request, render_template
import redis

app = Flask(__name__)

import os

REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = os.environ['REDIS_PORT']

POSTGRES_HOST = os.environ['POSTGRES_HOST']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PORT = os.environ['POSTGRES_PORT']
POSTGRES_DB = os.environ['POSTGRES_DB']
POSTGRES_PASSWORD = os.environ['PGPASSWORD']

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

# postgresql://username:password@host:port/database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev'

from models import db, CustomerFavs

db.init_app(app)
with app.app_context():
    # To create / use database mentioned in URI
    db.create_all()
    db.session.commit()

red = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/save", methods=['POST'])
def save():
    customer = str(request.form['customer']).lower()
    place = str(request.form['place']).lower()
    food = str(request.form['food']).lower()

    # check if data of the customer already exists in the redis
    if red.hgetall(customer).keys():
        print("hget customer:", red.hgetall(customer))
        # return a msg to the template, saying the customer already exists(from redis)
        return render_template('index.html', customer_exists=1, msg='(From Redis)', customer=customer, place=red.hget(customer,"place").decode('utf-8'), food=red.hget(customer,"food").decode('utf-8'))

    # if not in redis, then check in db
    elif len(list(red.hgetall(customer)))==0:
        record =  CustomerFavs.query.filter_by(customer=customer).first()
        print("Records fecthed from db:", record)
        
        if record:
            red.hset(customer, "place", place)
            red.hset(customer, "food", food)
            # return a msg to the template, saying the customer already exists(from database)
            return render_template('index.html', customer_exists=1, msg='(From DataBase)', customer=customer, place=record.place, food=record.food)

    # if data of the customer doesnot exist anywhere, create a new record in DataBase and store in Redis also
    # create a new record in DataBase
    new_record = CustomerFavs(customer=customer, place=place, food=food)
    db.session.add(new_record)
    db.session.commit()

    # store in Redis also
    red.hset(customer, "place", place)
    red.hset(customer, "food", food)

    # cross-checking if the record insertion was successful into database
    record =  CustomerFavs.query.filter_by(customer=customer).first()
    print("Records fetched from db after insert:", record)

    # cross-checking if the insertion was successful into redis
    print("key-values from redis after insert:", red.hgetall(customer))

    # return a success message upon saving
    return render_template('index.html', saved=1, customer=customer, place=red.hget(customer, "place").decode('utf-8'), food=red.hget(customer, "food").decode('utf-8'))

@app.route("/keys", methods=['GET'])
def keys():
	records = CustomerFavs.query.all()
	names = []
	for record in records:
		names.append(record.customer)
	return render_template('index.html', keys=1, customers=names)


@app.route("/get", methods=['POST'])
def get():
	customer = request.form['customer']
	print("customer:", customer)
	customer_data = red.hgetall(customer)
	print("GET Redis:", customer_data)

	if not customer_data:
		record = CustomerFavs.query.filter_by(customer=customer).first()
		print("GET Record:", record)
		if not record:
			print("No data in redis or db")
			return render_template('index.html', no_record=1, msg=f"Record not yet defined for {customer}")
		red.hset(customer, "place", record.place)
		red.hset(customer, "food", record.food)
		return render_template('index.html', get=1, msg="(From DataBase)",customer=customer, place=record.place, food=record.food)
	return render_template('index.html',get=1, msg="(From Redis)", customer=customer, place=customer_data[b'place'].decode('utf-8'), food=customer_data[b'food'].decode('utf-8'))