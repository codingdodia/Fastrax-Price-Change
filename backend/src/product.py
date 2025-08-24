from app import db
from sqlalchemy.exc import IntegrityError

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upc = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    department_name = db.Column(db.String, nullable=False)
    department_num = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String, nullable=False)


    def add_to_database(self, **kwargs):

        db.session.add(self)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            print(f"Unique Constraint Violation: {e}")

        product = Product.query.filter_by(upc=self.upc).first()
        if not product:
            return False

        for key, value in kwargs.items():
            setattr(product, key, value)
        db.session.commit()

    def get_product_from_database(self, upc):
        return Product.query.filter_by(upc=upc).first()

    def update_in_database(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'upc': self.upc,
            'name': self.name,
            'department_name': self.department_name,
            'department_num': self.department_num,
            'cost': self.cost,
            'price': self.price,
            'category': self.category
        }