from flask import Flask,render_template,flash, redirect,url_for,session,logging,request,make_response,jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import jwt
from functools import wraps
app = Flask(__name__)
app.config['SECRET_KEY'] = 'password234#'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users1.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
admin=Admin(app)

class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))
    phonenumber = db.Column(db.Integer)

admin.add_view(ModelView(user,db.session))

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message':'Token missing'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            session.pop("login",None)
            return jsonify({"message": 'Session expired!,Please log-in again'}),403    

       
        return func(*args,**kwargs)   
    return decorated    




@app.route("/auth")
@token_required
def auth():
    return render_template("logout.html")

@app.route("/logout")
def logout():
    session.pop("login",None)
    return redirect(url_for("login"))

@app.route("/")
def home():
    if "login" in session:
        return redirect(url_for("gettoken",name=session["token"]))

    return render_template("index.html")  

@app.route("/<name>")
def gettoken(name):
    return render_template("gettoken.html",content=name)


@app.route("/register",methods=["GET", "POST"])
def register():
    if request.method=="POST":
       fname=request.form['fname'] 
       lname=request.form['lname']
       passw=request.form['passw']
       email=request.form['mail']
       phonenumber=request.form['numb']
       register = user(firstname=fname, lastname=lname, email = email, password=passw, phonenumber=phonenumber,)
       db.session.add(register)
       db.session.commit()
       return redirect(url_for("login"))
    return render_template("register.html")     



@app.route("/login",methods=["GET", "POST"])
def login():
    if "login" in session:
        return redirect(url_for("gettoken",name=session["token"]))

    if request.method == "POST":
        kmail=request.form["email"]
        kpassw=request.form["passw"]
        login = user.query.filter_by(email=kmail, password=kpassw).first()
        if login is not None:
            session['login']='true'
            token = jwt.encode({'user':kmail, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300)}, app.config['SECRET_KEY'])
            
            session["token"]=token
            return redirect(url_for("gettoken",name=token))
            return jsonify ({'token':token.decode('utf-8')})
            
            
            

        else:
            return redirect(url_for("register"))    

    return render_template("login.html")

if __name__== "__main__":
    db.create_all()
    app.run(debug=True)
