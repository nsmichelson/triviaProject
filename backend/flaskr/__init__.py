import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

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

  #GET request to retrieve all the trivia questions (for main page)
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


  @app.route('/api/categories/<int:category_id>/questions',methods=['GET'])
  def qforcategory(category_id):
    print("This is the category id we are looking at",category_id)
    selection = Question.query.filter(Question.category==category_id)
    #selection = Question.query.filter(Category.id==category_id)
    #Why did above not work??> The artist and show one did, but is that because they are linked by a foregn key?
    #above query is not actually effectively querrying for category id... why?
    #print(Artist.query.filter(Artist.id==artistID, Shows.id==1)[0].name)

    for thing in selection:
      print(thing)
    print("This is the selection",selection[0].question)
    print("This is the selection",selection[1].question)
    current_questions = paginate_questions(request,selection)
    for question in current_questions:
      print(question)

    return jsonify({
      "success":True,
      "questions":current_questions

    })

 

  #STILL NEED TO FIX THIS ONE BELOW!!!!!!!!!
  @app.route('/api/questions', methods=["POST"])
  def addQuestion():
    searchTerm = request.get_json().get('searchTerm')
    print("Search term is",searchTerm)
    #initially had request fed into the function above, testing what happens if take it out
    if searchTerm:
      searchterm = request.get_json().get('searchTerm')
      selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(searchterm)))
        #selection = Book.query.order_by(Book.id).filter(or_(Book.title.ilike('%{}%'.format(search)), Book.author.ilike('%{}%'.format(search))))
      current_questions = paginate_questions(request, selection)
      
      return jsonify({
        'success': True,
        'questions': current_questions
        })

    else:
      print("there was no search term")
      body = request.get_json()
      print("This is the body of the request",body)
      new_question = body.get('question',None)
      new_answer = body.get('answer',None)
      new_difficulty = int(body.get('difficulty',None))
      new_category = int(body.get('category',None))
      print("This is what we are getting for category",new_category)
      
      #need to take the category received and convert it to the integrer that goes in the database
      #categoryy = Category.query.filter(Category.type==new_category).first()
      #print(categoryy)

      #categoryID = categoryy.id 

      #print("The ID of the category for the added question is",categoryID)
      #need to fix the above... as it turns out the category does need to be stored in the database as a string

      #need to convert the category to a number first?

     

      try:
        newQuestion = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
        print("Here is the new question",newQuestion)
        questionn = Question.query.filter(Question.id == 4).one_or_none()
        print("here is a question that the functions worked on",questionn)
        print(questionn.format())
        print(newQuestion.id)
        print(type(newQuestion.question))
        print(type(newQuestion.answer))
        print(type(newQuestion.category))
        print(type(newQuestion.difficulty))
        print("Testing if formating works",newQuestion.format())
        print("about to do the insert")
        #The 422 error is coming from the below... need to look up the insert in sqlalchemy and see what's going on
        try:
          newQuestion.insert()
          print("just did the insert function")
          return jsonify({
            "success":True,
            "created":newQuestion.id
            })
        except:
          print("Unexpected error:", sys.exc_info()[0])
          raise
          
      except:
        print("something went wrong")
        abort(422)
  
  
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

    