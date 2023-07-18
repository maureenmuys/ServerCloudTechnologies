from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()

class CustomerFavs(db.Model):
	customer = db.Column(db.String, primary_key=True)
	place = db.Column(db.String)
	food = db.Column(db.String)

	def __init__(self, customer, place, food):
		self.customer=customer
		self.place=place
		self.food=food

	def __repr__(self):
		return f'<User-Place-Food : {self.customer}-{self.place}-{self.food}'

