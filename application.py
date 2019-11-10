import os
from flask import Flask, session,redirect, url_for,flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, flash,redirect, logging,request,url_for, abort,jsonify
from flask_paginate import Pagination, get_page_args
from wtforms import Form,  StringField,  TextAreaField, PasswordField,SubmitField, validators
from passlib.hash import sha256_crypt
from wtforms.validators import DataRequired,InputRequired, Email,length
from wtforms.widgets import Input
from decorator import *



app = Flask(__name__)

# Check for environment variable
if not('postgres://skkajkvtaztnbm:b0d305decbb282d506a9a1fb345cb629da3520a0afb59ec9e2533dce0f281238@ec2-174-129-236-147.compute-1.amazonaws.com:5432/d3buogjcbe9anb'):
    raise RunTimeError("Database is not set!")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine('postgres://skkajkvtaztnbm:b0d305decbb282d506a9a1fb345cb629da3520a0afb59ec9e2533dce0f281238@ec2-174-129-236-147.compute-1.amazonaws.com:5432/d3buogjcbe9anb', pool_size=20, max_overflow=0)
db = scoped_session(sessionmaker(bind=engine))

dbSession=db()

#Registration for connecting with form template
class RegisterForm(Form):
    username = StringField('Username',[InputRequired(message="Please enter your name.")])
    email = StringField('Email', [InputRequired(message="Please enter your email address."), Email(message="This field requires a valid email address")])
    password = PasswordField('Password', [
        validators.InputRequired("enter password")
        #validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password', [
        validators.InputRequired("enter password")])


'''g is an object provided by Flask. It is a global namespace for holding any
data you want during a single app context.
from flask import g An app context lasts for one request / response cycle,
g is not appropriate for storing data across requests. Use a database, redis,
the session, or another external data source for persisting data.
'''

#Login form

class LoginForm(Form):
        username = StringField('Username',[InputRequired(message="Please enter your name.")])
        password = PasswordField('Password', validators=[DataRequired(message="enter password")])
        submit = SubmitField('login')


@app.route("/", methods=['GET','POST'])
def index():
    "project1 TODO!"
    if request.method=='GET':
       return render_template("index.html")

#@app.route("/book", methods=['GET','POST'])
#def book():
    #"project1 TODO!"
    #return render_template("book.html")


@app.route("/search",methods=['GET', 'POST'])
@login_required
def search():
    username=session.get('username')
    if session.get("books") is None:
        session["books"]=[]
    if request.method=='GET':
       return render_template("searchList.html")
       #search=request.form.get['search']
    if request.method=="POST":
        try:
        #in ajax search form the value the string used to store search is res=reguest..
            value =request.form.get('search')
            #likeString = "'%%"+res+"%%'"
            if value!="":

                result=dbSession.execute("SELECT * FROM books WHERE (LOWER(isbn) LIKE LOWER(:value)) OR (LOWER(title) LIKE LOWER(:value)) OR (LOWER(author) LIKE LOWER(:value))",
                { "value": '%' + value + '%'} ).fetchall()

                #result=dbSession.execute("SELECT * FROM books WHERE author iLIKE '%"+value+"%' OR title iLIKE '%"+value+"%' OR isbn iLIKE '%"+value+"%'").fetchall()
                if result:
                   for x in result:
                        session['books'].append(x)
                   return render_template("searchList.html",result=session['books'],username=username)
                flash("Sorry no book found!")
                return redirect(url_for('search'))
        except Exception as e:
           raise ValueError("couldn't select from book table", e)




#------------------------------------------

@app.route("/save", methods=[ 'GET','POST'])
def save():

       qry=request.form['search']
       #return(qry)
       if qry!="":
           try:
               result=dbSession.execute("SELECT isbn,title,author,year FROM books WHERE title = :title",
               {"title": qry}).fetchone()
               isbns= result['isbn']
               titles=result['title']
               authors=result['author']
               years=result['year']
               user_id=session.get('logged_in')
               #return (isbns)
               results=dbSession.execute("INSERT INTO save(isbn, title, author, year,reg_id)  VALUES (:isbn, :title, :author, :year, :reg_id)",
               {"isbn": isbns, "title": titles,"author":authors, "year": years, "reg_id":4})
               dbSession.commit()
               dbSession.close()
               #return redirect(url_for('book'))
               return render_template("book.html")


           except Exception as e:
                  raise ValueError('insertion failed', e)

       else:
           return ("No title selected")

@app.route("/detail/<string:isbn>", methods=[ 'GET','POST'])
def detail(isbn):
     username = session.get('username')
     if session.get("rating") is None:
        session["rating"]=[]
    # if request.method == 'GET':
        #try:
     #voted=dbSession.execute("SELECT * FROM rating WHERE username=:username AND isbn=:isbn",
     #{"username": username, "isbn":isbn}).fetchone()
     if request.method=="POST": #and voted is None:
         comment=request.form.get('comment')
         rate=request.form.get('rate')
         reviews=int(rate)
         voted=dbSession.execute("SELECT * FROM rating WHERE username=:username AND isbn=:isbn",
         {"username": username, "isbn":isbn}).fetchone()
         if voted is None:

              dbSession.execute("INSERT INTO rating(isbn, review,username, comment) VALUES(:isbn,:review,:username,:comment)",
              {"isbn":isbn,"review":reviews,"username":username,"comment":comment})
              dbSession.commit()
              dbSession.close()

     flash(" you've already added a review on this book")
     return redirect(url_for('detail'))
     result=dbSession.execute("SELECT * FROM rating WHERE isbn=:isbn",
     {"isbn":isbn}).fetchall()
     for x in result:
        session['rating'].append(x)
     results=dbSession.execute("SELECT * FROM books WHERE isbn=:isbn",
     {"isbn":isbn}).fetchone()
     return results.isbn
     res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": " ULZdeovSM8YTeNjzAtPoUA", "isbns": isbn})
     average_rating=res.json()['books'][0]['average_rating']
     work_ratings_count=res.json()['books'][0]['work_ratings_count']
     return render_template("detail.html", username=username,voted=voted,result=session['rating'],results=results,average_rating=average_rating,work_ratings_count=work_ratings_count)
        #except Exception as e:
           #raise ValueError("couldn't select from rating table", e)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form=LoginForm(request.form)

    if request.method=='GET':
        return render_template("login.html", form=form)

    elif request.method == 'POST':
        if form.validate():
            # Get Form Fields
             username = form.username.data
             password = form.password.data
             #return username +' '+ password
             try:
                 new_user=dbSession.execute("SELECT username,password From register WHERE username = :username",
                 { "username": username, "password":password }).fetchone()

                 if new_user:
                      if new_user.password==form.password.data:
                          session["username"]=new_user.username
                          return redirect(url_for('search'))
                 flash("invalid email or password")
                 return redirect(url_for('login'))
             except Exception as e:
                raise ValueError("couldn't select from register table", e)


@app.route("/logout")
def logout():
	"""Logout Form"""
	session.clear()
	return render_template("index.html")

# Registration
@app.route("/signup", methods=['GET' ,'POST'])
def signup():
    form = RegisterForm(request.form)
    if request.method == 'POST':
      if form.validate():
          #username=request.form['user']
          #email=request.form['email']
          #password=sha256_crypt.encrypt(str(request.form['pass']))

          username = form.username.data
          email = form.email.data
          passw=form.password.data
         # password = sha256_crypt.encrypt(str(form.password.data))
          confirm=form.confirm.data
          #return(password)
          if passw!=confirm:
              flash("password didn't match")
              return redirect(url_for('signup'))

          try:
               password = sha256_crypt.encrypt(str(form.password.data))
               new_user=dbSession.execute("SELECT username From register WHERE username = :username",
               { "username": username }).fetchone()

               if new_user:
                    flash("username already exist try another username")
                    return redirect(url_for('signup'))


               dbSession.execute("INSERT INTO register(username, email, password) VALUES (:username, :email, :password)",
               {"username": username, "email":email,"password":password})
               dbSession.commit()
               dbSession.close()
               flash(u'You are now registered and can log in with your details', 'success')
               return redirect(url_for('login'))

          except Exception as e:
            raise ValueError("couldn't insert into database", e)
      else:
            return ("data was no inserted")
    return render_template('signup.html',form=form)
    #return ("insert data")




    if __name__ == '__main__':
        app.run(host='0.0.0.0')
