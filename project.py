from flask import Flask, make_response, render_template,request,redirect,session
import mysql.connector
from flask_mail import *
import random
import os
from library import *
from flask_recaptcha import ReCaptcha
from datetime import timedelta

conn = mysql.connector.connect(host='localhost',user='root',password='hemant',database='hemant')
cursor = conn.cursor()

app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'  
app.config['MAIL_PORT']=465 
app.config['MAIL_USERNAME'] = 'flask604@gmail.com'  
app.config['MAIL_PASSWORD'] = 'qxfnriusnowundih'  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True 

mail = Mail(app)  
app.secret_key = os.urandom(24)

@app.route('/')
def login():
    return render_template('prlogin.html')

@app.route('/register')
def about():
    return render_template('prregister.html')

@app.route('/home')
def home():
    
    if 'user_id' in session:
        return render_template('prhome.html')
    else:
        return redirect('/')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email=request.form.get('email')
    password=request.form.get('password')
    cursor.execute("""SELECT  * FROM  `project` WHERE `email` LIKE '{}' AND `password` LIKE '{}'"""
                   .format(email,password))
    users = cursor.fetchall()
    if(len(users)>0):
        session['user_id'] = users[0][0]
        if('rem' in request.form and request.form['rem']==1):
            resp = make_response(render_template("/prhome.html"))
            resp.set_cookie('email',email)
            resp.set_cookie('password',password) 
            return resp 
        else:
            return redirect('/home')
    else:
        return render_template('/prlogin.html',message="Incorrect email or password!")

@app.route('/add_user',methods=['POST'])
def add_user():
    name = request.form.get('uname')
    email = request.form.get('uemail')
    password = request.form.get('upassword')
    cursor.execute("""SELECT * FROM `project` WHERE `email` = '{}'""".format(email))
    data=cursor.fetchall()
    if(cursor.rowcount==0):
        cursor.execute("""INSERT INTO `project`(`user_id`,`name`,`email`,`password`) 
                   VALUES (NULL,'{}','{}','{}')""".format(name,email,password))
        conn.commit()

        cursor.execute("""SELECT * FROM `project` WHERE `email` LIKE '{}'""".format(email))
        myuser = cursor.fetchall()
        session['user_id'] = myuser[0][0]
        return redirect("/")
    else:
        mess="Email already exist"
        return render_template('prregister.html',mes2=mess)


@app.route('/prforgetpass', methods=["POST","GET"])
def forgetpass():
        if(request.method == 'POST'):
            umail=request.form['email']
            session['mail']=umail
            msg = Message('OTP Verification', sender = 'flask604@gmail.com', recipients=[umail])
            session['OTP']= otp = random.randint(1111,9999)
            msg.body= "Hi!\nWe have received your request for a one-time-password, please do not share it with anyone : " + str(otp) + "\nThe OTP is only valid for 10 minutes\nHave a great day!\nTeam Techfly." 
            mail.send(msg)
            return render_template('protp.html')
        else:
            return render_template("prforgetpass.html", mes="mail does not exist")

@app.route('/validate', methods=["POST"])
def validate():
    user_otp = request.form['otp']
    if session["OTP"] == int(user_otp):
        return render_template('prconfirmpass.html')
    else:
        return render_template('protp.html',mes="Incorrect OTP!" )
    
@app.route('/newpass',methods=['POST','GET'])
def new_pass():
    
    npass = request.form['npass']
    cpass = request.form['cpass']
    if(npass != cpass):
        return render_template('prconfirmpass.html',mes3='Passwords do not match!')
    else:
        password = npass
        cursor.execute("UPDATE project SET `password` = '{}' WHERE `email` = '{}'".format(password,session['mail']))
        conn.commit()
        return render_template('prlogin.html')
  
@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')


if __name__=="__main__":
    app.run(debug=True)
      