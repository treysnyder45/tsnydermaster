import os
from flask_migrate import Migrate
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

database_name = "fyyur"
database_name = "trivia_test"
database_path = "postgresql://postgres:postgres@{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()
#migrate = Migrate(app,db)
engine = create_engine(database_path)
Session = sessionmaker(engine)
session = Session()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    engine = create_engine(database_path)
    Session = sessionmaker(engine)
    session = Session()

    db.app = app
    db.init_app(app)
    db.create_all()

'''
Question

'''
class Question(db.Model):  
  __tablename__ = 'questions'

  id = Column(Integer, primary_key=True)
  question = Column(String)
  answer = Column(String)
  difficulty = Column(Integer)
  category_id = Column(Integer, db.ForeignKey('categories.id'))

  def __init__(self, question, answer, category_id, difficulty):
    self.question = question
    self.answer = answer
    self.category_id = category_id
    self.difficulty = difficulty

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'question': self.question,
      'answer': self.answer,
      'category': self.category_id,
      'difficulty': self.difficulty
    }

'''
Category

'''
class Category(db.Model):  
  __tablename__ = 'categories'

  id = Column(Integer, primary_key=True)
  type = Column(String)
  questions = db.relationship('Question', backref='categories', lazy='dynamic')

  def __init__(self, type):
    self.type = type

  def format(self):
    return {
      'id': self.id,
      'type': self.type
    }