import os
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,True')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS')
    return response


  @app.route('/categories/')
  def categories():
    page  = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE  
    end   = start + QUESTIONS_PER_PAGE
    categories = Category.query.all()
    formatted_categories = [category.type for category in categories]
    return jsonify({"categories": formatted_categories})

  @app.route('/categories/<int:category_id>/questions/')
  def getCategoryById(category_id):
    page  = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE  
    end   = start + QUESTIONS_PER_PAGE
    questions = Question.query.filter_by(category = category_id+1).all();
    formatted_questions = [question.format() for question in questions]
    category = Category.query.filter_by(id = category_id+1).one_or_none()
    print ("category: ", category.type.lower())
    return jsonify({"questions":formatted_questions, 
            "total_questions" : len(formatted_questions),
            "current_category": {category_id : category.type.lower()}})

  @app.route('/questions/', methods=['GET'])
  def questions():
    page  = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE  
    end   = start + QUESTIONS_PER_PAGE
    questions = Question.query.all();
    formatted_questions = [question.format() for question in questions]
    categories = Category.query.all()
    formatted_categories = [category.type.lower() for category in categories]
    print("formatted_categories: ", formatted_categories)
    return jsonify({"questions":formatted_questions[start:end], 
            "total_questions" : len(formatted_questions),
            "categories" : formatted_categories,
            "current_category": "1"})

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def deleteQuestion(question_id):
    question = Question.query.filter_by(id = question_id).one_or_none();
    question.delete();
    return jsonify ( { "success" : "true" })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def addQuestion():
    question = Question(question=request.json['question'],answer=request.json['answer'] \
      , difficulty=request.json['difficulty'], category=request.json['category'])
    question.category = int(question.category) + 1
    question.insert();
    print('Record added successfully')
    return jsonify ( { "success" : "true" })

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods=['POST'])
  def searchQuestion():
    searchTerm = request.json['searchTerm']
    if searchTerm != None:
      questions = Question.query.filter(Question.question.ilike('%'+searchTerm+'%')).all()
    formatted_questions = [question.format() for question in questions]
    return jsonify ({"questions" : formatted_questions,
                      "total_questions" : len(formatted_questions)})

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


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
  def quizzes():
    print("request.json: ", request.json)
    previous_questions = request.json['previous_questions']
    print('previous_questions: ', previous_questions)
    quiz_category = request.json['quiz_category']
    print('quiz_category: ', quiz_category)
    category_name = quiz_category['type']
    print('category_name', category_name)
    question_id   = quiz_category['id']
    print('question_id', question_id)

    if category_name == 'click':
      catId = random.randrange(1, 7)
      category = Category.query.filter_by(id = catId).one_or_none()
    else :
      category = Category.query.filter_by(type = category_name).one_or_none()

    print ('category.id: ', category.id)

    question = Question.query.filter_by(category = category.id).all()

    index = random.randrange(len(question))

    if len(previous_questions) >= len(question):
      return  jsonify({"question" : ""})
    else:
      counter = 0
      blnFlag = False
      if len(previous_questions) != 0:
        while counter < len(question):
          if question[index].id not in previous_questions:
            blnFlag = True
            break
          else:
            newindex   = random.randrange(len(question))
          if (newindex != index):
            index      = newindex
            counter = counter + 1
          print("counter", counter)
      else:
        blnFlag = True
    if blnFlag:
      return jsonify({"question" : question[index].format()})
    else:
      return  jsonify({"question" : ""})

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app