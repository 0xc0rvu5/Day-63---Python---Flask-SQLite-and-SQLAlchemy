import os
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField, IntegerField, SelectField, validators
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy


#initialize global variables
SECRET_KEY = os.urandom(32)
APP = Flask(__name__, template_folder='templates', static_folder='static')
APP.config['SECRET_KEY'] = SECRET_KEY
APP.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#initiate bootstrap functionality
Bootstrap(APP)


#initiate sqlalchemy database functionality
db = SQLAlchemy(APP)


with APP.app_context():
    class Book(db.Model):
        '''Generate a book database.'''
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        title = db.Column(db.String(250), unique=True, nullable=False)
        author = db.Column(db.String(250), nullable=False)
        rating = db.Column(db.Integer, nullable=False)

        # Optional: this will allow each book object to be identified by its title when printed.
        def __repr__(self):
            return f'<Book {self.title}>'
    
    # # create database
    # db.create_all()

    # # create column
    # new_book = Book(title="Harry Potter 8", author="J. K. Rowling", rating=9)
    # db.session.add(new_book)
    # db.session.commit()


class BookForm(FlaskForm):
    '''Generate a book form.'''
    title = StringField('Book Name', validators=[DataRequired()])
    author = StringField('Book Author', validators=[DataRequired()])
    rating = IntegerField('Rating', validators=[DataRequired(), validators.NumberRange(min=0, max=10)])
    submit = SubmitField('Add Book')


@APP.route('/')
def home():
    return render_template('index.html', all_books=Book.query.all())


@APP.route("/add", methods=['GET', 'POST'])
def add():
    form = BookForm()
    if form.validate_on_submit():
        new_book = Book(
            title=request.form['title'], 
            author=request.form['author'], 
            rating=request.form['rating'])
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('add'))
        
    return render_template('add.html', form=form)


@APP.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == "POST":
        #edit by id
        book_id = request.form["id"]
        book_to_update = Book.query.get(book_id)
        book_to_update.rating = request.form["rating"]
        db.session.commit()
        return redirect(url_for('home'))

    book_id = request.args.get('id')
    book_selected = Book.query.get(book_id)
    return render_template("edit.html", book=book_selected)


@APP.route('/delete', methods=['GET', 'POST'])
def delete():
    book_id = request.args.get('id')
    #delete record by id
    book_to_delete = Book.query.get(book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    APP.run(debug=True)