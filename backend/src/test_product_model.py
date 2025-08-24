import unittest
from app import app, db, Product
from sqlalchemy.exc import IntegrityError

class ProductModelTestCase(unittest.TestCase):
    def setUp(self):
        # Use an in-memory SQLite database for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_product(self):
        product = Product(
            upc='111111111111',
            name='Test Product',
            department_name='Test Dept',
            department_num=1,
            cost=1.0,
            price=2.0,
            category='TestCat'
        )
        product.add_to_database()
        fetched = Product.query.filter_by(upc='111111111111').first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, 'Test Product')

    def test_update_product(self):
        product = Product(
            upc='222222222222',
            name='Old Name',
            department_name='Dept',
            department_num=2,
            cost=2.0,
            price=3.0,
            category='Cat'
        )
        product.add_to_database()
        product.update_in_database(name='New Name', price=4.0)
        updated = Product.query.filter_by(upc='222222222222').first()
        self.assertEqual(updated.name, 'New Name')
        self.assertEqual(updated.price, 4.0)

    def test_delete_product(self):
        product = Product(
            upc='333333333333',
            name='Delete Me',
            department_name='Dept',
            department_num=3,
            cost=3.0,
            price=4.0,
            category='Cat'
        )
        product.add_to_database()
        db.session.delete(product)
        db.session.commit()
        deleted = Product.query.filter_by(upc='333333333333').first()
        self.assertIsNone(deleted)

    def test_get_multiple_products(self):
        products = [
            Product(upc='444444444444', name='P1', department_name='D1', department_num=4, cost=4.0, price=5.0, category='C1'),
            Product(upc='555555555555', name='P2', department_name='D2', department_num=5, cost=5.0, price=6.0, category='C2'),
        ]
        for p in products:
            p.add_to_database()
        all_products = Product.query.all()
        self.assertEqual(len(all_products), 2)
        upcs = [p.upc for p in all_products]
        self.assertIn('444444444444', upcs)
        self.assertIn('555555555555', upcs)

if __name__ == '__main__':
    unittest.main()
