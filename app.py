from flask import Flask, render_template,request,flash, url_for, redirect,session
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import re


#########################################################

basedir = os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SECRET_KEY'] = "SECRETKEY"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)

Migrate(app,db)

#################   database    #######################
class Maintenance(db.Model):

    __tablename__ ='FaultDetails'

    id=db.Column('fault_number',db.Integer,primary_key=True)
    build_name=db.Column(db.Text)
    build_room=db.Column(db.Text)
    build_fault=db.Column(db.Text)
    comments=db.Column(db.Text)
    date_logged=db.Column(db.Date)
    student_num=db.Column(db.Text)
    prgress=db.Column(db.Text)
    date_completed=db.Column(db.Date)
    feedback=db.Column(db.String(250))


    def __init__(self,build_name,build_room,build_fault,comments,date_logged,studentid):
        self.build_name=build_name
        self.build_room=build_room
        self.build_fault=build_fault
        self.comments=comments
        self.date_logged=date_logged
        self.student_num=studentid
        
        

    def __repr__(self):
        return f"""
        Campus Name:{self.build_name} 
        Room: {self.build_room} 
        Fault: {self.build_fault}
        
        Comments made by student: {self.comments}.
        Date fault logged: {self.date_logged}

        --Progress--
        This fault progress is: {self.prgress}
        Date completed: {self.date_completed}.

        Feedback from Maintenance team: {self.feedback} 
        """
    

class Student(db.Model):

    __tablename__ ='StudentRecords'

    stud_id=db.Column('Student_num',db.Text,primary_key=True)
    pssword=db.Column(db.Text)

    def __init__(self,stud_id,pssword):
        self.stud_id=stud_id
        self.pssword=pssword
   

    def __repr__(self):
        return f"Student number:    {self.stud_id}     has already been register!. "



#------------------ signup page ---------------------------------
@app.route('/',methods=['GET','POST']) #127.0.0.1:5000
def index():
    if request.method=='POST':
        stud1=request.form['username1']
        pssword1=request.form['password1']


        stud1_exists=db.session.query(Student).filter_by(stud_id=stud1).first()
        session['username']=stud1

        if stud1=='Epadmin' and pssword1=='adminEp':
            return render_template('basic.html')

        if not stud1_exists:
            flash('Your details are not on our database! Please register on below link.','error')
            return redirect('/')

        pssword1_exists=stud1_exists.pssword

        p_Valid=(pssword1_exists==pssword1)

        if  not p_Valid:
            flash('Please enter in your information correctly. If you need your details added - please click on the relevant link.','error')
            return redirect('/')
        else:
            global stud
            stud=stud1
            return render_template('basic_user.html')
    return render_template('signup.html')


#-------------------------- register page ------------------------------------------

@app.route('/register', methods=['GET','POST'])
def register():
    
    if request.method=='POST':
        stud2=request.form['Stud_id']
        if stud2.isnumeric()==False:
            message="Please enter in numbers only for your student number"
            flash(message)
        stud2_exists=db.session.query(Student).filter_by(stud_id=stud2).first()

        if not request.form['Stud_id'] or not request.form['Pssword']:
            flash('Please enter all the fields!','error')
        elif stud2_exists:
            stud2_exists.pssword=request.form['Pssword']
            db.session.commit()
            return redirect('/')

        else:
            stud=Student(request.form['Stud_id'],request.form['Pssword'])
            db.session.add(stud)
            db.session.commit()
            flash("Record was added successfully!",'error')
            return redirect('/')

    return render_template('register.html')

#------------------------------ welcome page (admin)-------------------------------------------------------

@app.route('/welcome')
def welcome():
    return render_template('basic.html')


#---------------------------------welcome page (user)-----------------------------------------------
@app.route('/welcome_user')
def welcome_user():
    return render_template('basic_user.html')


#------------------------------ logout page -------------------------------------------------------

@app.route('/logout')
def logout():
    return render_template('logged_out.html')

#------------------------------ fault page -------------------------------------------------------

@app.route('/logFault',methods=['GET','POST'])
def logFault():
    if request.method=='POST':  ##the get in buildname and fault-- check if works!  also try request.args.get(nameofselect
        build_name1=request.form.get('campus_name')
        room_num1=request.form['room_num']
        if room_num1.isalnum()==False:
            message="Please enter in numbers and letters only for room number"
            flash(message)
        fault1=request.form.get('fault_desc')
        comment1=request.form['comment_box']
        date_logged1=datetime.now()

        if not build_name1 or not room_num1 or not fault1 or not comment1:
            flash('Please enter all the fields!','error')
        else:
            maint1=Maintenance(build_name1,room_num1,fault1,comment1,date_logged1,stud)
            db.session.add(maint1)
            db.session.commit()
            ref=Maintenance.query.all()
            ref=ref[-1].id

            message1 = f"Fault created successfuly!  Your fault ref is: {ref}"
            flash(message1+" Thank You.")
            return redirect(url_for('usercomments'))

    return render_template('fault.html')

#------------------------------ user -> view comment page -----------------------------------------
@app.route('/usercomments')
def usercomments():
    rec_exists=Maintenance.query.all()
    rec_exists=rec_exists[-1]
    return render_template('usercomments.html',value=rec_exists)

#------------------------------ view feedback page - user only ------------------------------------------------
@app.route('/feedback',methods=['GET','POST'])
def feedback():
    
    if request.method == "POST":
        searchStud=request.form['searchstud_num']
        if searchStud.isnumeric()==False:
            message="Please enter in numbers only for your student number"
            flash(message)
        if searchStud==stud:
            maint1=Maintenance.query.filter(Maintenance.student_num==searchStud).order_by(Maintenance.student_num).all()
        else:
            flash("Please enter in your student number correctly!")
            return redirect(url_for('feedback'))

        if maint1==None:
            flash("You have no faults submitted!")
            return redirect(url_for('feedback'))
        else:
            return render_template('feedback.html',query=maint1) 
    
    return render_template('feedback.html')
#-----------------------------write feedback - admin only----------------------------------------------------------------------
@app.route('/write_feedback',methods=['GET','POST'])
def write_feedback():
    if request.method=="POST":
        ref1=request.form['ref_num']
        if ref1.isnumeric()==False:
            message="Please enter in numbers only for ref number"
            flash(message)
        prgress1=request.form.get('prgress_fault')
        feedbck1=request.form['feedback_maint']

        fault_exists=db.session.query(Maintenance).filter_by(id=ref1).first()
        if not ref1 or not prgress1 or not feedbck1:
            flash('Please enter all the fields!','error')
        elif not fault_exists:
            flash('Please enter in the correct ref!','error')
        else:
            fault_exists.prgress=prgress1
            fault_exists.date_completed=datetime.now()
            fault_exists.feedback=feedbck1
            db.session.commit()
            flash('Record is edited successfully! Thank You.')
            return redirect(url_for('welcome'))


    return render_template('write_feedback.html')

#------------------------------ view DB page ------------------------------------------------------
@app.route('/viewdb',methods=['GET','POST'])
def viewdb():
    if request.method=="POST":
        records1=Maintenance.query.all()
        if 'username' in session:  
            admin = session['username']

        return render_template('viewdb.html',maint1=records1,user=admin)
    
    return render_template('viewdb.html')

#------------------------------help page-----------------------------------------------------------
@app.route('/help',methods=['GET','POST'])
def help():
    if request.method=="POST":
        return redirect(url_for('index'))

    return render_template('help.html')


#------------------------------ main method -------------------------------------------------------

if __name__=='__main__':
    with app.app_context():
        db.create_all()

    app.run()

