# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_to_read_a_product(self):
        """ It should read a product from the database """
        # Step 1 create a product, make log note
        product = ProductFactory()
        logging.info("Created a product to test read")
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Step 2 read it back and make sure it got the info right
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_to_update_a_product(self):
        """ This should update a product """
        # Step 1 create a product, make log note
        product = ProductFactory()
        logging.info("Created a product to test read product")
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        logging.info("Product info check")

        # Step 2 Change the description and save changes
        product.description = "testing"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "testing")
        logging.info("updated product description to")

        # Step 3 Make sure the ID didn't change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "testing")
        logging.info("done testing update descriptions")

    def test_delete_a_product(self):
        """ It should be able to detlete an item """
        # step 1 create an item, make sure it is there
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # Step 2 delete the item
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_to_list_all_products(self):
        """ It should list all products """
        # Step 1 make products and put product list
        # make 5 products
        products = Product.all()
        self.assertEqual(products, [])
        for _ in range(5):
            product = ProductFactory()
            product.create()

        # step 2, should get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_to_find_a_product_by_name(self):
        """ It should find a product by name """
        # step 1 create a batch of 5 products and save them
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        # step 2 get the name
        name = products[0].name
        # step 3 count occurances
        count = len([product for product in products if product.name == name])
        # step 4 retreive producst by name
        found = Product.find_by_name(name)
        # step 5 assert count is equal
        self.assertEqual(found.count(), count)
        # step 6 match names
        for product in found:
            self.assertEqual(product.name, name)

    def test_to_find_a_product_by_availabiliyt(self):
        """ should be able to find by availabilty """
        # step 1 create batch of 10 products & save them
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # step 2 get the availability of the first product
        available = products[0].available
        # step 3 count the number of occurrences
        count = len([product for product in products if product.available == available])
        # step 4 get products from the database that are available
        found = Product.find_by_availability(available)
        # step 5 check count
        self.assertEqual(found.count(), count)
        # assert each matches
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """ It should Find Products by Category """
        # step 1 use batch to make 10 items
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # step 2 get category of the first product
        category = products[0].category
        # step 3 Count the number of occurrences
        count = len([product for product in products if product.category == category])
        # step 4 get products from the database
        found = Product.find_by_category(category)
        # step 5 Assert if the count of the found products matches the expected count.
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    # OTHER TESTS TO HELP GET CODE COVERAGE ABOVE 95% #
    def test_find_by_price(self):
        """It should Find Products by Price"""
        # step 1 use batch to make 10 items
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # step 2 get price of the first product
        price = products[0].price
        # step 3 Count the number of occurrences
        count = len([product for product in products if product.price == price])
        # step 4 get products from the database
        found = Product.find_by_price(price)
        # step 5 Assert if the count of the found products matches the expected count.
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.price, price)

    def test_find_by_price_str(self):
        """It should Find Products by string Price"""
        # step 1 use batch to make 10 items
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # step 2 get price of the first product
        price = products[0].price
        # step 3 Count the number of occurrences
        count = len([product for product in products if product.price == price])
        # step 4 get products from the database
        found = Product.find_by_price(str(price))
        # step 5 Assert if the count of the found products matches the expected count.
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.price, price)

    def test_to_update_a_product_with_empty_name(self):
        """ This should NOT update a product with an empty name """
        # had to add import DataValidationError at the top of the file
        # Step 1 create a product, make log note
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Step 2 Change the description and save changes
        product.description = "testing"
        product.id = None
        with self.assertRaises(DataValidationError):
            product.update()
