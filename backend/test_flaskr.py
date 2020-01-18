import os
import unittest
import json
import random
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.username = 'nsmichelson'
        self.password = 'nsmichelson'
        self.database_path = "postgres://{}:{}@{}/{}".format(self.username,self.password,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    #get questions successfully
    def test_getCategories(self):
        response = self.client().get('/api/categories')

        data = json.load(response)

        self.assertEqual(data['success'],True)
        self.assetTrue(data['categories'])

    #get cateogires successfully
    def test_getQuestions(self):
        response =self.client().get('/api/questions')
        data = json.load(response.data)

        self.assertEqual(date['success'],True)
        self.assertTrue(date['questions'])
    #delete a question successfully
    def test_deletesQ(self):
        random_q = random.choice([question.id for question in Question.query.all()])
        response = self.client().delete('api/questions/{}'.format(random_q))

        data = json.load(response)
        self.assertEqual(["success"],True)
        self.assertTrue(data['questions'])
    #create a quiz

    def test_quiz(self):
        random_category = random.choice([category.id for category in Category.query.all()])
        response = self.client().post('/api/quizzes',json={'previous_questions': [],'quiz_category': {'type': 'Art','id': '2'}})

        data = json.load(response.data)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])

         
    #add a question
    def test_addQ(self):
        qToAdd  = {'question':'Test','answer':'Test Answer','category':1,'difficulty':1}
        response=self.client().post('/api/questions',json=qToAdd)

        data = json.load(response.data)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['created'])



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()