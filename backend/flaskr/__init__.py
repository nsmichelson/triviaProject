import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = []

  for question in selection:
    formattedQ = Question.format(question)
    questions.append(formattedQ)


  print("Here are all the questions",questions) 


  #questions = [Question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r"/api/*": {"origins": "*"}})
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    #wondering if I need to add something here to allow the "include" for adding questions... will look into that
    #and yep adding the last one above seemed to allow the question form to get submitted to server.. but whhhhy?
    return response
  
  #GET request to get a list of all the category names and their ids
  @app.route('/api/categories',methods=["GET"])
  def getCategories():
    categories = Category.query.order_by(Category.id).all()
    print("categories are:",categories)

    CategoriesFormatted = []
    
    for category in categories:
      cleanCategory = Category.format(category)
      CategoriesFormatted.append(cleanCategory)
      print(category.type)

    if categories is None:
      abort(404)

    return jsonify({
      "Success":True,
      "Total_Categories":len(Category.query.all()),
      "categories":CategoriesFormatted
    })


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

  @app.route('/api/questions')
  def getQuestions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request,selection)

    if len(current_questions)==0:
      abort(404)

    categoryList = []

    for question in current_questions:
      if question['category'] not in categoryList:
        categoryList.append(question['category'])

    categories = Category.query.all()
      
    categoriesReturn = {category.id : category.type for category in categories} 
    print("TEST")
    print(categoriesReturn)
    return jsonify({
      "success":True,
      "questions": current_questions,
      "totalQuestions": len(Question.query.all()),
      "categories":categoriesReturn,
      "current_category": list(set([question['category'] for question in current_questions]))
    })
  

  #route to delete a specific question  
  @app.route('/api/questions/<int:question_id>', methods=["DELETE"])
  def deleteQuestion(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      print("This is the question to delete")
      
      if question is None:
        abort(404)
        
      question.delete()
      print("question was deleted")

      selection = Question.query.order_by(Question.id).all()
      print("This is the selection",selection)

      current_questions = paginate_questions(request,selection)

      #Question.close()   --- does this need to be here?

      return jsonify({
        "success":True,
        "questions":current_questions
        })
    except:
      abort(422)
  

  @app.route('/api/questions', methods=["POST"])
  def addQuestion():
    #initially had request fed into the function above, testing what happens if take it out

    body = request.get_json()

    new_question = body.get('question',None)
    new_answer = body.get('answer',None)
    new_difficulty = body.get('difficulty',None)
    new_category = body.get('category',None)

    #need to convert the category to a number first?

    print("This is the body of the request",body)

    try:
      newQuestion = Question(question=new_question,answer=new_answer,category=new_category,difficulty=new_difficulty)
      print("Here is the new question",newQuestion)
      newQuestion.insert()

      return jsonify({
        "success":True,
        })
        
    except:
      abort(422)

    
  
  
  return app

    