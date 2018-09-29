import os
from flask import Flask, session
from flask import Flask, render_template, flash,redirect, logging,request,url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from wtforms import Form,  StringField,  TextAreaField, PasswordField,  validators
from passlib.hash import sha256_crypt
from wtforms.validators import InputRequired, Email
from wtforms.widgets import Input


app = Flask(__name__)

# Check for environment variable
if not('postgres://skkajkvtaztnbm:b0d305decbb282d506a9a1fb345cb629da3520a0afb59ec9e2533dce0f281238@ec2-174-129-236-147.compute-1.amazonaws.com:5432/d3buogjcbe9anb'):
    raise RunTimeError("Database is not set!")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine('postgres://skkajkvtaztnbm:b0d305decbb282d506a9a1fb345cb629da3520a0afb59ec9e2533dce0f281238@ec2-174-129-236-147.compute-1.amazonaws.com:5432/d3buogjcbe9anb')
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=['GET','POST'])
def index():
    "project1 TODO!"
    if request.method=='GET':
       return render_template("index.html")
    else:
        if request.form['submit'] == 'load':
            # Get Form Fields
            username = request.form['uname']
            password = request.form['password']


            try:
                    result= db.execute("SELECT * FROM register WHERE username = :username AND password=:password",
                    {"username": username, "password":password}).fetchone()
                    if result is not None:

                       session['logged_in']=True
                       session['username']=username
                       flash('you are logged in', 'success')
                       return render_template("search.html")
                    else:

                       return render_template('error.html', message="enter login detail")

            except Exception as e:
                   raise ValueError('insertion failed', e)

    return render_template('search.html')

@app.route("/book", methods=['GET','POST'])
def book():
    "project1 TODO!"
    return render_template("book.html")


@app.route("/search",methods=['GET', 'POST'])
def search():
    if request.method=='GET':
       return render_template("search.html")
       #search=request.form.get['search']
    else:
        #try:
            res =request.form.get('search')
            #likeString = "'%%"+res+"%%'"
            if res!="":
                #return(res)
                results=db.execute("SELECT * FROM books WHERE (LOWER(isbn) LIKE LOWER(:res)) OR (LOWER(title) LIKE LOWER(:res)) OR (author LIKE LOWER(:res)) LIMIT 10",
                { "res": '%' + res + '%'} ).fetchall()

                #for x in results:
                   #return ','.join(str(x))
                if results is None:
                   return render_template("error.html", message="No such book")
                else:
                   #for x in results:
                     # return ','.join(x)
                   return render_template("search.html",results=results)
            else:
                return ("you didn't enter a search value")

        #except Exception as e:
                #raise ValueError ("could not retrieve from database", e)

                #list_id = int(request.form.get('data-list'))
                #search=request.form['search']
            # else: return ("datalist is null")
        #except ValueError:
             #return render_template("error.html", message="Invalid book number.")
             #check if a value id exist in db
        #store=db.execute("SELECT * FROM books WHERE book_id = :id", {"id":list_id})
        #if store.rowcount == 0:

        #else:
             #return render_template("book.html")
             #insert into save book table to b retrieved when users goes to his my book page
#------------------------------------------


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method=='GET':
        return render_template("login.html")

    elif request.method == 'POST':
        if request.form['submit'] == 'load':
            # Get Form Fields
            username = request.form['uname']
            password = request.form['password']


            try:
                    result= db.execute("SELECT * FROM register WHERE username = :username AND password=:password",
                    {"username": username, "password":password}).fetchone()
                    if result is not None:

                       session['logged_in']=True
                       session['username']=username
                       flash('you are logged in', 'success')
                       return render_template("search.html")
                    else:

                       return render_template('error.html', message="enter login detail")

            except Exception as e:
                   raise ValueError('insertion failed', e)

    return render_template('search.html')

@app.route("/logout")
def logout():
	"""Logout Form"""
	session['logged_in'] = False
	return render_template("index.html")

# Register Form Classdescription={'placeholder':'username'}
class RegisterForm(Form):
    username = StringField('Username',[InputRequired("Please enter your name.")])
    email = StringField('Email', [InputRequired("Please enter your email address."), Email("This field requires a valid email address")])
    password = PasswordField('Password', [
        validators.InputRequired("enter password"),
        #validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password', [
        validators.InputRequired("enter password")])

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
          password = sha256_crypt.encrypt(str(form.password.data))
          confirm=form.confirm.data
          #return(password)
          try:
     #execute query with placeholder :
             db.execute("INSERT INTO register(username, email, password) VALUES (:username, :email, :password)",
             {"username": username, "email": email,"password":password})
             db.commit()
             return ("data inserted")
             flash('You are now registered and can log in', 'success')
             return redirect(url_for('index'))
          except Exception as e:
            raise ValueError("couldn't insert into database", e)
      else:
            return ("data was no inserted")
    return render_template('signup.html',form=form)
    #return ("insert data")




    if __name__ == '__main__':
        app.run(host='0.0.0.0')
