import os
from flask import Flask, request, abort, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.sql.sqltypes import String
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json
import sys

from models import setup_db, session, Question, Category

QUESTIONS_PER_PAGE = 3

def page_paginate(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  #@cross_origin
  def get_categories():
    try:
      cat_dict = {}
      categories = Category.query.order_by(Category.type).all()
      
      for category in categories:
        cat_dict[category.id] = category.type

      return jsonify({
      'success': True,
      'categories': cat_dict,
      })
      
    except Exception as e:
      abort(422)

  '''
  @TODO: Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  #@cross_origin
  def get_questions():
    # Implement pagniation
    try:
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + 10

      current_category = request.args.get('current_category', 'Science', type=String)
      questions = session.query(Question).all()
      formatted_question = [question.format() for question in questions]
      
      cat_dict = {}
      categories = session.query(Category).all()
      for category in categories:
        cat_dict[category.id] = category.type
  
      return jsonify({
        'success': True,
        'questions':formatted_question[start:end],
        'totalQuestions':len(formatted_question),
        'categories': cat_dict,
        'currentCategory': current_category,
        'page': page
        })
    except Exception as e:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    
  @app.route('/questions/<int:question_id>/', methods=['DELETE'])
  def delete_questions(question_id):

    question = Question.query.filter(Question.id == question_id).one_or_none()
    if question is None:
      abort(404)

    try:  
      question.delete()
      
      return jsonify({
        'success': True,
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  

  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods=['POST'])
  def create_or_search_question():

    try:
      body = request.get_json()
      search_term = body.get('searchTerm', None)

      if search_term == None:
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        q1 = Question(question=new_question, answer=new_answer, category_id=new_category, difficulty=new_difficulty)
        
        q1.insert()

        return jsonify({
          'success': True,
          'question': new_question,
          'answer': new_answer,
          'category': new_category,
          'difficulty': new_difficulty
        })

      else:
        current_category = body.get('current_category', None)

        question_list = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

        formatted_question = [question.format() for question in question_list]

        return jsonify({
          'success': True,
          'questions':formatted_question,
          'total_questions':len(formatted_question),
          'currentCategory': current_category
        })       

    except Exception as e:
      abort(422)


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  
  @app.route('/categories/<int:category_id>/questions')
  #@cross_origin....put a 404
  def get_questions_for_category(category_id):
    # Implement pagniation
    try:
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + 10

      current_category = request.args.get('current_category', '', type=String)
      questions = session.query(Question).filter_by(category_id = category_id).all()

      if questions is None:
        abort(404)

      formatted_question = [question.format() for question in questions]

      return jsonify({
        'success': True,
        'questions':formatted_question[start:end],
        'totalQuestions':len(formatted_question),
        'currentCategory': current_category
        })
    
    except Exception as e:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  
  @app.route('/quizzes', methods=['POST'])
  def quiz():
    try:
      body = request.get_json()
      
      previous_questions = body.get('previous_questions', None)
      quiz_category = body.get('quiz_category', None)

      result = session.query(Question).join(Category).filter(Question.id.notin_(previous_questions)).filter(Category.type == quiz_category)
      formatted_question = [question.format() for question in result]

      rand_question = {'answer': '', 'category': '', 'difficulty': '', 'id': '', 'question': ''}
      if len(formatted_question) > 0:
        rand_question = random.choice(formatted_question)

      return jsonify({
        'success': True,
        'question': rand_question,
        })
    except Exception as e:
      abort(422)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,  
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

  return app
