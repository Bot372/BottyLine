from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from os import environ

app = Flask(__name__)
app.config.setdefault('SECRET_KEY', environ.get('SECRET_KEY'))
app.config.setdefault('SQLALCHEMY_DATABASE_URI', environ.get('postgres://rxjnmrsmmgxhse:8573675da132f32d66f555c2c00a2a716b8558fec72939c4620cd523f2a68123@ec2-75-101-138-26.compute-1.amazonaws.com:5432/d5qm8rrqjo34jv'))
#app.config.setdefault('SENTRY_DSN', environ.get('SENTRY_DSN'))
#app.config.setdefault('EXCEPTIONAL_API_KEY', environ.get('EXCEPTIONAL_API_KEY'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


class UserData(db.Model):
    __tablename__ = 'UserData'

    #id = db.Column(db.String(64), primary_key=True)
    line_id = db.Column(db.String(64), primary_key=True)
    #Description = db.Column(db.String(128))

if __name__ == '__main__':
    manager.run()