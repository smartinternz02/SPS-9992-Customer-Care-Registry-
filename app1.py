from flask import Flask , render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from sendmail import sendmail
import smtplib

app = Flask(__name__)
app.secret_key = 'a'

app.config['MYSQL_HOST'] = "remotemysql.com"
app.config['MYSQL_USER'] = "d52gKQBsVf"
app.config['MYSQL_PASSWORD'] = "qWF9xFqp7T"
app.config['MYSQL_DB'] = "d52gKQBsVf"

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template("home1.html")


@app.route('/signup',methods =["POST","GET"])
def signup():
    msg=''
    if request.method =="POST":
        name = request.form["name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        password = request.form["password"]
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM signup WHERE name = % s', (name, ))
        cursor.execute('SELECT * FROM signup WHERE mobile = % s', (mobile, ))
        account = cursor.fetchone()
        print(account)
        if account:
            msg = 'Account already exists.!!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address '
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'name must contain only characters and numbers !'
        else:
            cursor.execute('INSERT INTO signup VALUES(NULL,%s,%s,%s,%s)',(name,email,mobile,password))
            mysql.connection.commit()
            msg="Successfully registered.!!"
            TEXT = "Hello  "+name + ",\n\n"+ """you have successfully registered to our customer care """ 
            sendmail(TEXT,email)
    return render_template("signup.html",msg = msg)



@app.route('/userlogin',methods =["POST","GET"])
def userlogin():
    global userid
    msg = ''
    if request.method == 'POST' :
        name = request.form['name']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM signup WHERE name = % s AND password = % s', (name, password ),)
        account = cursor.fetchone()
        print (account)
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            userid=  account[0]
            session['name'] = account[1]
            return render_template('ComplainRegistration.html')
        else:
            msg = 'Incorrect username / password !'
    return render_template('user_login.html', msg = msg)
    

@app.route('/ComplainRegistration',methods =["POST","GET"])
def complainregistry():
    msg=''
    if request.method =="POST":
        name = request.form["name"]
        email = request.form["email"]
        mobile = request.form["mobileno"]
        complain_description = request.form["complaindescription"]
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM signup WHERE name = % s', (name,))
        account = cursor.fetchone()
        if not account:
            msg = 'Invalid username'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address '
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'name must contain only characters and numbers !'
        else:
          cursor.execute('INSERT INTO complain_registry VALUES(NULL,%s,%s,%s,%s)',(name,email,mobile,complain_description))
          mysql.connection.commit()
          msg="Complain Successfully Registerd"
          
          cursor = mysql.connection.cursor()
          cursor.execute('SELECT complainId FROM complain_registry WHERE name= %s AND complaindescription= %s', (name,complain_description,))
          session['complainId'] = cursor.fetchone()
          TEXT = "hello" + name + ",\n\n"+ """your complain has been successfully registered and will be processed soon """+"\n\n"+ "your complainId:"+ str(session['complainId']) + "\n"+ """You can Use the above complainId to track your request\n """
          sendmail(TEXT,email)
    return render_template("ComplainRegistration.html",msg = msg)


@app.route('/adminlogin',methods =["POST","GET"])
def adminlogin():
    msg = ''
    if request.method == 'POST' :
        adminname = request.form['adminname']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM adminlogin WHERE adminname = % s AND password = % s', (adminname, password ),)
        account = cursor.fetchone()
       
        if not account:
            msg = 'Incorrect username / password !' 
        else:
            session['loggedin'] = True
            session['id'] = account[0]
            userid=  account[0]
            session['name'] = account[1]
            return dashboard()
    return render_template('admin_login.html', msg = msg)
        


@app.route('/dashboard',methods =["POST","GET"])
def dashboard():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM complain_registry')
    account = cursor.fetchall() 
    return render_template('daashboard.html',account=account )



@app.route('/delete/<string:complainId>', methods = ['GET'])
def delete(complainId):
    flash("Record Has Been Deleted Successfully")
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM complain_registry WHERE complainId=%s", (complainId,))
    mysql.connection.commit()
    return redirect(url_for('dashboard'))


@app.route('/admin',methods =["POST","GET"])
def admin():
    msg=''
    if request.method =="POST":
        customername = request.form["customername"]
        complainId = request.form["complainId"]
        email = request.form["email"]
        complain = request.form["complain"]
        agent = request.form["agent"]
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO assignedagent VALUES (NULL,%s,%s,%s,%s,%s)', (customername,complainId,email,complain,agent,))
        mysql.connection.commit()
        msg='Agent assigned'
        TEXT = "Dear"+ customername + ",\n\n"+ ", \n\nyour complainId:"+ complainId + ",\n"+ """Use the above complainId to track your request\n """
        sendmail(TEXT,email)
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT agent FROM agentdb WHERE agent = %s', (agent,))
        session['agentname'] = cursor.fetchone()
        cursor.execute('SELECT contact FROM agentdb WHERE agent = %s', (agent,))
        session['contact']= cursor.fetchone()
        TEXT= "Dear customer,\nwe have assigned an agent to manage and solve your complain.\nAgent details:\nAgent Name:"+ str(session['agentname']) +"\ncontact:"+ str(session['contact']) +"""\ncontact the agent for further queries"""
        sendmail(TEXT,email)
    return render_template("admin.html",msg = msg)


@app.route('/progress',methods =["POST","GET"])
def progress():
    msg=''
    if request.method =="POST":
        complainId = request.form["complainId"]
        progress = request.form["progress"]
        session["complainId"] = complainId
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO progress VALUES(%s,%s)',(complainId,progress,))
        mysql.connection.commit()
        msg="progress updated.!"
        cursor = mysql.connection.cursor()
    return render_template("progress.html",msg = msg)

@app.route('/track',methods =["POST","GET"])
def track():
    if request.method =="POST":
     complainId = request.form["complainId"]
     cursor = mysql.connection.cursor()
     cursor.execute('SELECT * FROM progress WHERE complainId = % s', (complainId,))
     account = cursor.fetchall()
     if not account:
         return render_template("track.html",account="you complain is registered and will be proccessed soon ")
     else:
           cursor = mysql.connection.cursor()
           cursor.execute('SELECT * FROM progress WHERE complainId = % s', (complainId,))
           account = cursor.fetchall()
           for progress in account :
            return render_template("track.html",account = progress)
    return render_template("track.html",account = "complainId , progress ")
    

@app.route('/feedback',methods =["POST","GET"])
def feedback():
    msg=''
    if request.method == 'POST':
        agent = request.form['agent']
        ratings = request.form['opt']
        comments = request.form['comments']
        cursor = mysql.connection.cursor()
        if agent == '':
            return render_template('track.html', msg='Please enter required fields')
        else:
             cursor.execute('INSERT INTO feedback VALUES(NULL,%s,%s,%s)',(agent,ratings,comments))
             mysql.connection.commit()
             msg="Thank you for your valuable feedback"
    return render_template("track.html",msg = msg)


@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('home1.html')

    
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug = True,port = 8080)
    
    
    