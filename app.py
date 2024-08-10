from flask import Flask,render_template,request,redirect,url_for,session,make_response,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
from flask_mail import Mail
import pdfkit
import json
import re
import random
from flask import jsonify
from sqlalchemy.exc import IntegrityError
# config = pdfkit.configuration(wkhtmltopdf='C:/Users/nidhi/Downloads/wkhtmltox-0.12.6-1.mxe-cross-win64 (1)/wkhtmltox/bin/wkhtmltopdf.exe')



with open('config.json','r') as c:
    params=json.load(c)["params"]
local_server=True

app=Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],                    
    MAIL_PASSWORD=params['gmail-password']
)
mail=Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI']=params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

app.config['SECRET_KEY'] = 'abcd'
db = SQLAlchemy(app)


class Logininfo(db.Model):
    
    username=db.Column(db.Integer,primary_key=True)
    userid = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)

class Otp(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    otp = db.Column(db.Integer, nullable=True)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        if not userid:
            error="Please enter user ID"
        elif not password:
            error="Please enter password"
        else:
        # Check if user exists
            user = Logininfo.query.filter_by(userid=userid).first()
            if not user:
                error = "You have not registered"
            elif user.password != password:
                error = "Invalid credentials"
            else:
                # Login successful
                session['loggedin'] = True
                session['userid'] = userid
                return redirect(url_for('mainpage'))  # Redirect to mainpage after successful login
           
    return render_template('index.html', error=error)
    



@app.route('/createAccount',methods=['GET','POST'])
def createAccount():
    error = None
    if request.method == 'POST':
        userid = request.form.get('userid')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmpass')
        
        # Check if passwords match
        if password != confirm_password:
            error = "Passwords do not match"
        elif len(password)<6:
            error="Length of password should be at least 6 characters"
        elif not re.search("[\W_]", password):  # Check for special character
            error = "Password should contain at least one special character"
        else:
            # Check if user with same userid already exists
            existing_user = Logininfo.query.filter_by(userid=userid).first()
            if existing_user:
                error = "User already exists"
            else:
                entry = Logininfo(userid=userid, password=password,username=username)
                db.session.add(entry)
                db.session.commit()
                # Clear error message from session
                session.pop('error', None)
                mail.send_message('Account created on',
                sender="rvdautpure21tp@gmail.com",
                recipients=[userid],  # Pass email address as a list
                body=f"Dear {username} you have login succesfully.")
                # Redirect to success page or any other page after successful account creation
                return redirect(url_for('success'))
    
    # Store error message in session
    session['error'] = error if error else None
    return render_template('file3CREATE.html', error=error)

@app.route("/success")
def success():
    error = session.pop('error', None)
    return render_template('index.html',error="You have succesfully registered 🎉")




@app.route("/forgotpass", methods=['GET', 'POST'])
def forgot():
    error=None
    if request.method == 'POST':
        email=request.form.get('email')
        if not email:
            error="Enter your email"
        else:
            user=Logininfo.query.filter_by(userid=email).first()
            print("hello")
            print(user)
            if not user:
                error="You are not user"
            else:
                otp = ''.join(random.choices('0123456789', k=5))
                otp_add = Otp(email=email, otp=otp)
                db.session.add(otp_add)
                db.session.commit()
                mail.send_message('OTP Request',
                    sender="rvdautpure21tp@gmail.com",
                    recipients=[email],  # Pass email address as a list
                    body=f"Your OTP is {otp}.\n Do not share this OTP with anyone.")
                # error="OTP sent to your email"
                return render_template('file4(OTP).html',email=email)
    return render_template('forgetpassword.html',error=error)



@app.route("/mainpage")
def mainpage():
    session.pop('error', None)
    # Check if user is logged in
    if 'loggedin' in session:
        return render_template('mainpage.html')
    else:
        return redirect(url_for('/'))  # Redirect to login page if not logged in


@app.route('/teacher.html')
def teacher_page():
    return render_template('teacher.html')

@app.route('/info.html')
def info_page():
    return render_template('info.html')

@app.route('/user.html')
def users():
    usercurrent=session.get('userid')
    # Fetch user data from the database
    users = Logininfo.query.filter_by(userid=usercurrent)
    print(usercurrent)

    if users:
        return render_template('user.html',users=users)

    
    # Render the template with the user data
    return render_template('mainpage.html')

import requests

@app.route('/logout')
def logout():
    truncate_tables()
    session.pop('userid',None)
    return render_template('index.html')


@app.route('/timetable.html')
def generatetimetable_page():
    response = requests.get('http://localhost:3000')
    html_content = response.content.decode('utf-8')
    return render_template('timetable.html', html_content=html_content)

    return render_template('timetable.html') 


@app.route('/addclassroom.html')
def addclassroom_page():
    return render_template('addclassroom.html')


@app.route('/displayteacher.html')
def display_teachers():
    return render_template('displayteacher.html') 


@app.route('/mainpage.html')
def main_page():
    return render_template('mainpage.html')



























class Teacher(db.Model):
    teacherid = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.Integer, nullable=False)

class Teacher2(db.Model):
    teacherid = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.Integer, nullable=False)

class Classroom(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

""" class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=Fa lse)"""
class Branch(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(100), nullable=False)

# class TT(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     teacher = db.Column(db.String(500), nullable=False)
#     subject = db.Column(db.String(100), nullable=False)
#     division = db.Column(db.String(50))
#     day = db.Column(db.String(50))
#     time = db.Column(db.String(10))
#     classroom = db.Column(db.String(50))
    


# Route to handle adding classrooms
@app.route('/add_classroom', methods=['POST'])
def add_classroom():
    try:
        classroom_name = request.form['classroom_name']

        new_classroom = Classroom(name=classroom_name)
        db.session.add(new_classroom)
        db.session.commit()

        error_message = "Classroom added succesfully."
        return render_template('mainpage.html', error_message=error_message)
    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction to avoid leaving it in an inconsistent state
        error_message = "Classroom already exists. Please choose different classroom."
        return render_template('mainpage.html', error_message=error_message)





def generate_timetable1(start_time, end_time, break_start_time, break_end_time):
    # Retrieve teachers and subjects from the database
    teachers = Teacher.query.all()
    subjects = list(set(teacher.subject for teacher in teachers))  # Convert subjects set to a list
    classrooms = Classroom.query.all()  # Retrieve all classrooms from the database
    timetable = {}

    # Convert start and end time strings to datetime objects
    start_time = datetime.strptime(start_time, "%H:%M")
    end_time = datetime.strptime(end_time, "%H:%M")
    break_start_time = datetime.strptime(break_start_time, "%H:%M")
    break_end_time = datetime.strptime(break_end_time, "%H:%M")

    # Define available time slots
    time_slots = []
    current_time = start_time
    while current_time < end_time:
        time_slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(hours=1)

    # Iterate over each day of the week
    for day in range(1, 7):
        daily_timetable = []
        assigned_subjects = {teacher.teacherid: set() for teacher in teachers}  # To track assigned subjects for each teacher

        random.shuffle(teachers)
        random.shuffle(subjects)  # Shuffle subjects for each day

        for time_slot in time_slots:
            if break_start_time <= datetime.strptime(time_slot, "%H:%M") < break_end_time:
                daily_timetable.append((day, time_slot, "", "Break", ""))  # Add break time slot
                continue

            # Shuffle subjects for each loop iteration to increase randomness
            random.shuffle(subjects)
            subject_assigned = False

            for subject in subjects:
                # Find a teacher who can teach the subject and has not taught it the maximum number of times
                teacher = None
                for t in teachers:
                    if t.subject == subject and len(assigned_subjects[t.teacherid]) < t.frequency and subject not in assigned_subjects[t.teacherid]:
                        teacher = t
                        assigned_subjects[t.teacherid].add(subject)
                        break

                if teacher:  # Assign the subject to the teacher
                    # Choose a random classroom from the available classrooms
                    classroom = random.choice(classrooms)
                    daily_timetable.append((day, time_slot, teacher.name, subject, classroom.name))  # Add classroom name
                    subject_assigned = True
                    break

            if subject_assigned:
                continue  # Move to the next time slot

        timetable[day] = daily_timetable

    return timetable


def generate_timetable2(start_time, end_time, break_start_time, break_end_time):
    # Retrieve teachers and subjects from the database
    teachers = Teacher2.query.all()
    subjects = list(set(teacher.subject for teacher in teachers))  # Convert subjects set to a list
    classrooms = Classroom.query.all()  # Retrieve all classrooms from the database
    timetable = {}

    # Convert start and end time strings to datetime objects
    start_time = datetime.strptime(start_time, "%H:%M")
    end_time = datetime.strptime(end_time, "%H:%M")
    break_start_time = datetime.strptime(break_start_time, "%H:%M")
    break_end_time = datetime.strptime(break_end_time, "%H:%M")

    # Define available time slots
    time_slots = []
    current_time = start_time
    while current_time < end_time:
        time_slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(hours=1)

    # Iterate over each day of the week
    for day in range(1, 7):
        daily_timetable = []
        assigned_subjects = {teacher.teacherid: set() for teacher in teachers}  # To track assigned subjects for each teacher

        random.shuffle(teachers)
        random.shuffle(subjects)  # Shuffle subjects for each day

        for time_slot in time_slots:
            if break_start_time <= datetime.strptime(time_slot, "%H:%M") < break_end_time:
                daily_timetable.append((day, time_slot, "", "Break", ""))  # Add break time slot
                continue

            # Shuffle subjects for each loop iteration to increase randomness
            random.shuffle(subjects)
            subject_assigned = False

            for subject in subjects:
                # Find a teacher who can teach the subject and has not taught it the maximum number of times
                teacher = None
                for t in teachers:
                    if t.subject == subject and len(assigned_subjects[t.teacherid]) < t.frequency and subject not in assigned_subjects[t.teacherid]:
                        teacher = t
                        assigned_subjects[t.teacherid].add(subject)
                        break

                if teacher:  # Assign the subject to the teacher
                    # Choose a random classroom from the available classrooms
                    classroom = random.choice(classrooms)
                    daily_timetable.append((day, time_slot, teacher.name, subject, classroom.name))  # Add classroom name
                    subject_assigned = True
                    break

            if subject_assigned:
                continue  # Move to the next time slot

        timetable[day] = daily_timetable

    return timetable



@app.route('/add_teacher_subject', methods=['POST'])
def add_teacher_subject():
    try:
        year = request.form['year']
        division = request.form['division']
        teacherid = request.form['teacherid']
        name = request.form['teachername']
        subject = request.form['subject']
        frequency = request.form['frequency']
        branch = request.form['branch']

        if should_truncate(branch, year):
            truncate_tables()

        new_branch = Branch(name=branch, year=year)
        db.session.add(new_branch)
        db.session.commit()

        if division == '1':
            new_teacher_subject = Teacher(teacherid=teacherid, name=name, subject=subject, frequency=frequency)
        elif division == '2':
            new_teacher_subject = Teacher2(teacherid=teacherid, name=name, subject=subject, frequency=frequency)
        else:
            return 'Invalid division'

        db.session.add(new_teacher_subject)
        db.session.commit()
        error_message = "Teacher added succesfully."
        return render_template('teacher.html', error_message=error_message)
    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction to avoid leaving it in an inconsistent state
        error_message = "Teacher ID already exists. Please choose a different ID."
        return render_template('teacher.html', error_message=error_message)





def should_truncate(branch, year):
    # Check if the provided branch is different from the existing branch in the database
    existing_branch = Branch.query.first()
    if existing_branch:
        if (branch != existing_branch.name or year!=existing_branch.year):
            return True
        else:
            return False
        

def truncate_tables():
    # Truncate all tables in the database
    db.session.query(Teacher).delete()
    db.session.query(Teacher2).delete()
    db.session.query(Classroom).delete()
    db.session.query(Branch).delete()
    db.session.commit()

def calculate_time_slots(start, end, interval):
        start = datetime.strptime(start, "%H:%M")
        end = datetime.strptime(end, "%H:%M")  
        time_slots = []
        current_time = start
        while current_time < end:
            time_slots.append(current_time.strftime("%H:%M"))
            current_time += interval
        return time_slots 

@app.route('/generate_timetable', methods=['POST'])       
def generate_timetable_route():
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    break_start_time = request.form['break_start_time']
    break_end_time = request.form['break_end_time']


    time_slots = calculate_time_slots(start_time, end_time, timedelta(hours=1)) 
    timetable = {}  # Initialize an empty timetable dictionary
    
    # Generate timetable for Division 1
    timetable['Division 1'] = generate_timetable1(start_time, end_time, break_start_time, break_end_time)
    
    # Generate timetable for Division 2
    # timetable['Division 2'] = generate_timetable2(start_time, end_time, break_start_time, break_end_time)

    if Teacher2.query.count() > 0:
        timetable['Division 2'] = generate_timetable2(start_time, end_time, break_start_time, break_end_time)

    # Print the generated timetable
    for division, division_timetable in timetable.items():
        print(f"Timetable for {division}:")
        for day, entries in division_timetable.items():
            print(f"Day: {day}")
            for entry in entries:
                print(f"Time: {entry[1]}, Teacher: {entry[2]}, Subject: {entry[3]}, Classroom: {entry[4]}")
                # new_tt = TT(teacher={entry[2]},subject={entry[3]},division=division,day=day,time={entry[1]},classroom={entry[4]})
                # db.session.add(new_tt)
                # db.session.commit()

    day_names = {
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday'
    }

    return render_template('timetable.html',time_slots= time_slots, timetable=timetable, day_names=day_names)





























@app.route('/div1')
def display_div1():
    # Fetch data from the teacher table
    teachers = Teacher.query.all()
    return render_template('displayteacher.html', teachers=teachers)

@app.route('/div2')
def display_div2():
    # Fetch data from the teacher2 table
    teachers2 = Teacher2.query.all()
    return render_template('displayteacher.html', teachers2=teachers2)


@app.route('/edit_teacher/<teacher_id>')
def edit_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    return render_template('edit_teacher.html', teacher=teacher,div='1')
 

@app.route('/edit_teacher2/<teacher_id>')
def edit_teacher2(teacher_id):
    teacher = Teacher2.query.get(teacher_id)
    return render_template('edit_teacher.html', teacher=teacher)

@app.route('/update_teacher/<teacher_id>', methods=['POST'])
def update_teacher(teacher_id):
    if request.method == 'POST':
        teacher = Teacher.query.get(teacher_id)
        teacher.name = request.form['name']
        teacher.subject = request.form['subject']
        teacher.frequency = request.form['frequency']
        db.session.commit()
        return redirect(url_for('display_div1')) 

@app.route('/update_teacher2/<teacher_id>', methods=['POST'])
def update_teacher2(teacher_id):
    if request.method == 'POST':
        teacher = Teacher2.query.get(teacher_id)
        teacher.name = request.form['name']
        teacher.subject = request.form['subject']
        teacher.frequency = request.form['frequency']
        db.session.commit()
        return redirect(url_for('display_div2'))  

@app.route('/delete_teacher/<teacher_id>', methods=['POST'])
def delete_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        db.session.delete(teacher)
        db.session.commit()
    return redirect(url_for('display_div1', div=request.form['div']))


@app.route('/delete_teacher2/<teacher_id>', methods=['POST'])
def delete_teacher2(teacher_id):
    teacher = Teacher2.query.get(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    return redirect(url_for('display_div2', div=request.form['div']))
    





""" @app.route('/get_pdf', methods=['POST'])
def view_timetable():
    # Fetch data from the TT table
    timetable_data = TT.query.all()  # Assuming you want to fetch all records

    # Prepare a dictionary to store timetable entries for each division
    timetable = {'Division 1': {}, 'Division 2': {}}

    # Populate the timetable dictionary with fetched data
    for entry in timetable_data:
        division = entry.division
        day = entry.day
        time = entry.time
        teacher = entry.teacher
        subject = entry.subject
        classroom = entry.classroom

        # Check if the division exists in the timetable dictionary
        if division in timetable:
            # Check if the day exists for the division
            if day in timetable[division]:
                # Append the timetable entry for the day
                timetable[division][day].append((time, teacher, subject, classroom))
            else:
                # Initialize the day with the timetable entry
                timetable[division][day] = [(time, teacher, subject, classroom)]
    
    day_names = {
        '1': 'Monday',
        '2': 'Tuesday',
        '3': 'Wednesday',
        '4': 'Thursday',
        '5': 'Friday',
        '6': 'Saturday'
    }
    
    # Pass the timetable data to the HTML template for rendering
    rendered = render_template('timetablepdf.html', timetable=timetable, day_names=day_names)

    pdf = pdfkit.from_string(rendered, False, configuration=config, options={'enable-local-file-access': None})
    TT.query.delete()
    db.session.commit()
    response = make_response(pdf)
    response.headers['content-Type'] = 'application/pdf'
    response.headers['content-Disposition'] = 'inline: filename' + '.pdf'
    return response
 """

from flask import make_response
""" 
@app.route('/get_pdf', methods=['POST'])
def get_pdf():
    # Fetch data from the TT table
    timetable_data = TT.query.all()  # Assuming you want to fetch all records

    # Prepare a dictionary to store timetable entries for each division
    timetable = {'Division 1': {}, 'Division 2': {}}

    # Populate the timetable dictionary with fetched data
    for entry in timetable_data:
        division = entry.division
        day = entry.day
        time = entry.time
        teacher = entry.teacher
        subject = entry.subject
        classroom = entry.classroom

        # Check if the division exists in the timetable dictionary
        if division in timetable:
            # Check if the day exists for the division
            if day in timetable[division]:
                # Append the timetable entry for the day
                timetable[division][day].append((time, teacher, subject, classroom))
            else:
                # Initialize the day with the timetable entry
                timetable[division][day] = [(time, teacher, subject, classroom)]

    day_names = {
        '1': 'Monday',
        '2': 'Tuesday',
        '3': 'Wednesday',
        '4': 'Thursday',
        '5': 'Friday',
        '6': 'Saturday'
    }

    # Pass the timetable data to the HTML template for rendering
    rendered = render_template('timetablepdf.html', timetable=timetable, day_names=day_names)

    pdf = pdfkit.from_string(rendered, False, configuration=config, options={'enable-local-file-access': None})
    TT.query.delete()
    db.session.commit()

    # Create a response with the PDF content
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=timetable.pdf'  # Set Content-Disposition to "attachment"

    return response """




def get_time_bounds(timetable_data, division):
    smallest_time = None
    biggest_time = None

    for entry in timetable_data:
        if entry.division == division:
            current_time = datetime.strptime(entry.time, '%H:%M')
            if smallest_time is None or current_time < smallest_time:
                smallest_time = current_time
            if biggest_time is None or current_time > biggest_time:
                biggest_time = current_time

    return smallest_time.strftime('%H:%M'), biggest_time.strftime('%H:%M')



# Inside your `get_pdf` function
# @app.route('/get_pdf', methods=['POST'])
# def get_pdf():
#     # Fetch data from the TT table
#     timetable_data = TT.query.all()  # Assuming you want to fetch all records

#     # Prepare a dictionary to store timetable entries for each division
#     timetable = {'Division 1': {}, 'Division 2': {}}

#     # Populate the timetable dictionary with fetched data
#     for entry in timetable_data:
#         division = entry.division
#         day = entry.day
#         time = entry.time
#         teacher = entry.teacher
#         subject = entry.subject
#         classroom = entry.classroom

#         # Check if the division exists in the timetable dictionary
#         if division in timetable:
#             # Check if the day exists for the division
#             if day in timetable[division]:
#                 # Append the timetable entry for the day
#                 timetable[division][day].append((time, teacher, subject, classroom))
#             else:
#                 # Initialize the day with the timetable entry
#                 timetable[division][day] = [(time, teacher, subject, classroom)]

#     # Find smallest and biggest time slots for each division
#     time_bounds = {}
#     for division in timetable.keys():
#         time_bounds[division] = get_time_bounds(timetable_data, division)

#     time_bounds = {}
#     for division in timetable.keys():
#         smallest_time, biggest_time = get_time_bounds(timetable_data, division)
#     print(smallest_time,biggest_time)
#     print("Time Bounds:", time_bounds)
#     smallest_hour = int(smallest_time.split(':')[0])  # Extract the hour part and convert to int
#     biggest_hour = int(biggest_time.split(':')[0])  

    
#     day_names = {
#         '1': 'Monday',
#         '2': 'Tuesday',
#         '3': 'Wednesday',
#         '4': 'Thursday',
#         '5': 'Friday',
#         '6': 'Saturday'
#     }

#     if Teacher2.query.count() > 0:
#         poss=1

#     # Pass the timetable data and time slots to the HTML template for rendering
#     rendered = render_template('timetablepdf.html', timetable=timetable,smallest_hour=smallest_hour,biggest_hour=biggest_hour ,day_names=day_names,poss=poss)
#     pdf = pdfkit.from_string(rendered, False, configuration=config, options={'enable-local-file-access': None})
#     TT.query.delete()
#     db.session.commit()

#     # Create a response with the PDF content
#     response = make_response(pdf)
#     response.headers['Content-Type'] = 'application/pdf'
#     response.headers['Content-Disposition'] = 'attachment; filename=timetable.pdf'  # Set Content-Disposition to "attachment"

#     return response












@app.route("/verify_otp", methods=['POST'])
def verify_otp():
    if request.method == 'POST':
        otp_entered = request.form.get('otp')
        email = request.form.get('email')  # Get the email from the form
        otp_record = Otp.query.filter_by(email=email).first()
        print(f"otp_entered:{otp_entered},{type(otp_entered)}")
        print(f"otp_record:{otp_record.otp},{type(otp_record)}")
        if otp_record.otp:
            if int(otp_entered) == int(otp_record.otp):
                return redirect(url_for('OTPchange_password', email=email))
                

            else:
                return "Incorrect OTP"
        else:
            return "No OTP found for this email"
    else:
        return "Invalid request method"
    
@app.route("/OTPchange_password/<email>", methods=['GET', 'POST'])  # Added email parameter to the route
def OTPchange_password(email):
    return render_template('change_password.html', email=email)


@app.route("/change_password", methods=['POST'])
def change_password_otp():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        userid = request.form.get('email')

        # Ensure the new password and confirm password match
        if new_password != confirm_password:
            return "Passwords do not match"

        # Retrieve the email from the Otp table
        otp_record = Otp.query.filter_by(email=userid).first()
        print(otp_record)
        if not otp_record:
            return "No OTP found for this email"
        
        # Retrieve the user from the User table based on the email
        user = Logininfo.query.filter_by(userid=otp_record.email).first()
        print(f"{type(otp_record.email)}")
        print(f"Userid:{type(userid)}")
        print(user)
        if not user:
            return "User not found"
        
        # Update the user's password
        user.password = new_password
        db.session.commit()
        db.session.delete(otp_record)
        db.session.commit()
        error= "Password updated successfully"
        return render_template('index.html', error=error)
    else:
        return "Invalid request method"




if __name__ == '__main__':
    app.run(debug=True,port=3000)

