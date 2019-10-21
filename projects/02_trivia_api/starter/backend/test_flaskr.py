import os
import unittest
import json
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
        self.database_path = "postgres://sairam:sairam@{}/{}".format('localhost:5432', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions(self):
        for index in 1,2:
            res = self.client().get('/questions/?page=' + str(index))
            data = json.loads(res.data)
            #print("test_get_paginated_questions", data)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], 'True')
            self.assertTrue(data['questions'])
            self.assertTrue(len(data['questions']))

    def test_get_paginated_questions_error(self):
        index = 10
        res = self.client().get('/questions/?page=' + str(index))
        data = json.loads(res.data)
        #print("datea: " , data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], 'False')
        self.assertEqual(0, len(data['questions']))

    def test_delete_question(self):
        res = self.client().post('/questions', json={'question' : 'what is your name?',
        'answer' : 'bot', 'difficulty' : '1', 'category' : '4' })
        question = Question.query.filter_by(question = 'what is your name?').first()
        question.id = 1
        question.update()
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], 'True')

    def test_delete_question_error(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)

    def test_add_question(self):
        res = self.client().post('/questions', json={'question' : 'what is your name?',
        'answer' : 'bot', 'difficulty' : '1', 'category' : '4' })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], 'True')

    def test_add_question_error(self):
        res = self.client().post('/questions', json={'question' : 'what is your name?'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)


    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm' : 'cup'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_quizzes_question(self):
        res = self.client().post('/quizzes', json={'quiz_category' : { 'type' : 'click' , 'id' : '0'}, 'previous_questions' : ''})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertTrue(len(data['question']))

    def test_quizzes_question_error(self):
        res = self.client().post('/quizzes', json={'quiz_category' : { 'type' : 'click' , 'id' : '0'}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()