import os
import unittest
import json
import logging
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
        self.database_path = "postgresql://postgres:postgres@{}/{}".format('localhost:5432', self.database_name)
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
    
    ## get all categories
    def test_get_all_category_with_results(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        cat_dict = {'1':'Science', '2':'Art', '3':'Geography', '4':'History', '5':'Entertainment', '6':'Sports'}
        self.assertEqual(data['categories'], cat_dict)
   
    ##get all questions
    def test_get_all_questions_with_results(self):
        res = self.client().get('/questions?=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        tst_cat = {"1":"Science","2":"Art","3":"Geography","4":"History","5":"Entertainment","6":"Sports"}
        self.assertEqual(data['categories'], tst_cat)
        
        tst_cur_cat = "Science"
        self.assertEqual(data['currentCategory'], tst_cur_cat)
        tst_ques = [{'answer': 'Maya Angelou', 'category': 4, 'difficulty': 2, 'id': 1, 'question': "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"}, \
                    {'answer': 'Muhammad Ali', 'category': 4, 'difficulty': 1, 'id': 2, 'question': "What boxer's original name is Cassius Clay?"}, \
                    {'answer': 'Apollo 13', 'category': 5, 'difficulty': 4, 'id': 3, 'question': 'What movie earned Tom Hanks his third straight Oscar nomination, in 1996?'}, \
                    {'answer': 'Tom Cruise', 'category': 5, 'difficulty': 4, 'id': 4, 'question': 'What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?'}, \
                    {'answer': 'Edward Scissorhands', 'category': 5, 'difficulty': 3, 'id': 5, 'question': 'What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?'}, \
                    {'answer': 'Brazil', 'category': 6, 'difficulty': 3, 'id': 6, 'question': 'Which is the only team to play in every soccer World Cup tournament?'}, \
                    {'answer': 'Uruguay', 'category': 6, 'difficulty': 4, 'id': 7, 'question': 'Which country won the first ever soccer World Cup in 1930?'}, \
                    {'answer': 'George Washington Carver', 'category': 4, 'difficulty': 2, 'id': 8, 'question': 'Who invented Peanut Butter?'}, \
                    {'answer': 'Lake Victoria', 'category': 3, 'difficulty': 2, 'id': 9, 'question': 'What is the largest lake in Africa?'}, \
                    {'answer': 'The Palace of Versailles', 'category': 3, 'difficulty': 3, 'id': 10, 'question': 'In which royal palace would you find the Hall of Mirrors?'}]
        
        self.assertEqual(data['questions'], tst_ques)
        
        tst_tot_ques = 21
        self.assertEqual(data['totalQuestions'], tst_tot_ques)
    
    ##delete a question THIS ONE IS DONE
    def test_delete_question_with_results(self):
        res = self.client().delete('/questions/2/')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    ##post a new question
    def test_new_question_with_results(self):
        res = self.client().post('/questions', json={'question': 'How is this working?', 'answer': 'yes', 'category': 4, 'difficulty': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], 'How is this working?')
        self.assertEqual(data['answer'], 'yes')
        self.assertEqual(data['category'], 4)
        self.assertEqual(data['difficulty'], 1)

    ##question bases on search    
    def test_get_question_search_with_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'Which'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 7)

    ##get question based on category
    def test_get_question_based_on_category_with_results(self):
        res = self.client().get('/categories/5/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        tst_cur_cat = ''
        self.assertEqual(data['currentCategory'], tst_cur_cat)

        tst_ques = [{"answer":"Apollo 13", "category":5, "difficulty":4, "id":3, "question":"What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"}, \
                    {"answer":"Tom Cruise", "category":5, "difficulty":4, "id":4, "question":"What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"}, \
                    {"answer":"Edward Scissorhands", "category":5, "difficulty":3, "id":5, "question":"What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"}] 

        self.assertEqual(data['questions'], tst_ques)
        tst_tot_ques = 3
        self.assertEqual(data['totalQuestions'], tst_tot_ques)


    #post question to play quiz
    def test_quiz_with_results(self):
        res = self.client().post('/quizzes', json = {'previous_questions': [17, 18, 22], 'quiz_category': 'Science'})
        data = json.loads(res.data)
        question_dict = data['question']

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question_dict['question'], 'What is the heaviest organ in the human body?')
        self.assertEqual(question_dict['answer'], 'The Liver')
        self.assertEqual(question_dict['category'], 1)
        self.assertEqual(question_dict['difficulty'], 4)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()