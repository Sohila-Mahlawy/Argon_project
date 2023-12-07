
from flask import Flask, render_template, request, redirect, session,url_for,flash
import requests
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, logout_user, current_user
from sqlalchemy.exc import NoResultFound
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from functools import wraps

app = Flask(__name__)
# load the extension
login_manager = LoginManager(app)


app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
with app.app_context():
    user_student_association = db.Table(
        'user_student_association',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('student_id', db.Integer, db.ForeignKey('students.id'))
    )


    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        phone = db.Column(db.String(100))
        password = db.Column(db.String(100))
        name = db.Column(db.String(1000))
        role = db.Column(db.String(1000), default="user")
        students = db.relationship('Students', secondary=user_student_association, back_populates='users')


    class Students(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(1000))
        parent_name = db.Column(db.String(1000))
        parent_phone = db.Column(db.String(1000))
        users = db.relationship('User', secondary=user_student_association, back_populates='students')


    class Teacher(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(1000))
        phone = db.Column(db.String(100), unique=True)
        teacher_sample = db.Column(db.String(100))
        status = db.Column(db.String(100))
        videos = db.relationship('Videos', back_populates='teacher')


        def __repr__(self):
            return f"<Teacher {self.name}>"


    class Courses(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        course_name = db.Column(db.String(1000))
        teacher_name = db.Column(db.String(100))
        teacher_phone = db.Column(db.String(100))
        course_price = db.Column(db.Integer)
        rate = db.Column(db.String(100))
        course_sample = db.Column(db.String(100))
        status = db.Column(db.String(100))



    class Videos(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(1000))
        description = db.Column(db.String(100))
        grade = db.Column(db.Integer)
        teacher_name = db.Column(db.String(100))
        teacher_phone = db.Column(db.String(100))
        course_name = db.Column(db.String(100))
        video_url = db.Column(db.String(200))  # New column for video URL
        video_status = db.Column(db.String(100))
        teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
        teacher = db.relationship('Teacher', back_populates='videos')

        def __repr__(self):
            return f"<Video {self.name}>"


    class Paid_courses(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        course_name = db.Column(db.String(1000))
        teacher_name = db.Column(db.String(100))
        teacher_phone = db.Column(db.String(100))
        user_name = db.Column(db.String(100))
        user_phone = db.Column(db.String(100))
        user_id = db.Column(db.String(100))
        course_id = db.Column(db.String(100))


    class Question(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        question_text = db.Column(db.String(255), nullable=False)
        course_name = db.Column(db.String(255))
        answers = db.relationship('Answer', backref='question', lazy=True)



    class Answer(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        answer_text = db.Column(db.String(255), nullable=False)
        is_correct = db.Column(db.Boolean, default=False)
        question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)


    class QuizResult(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, nullable=False)
        name=db.Column(db.Integer, nullable=False)
        course_name = db.Column(db.String(255), nullable=False)
        parent_name=db.Column(db.String(255), nullable=False)
        score = db.Column(db.Integer, nullable=False)

    db.create_all()



class MyModelView(ModelView):
    def is_accessible(self):
        # Check if the user is logged in and has the 'admin' role
        if 'user_role' in session and session['user_role'] == 'admin':
            return True
        return False






admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Students, db.session))
admin.add_view(MyModelView(Teacher, db.session))
admin.add_view(MyModelView(Courses, db.session))
admin.add_view(MyModelView(Videos, db.session))
admin.add_view(MyModelView(Paid_courses, db.session))
admin.add_view(MyModelView(Question, db.session))
admin.add_view(MyModelView(Answer, db.session))
admin.add_view(MyModelView(QuizResult, db.session))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    courses = Courses.query.all()
    teachers = Teacher.query.all()
    return render_template("index.html",courses=courses,teachers=teachers)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/feature")
def feature():
    return render_template("feature.html")
# @app.route("/redirecting")
# def redirecting():
#     user_name = session.get('user_name')
#     students = Students.query.all()
#     my_children = []
#     for student in students:
#         if student.parent_name == user_name:
#             my_children.append(student)
#     return render_template("redirecting.html",my_children=my_children)





@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        phone = request.form.get("phone")
        name = request.form.get("name")
        password = request.form.get("password")
        new_user = User(
            name=name,
            phone=phone,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        phone = request.form.get("your_phone")
        password = request.form.get("your_pass")
        role_user = "user"
        role_teacher = "teacher"
        role_admin = "admin"
        role_student='student'

        users = User.query.all()
        for user in users:
            if phone == user.phone and password == user.password and role_user==user.role:
                # Assuming 'id', 'name', and 'phone' are attributes of your User model
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_phone'] = user.phone
                session['user_role'] = user.role
                return redirect("/profile")

            if phone == user.phone and password == user.password and role_teacher==user.role:
                # Assuming 'id', 'name', and 'phone' are attributes of your User model
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_phone'] = user.phone
                session['user_role'] = user.role
                return redirect("/teacher_profile")

            if phone == user.phone and password == user.password and role_student==user.role:
                # Assuming 'id', 'name', and 'phone' are attributes of your User model
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_phone'] = user.phone
                session['user_role'] = user.role
                return redirect("/child_pro")

            if phone == user.phone and password == user.password and role_admin==user.role:
                # Assuming 'id', 'name', and 'phone' are attributes of your User model
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_phone'] = user.phone
                session['user_role'] = user.role
                return redirect("/admin_dashboard")

            if phone == user.phone and password == user.password :
                # Assuming 'id', 'name', and 'phone' are attributes of your User model
                session['user_id'] = user.id
                session['user_name'] = user.name

                return redirect("/redirecting")

        return redirect("/register")
    return render_template("login.html")
@app.route("/child_pro")
def child_pro():
    # Retrieve user information from the session
    user_role = session.get('user_role')
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_phone = session.get('user_phone')
    if user_role == "student":
        # Use the user information in your template
        return render_template("child_profile.html", user_id=user_id, user_name=user_name, user_phone=user_phone)
    else:
        return ('YOU ARE NOT A REGULAR USER')

@app.route("/profile")
def profile():
    # Retrieve user information from the session
    user_role = session.get('user_role')
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_phone = session.get('user_phone')
    students = Students.query.all()
    my_children = []
    for student in students:
        if student.parent_name == user_name:
            my_children.append(student)
    if user_role == "user":
        # Use the user information in your template
        return render_template("profile.html", user_id=user_id, user_name=user_name, user_phone=user_phone, my_children=my_children)
    else:
        return ('YOU ARE NOT A REGULAR USER')
@app.route("/teacher_profile")
def teacher_profile():
    # Retrieve user information from the session
    user_role = session.get('user_role')
    user_name = session.get('user_name')
    user_phone = session.get('user_phone')
    user_id = session.get("user_id")
    if user_role == "teacher":
        # Use the user information in your template
        return render_template("teacher_profile.html", user_id=user_id, user_name=user_name, user_phone=user_phone)
    else:
        return ('YOU ARE NOT A TEACHER')

@app.route("/admin")
def admin():
    user_role = session.get('user_role')
    user_name = session.get('user_name')
    user_phone = session.get('user_phone')
    user_id = session.get("user_id")
    if user_role == "admin":
        return redirect("/admin/")
    else:
         return ('YOU ARE NOT AN ADMIN')


@app.route("/paid_courses")
def paid():
    # Retrieve user information from the session
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_phone = session.get('user_phone')
    paid_courses=Paid_courses.query.all()
    my_courses=[]
    for course in paid_courses:
        if   user_name == course.user_name and user_phone==course.user_phone :
            my_courses.append(course)
            print (course)

    # Use the user information in your template
    return render_template("paid_courses.html", user_id=user_id, user_name=user_name, user_phone=user_phone,paid_courses=my_courses)

@app.route("/course")
def course():
    # Retrieve user information from the session
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_phone = session.get('user_phone')

    all_courses=Courses.query.filter_by(status='approved')

    # Pass user information and courses to the template
    return render_template("course.html", user_id=user_id, user_name=user_name, user_phone=user_phone, all_courses=all_courses)

@app.route('/detail/<int:id>')
def detail(id):
    course = Courses.query.filter_by(id=id).first()
    course_id = course.id
    course_name = course.course_name
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_phone = session.get('user_phone')
    paid_courses = Paid_courses.query.all()
    all_videos = Videos.query.all()
    videos = []

    if course:
        course_name = course.course_name
        teacher_name = course.teacher_name
        teacher_phone = course.teacher_phone
        price = course.course_price
        for c in paid_courses:
            if c.course_name == course_name and c.teacher_name==teacher_name and c.teacher_phone==teacher_phone and c.user_phone==user_phone:
                for video in all_videos:
                    if video.course_name == course_name and video.teacher_name == teacher_name:
                            videos.append(video)

    return render_template("detail.html", videos=videos, current_name=course.course_name, user_id=user_id, user_name=user_name, user_phone=user_phone, course=course)



@app.route('/video/<int:id>')
def video_detail(id):
    videos = Videos.query.filter_by(id=id)
    for video in videos:
        name=video.name
        description=video.description
        video_file=video.video_url

    return render_template("video_detail.html", videos=video, name=name,description=description,video_file=video_file)


class PurchaseForm(FlaskForm):
    user_name = StringField('Your Name', validators=[DataRequired()])
    user_phone = StringField('Your Phone Number', validators=[DataRequired()])
    submit = SubmitField('Purchase')

@app.route("/buy_course/<int:id>", methods=["GET", "POST"])
def buy_course(id):
    form = PurchaseForm()

    if request.method == "POST" and form.validate_on_submit():
        course = Courses.query.filter_by(id=id).first()

        if course:
            user_id = session.get('user_id')
            course_name = course.course_name
            teacher_name = course.teacher_name
            teacher_phone = course.teacher_phone
            course_id = course.id

            user_name = form.user_name.data
            user_phone = form.user_phone.data

            try:
                existing_purchase = Paid_courses.query.filter_by(
                    user_phone=user_phone,
                    course_name=course_name,
                    user_name=user_name,
                    course_id=course_id
                ).one()

                return 'already purchased'

            except NoResultFound:
                buy = Paid_courses(
                    course_name=course_name,
                    teacher_name=teacher_name,
                    teacher_phone=teacher_phone,
                    course_id=id,
                    user_id=user_id,
                    user_name=user_name,
                    user_phone=user_phone,
                )
                db.session.add(buy)
                db.session.commit()

                return render_template("payment_success.html")

    return render_template("purchase_course.html", form=form)
# Additional note: Make sure to handle errors and edge cases appropriately in your actual implementation.




@app.route("/maketeacher", methods=["GET", "POST"])
def maketeacher():
    if request.method == "POST":
        phone = session.get('user_phone')
        all_users = User.query.filter_by(phone=phone).all()
        teacher_sample= request.form.get("teacher_sample")
        for user in all_users:
            if phone == user.phone:
                new_teacher = Teacher(
                    name=user.name,
                    phone=user.phone,
                    teacher_sample= teacher_sample,
                    status='pending'

                )
                db.session.add(new_teacher)
                db.session.commit()

                return render_template("pending_accounts.html", user=user)

        return 'User not found'

    return render_template("maketeacher.html")



@app.route("/approve_teacher_request/<int:request_id>")
def approve_teacher_request(request_id):
    # Retrieve the specific teacher request
    teacher_request = Teacher.query.get(request_id)

    # Check if the teacher request exists and is 'pending'
    if teacher_request and teacher_request.status == 'pending':
        # Update the status to 'approved'
        teacher_request.status = 'approved'
        db.session.commit()

        # Update the corresponding user's role to 'teacher'
        user = User.query.filter_by(phone=teacher_request.phone).first()
        if user:
            user.role = 'teacher'
            db.session.commit()

        return redirect("/admin_dashboard")

@app.route("/view_teacher_sample/<int:request_id>")
def view_teacher_sample(request_id):
    teacher = Teacher.query.filter_by(id=request_id).first()

    if teacher:
        name = teacher.name
        phone = teacher.phone
        video_file = teacher.teacher_sample
        return render_template("view_teacher_sample.html", name=name, phone=phone, video_file=video_file)
    else:
        return "No teacher found with this ID."


@app.route("/createcourse", methods=["GET", "POST"])
def createcourse():
    # Check if the user is logged in and has the role 'teacher'
    user_id = session.get('user_id')
    user_role = session.get('user_role')

    # Assuming 'teacher' is the role for teachers
    if user_id and user_role == 'teacher':
        if request.method == "POST":
            teacher_name = session.get('user_name')
            teacher_phone = session.get('user_phone')
            course_name = request.form.get("course_name")
            course_price = request.form.get("course_price")
            course_sample = request.form.get("course_sample")
            new_course = Courses(
                course_name=course_name,
                teacher_name=teacher_name,
                teacher_phone=teacher_phone,
                course_price=course_price,
                course_sample=course_sample,
                status='pending'
            )
            db.session.add(new_course)
            db.session.commit()
            return redirect("teacher_profile")
        return render_template("create_course.html")

    # If the user is not a teacher, you may want to redirect them or show an error
    return "Unauthorized access"


@app.route("/approve_course_request/<int:course_id>")
def approve_course_request(course_id):
    # Retrieve the specific course request
    course_request = Courses.query.get(course_id)

    # Update the status to 'approved'
    if course_request:
        course_request.status = 'approved'
        db.session.commit()

    return redirect("/admin_dashboard")


@app.route("/course_detail/<int:course_id>")
def course_detail(course_id):
    # Use .first() to get the first result or None
    course = Courses.query.filter_by(id=course_id).first()

    if course:
        course_name = course.course_name
        teacher_name = course.teacher_name
        course_sample = course.course_sample

        return render_template("course_detail.html", course_name=course_name, teacher_name=teacher_name, course_sample=course_sample)
    else:
        # Handle the case where the course with the given ID is not found
        return render_template("course_not_found.html")

@app.route("/create_video/<int:course_id>", methods=["GET", "POST"])
def create_video(course_id):
    if request.method == "POST":
        course = Courses.query.get(course_id)
        if course:
            course_name = course.course_name
            teacher_name = session.get('user_name')
            teacher_phone = session.get('user_phone')
            name = request.form.get("name")
            description = request.form.get("description")
            video_url = request.form.get("video_url")
            subscription_type = request.form.get("subscription_type")

            new_video = Videos(
                name=name,
                description=description,
                teacher_name=teacher_name,
                teacher_phone=teacher_phone,
                course_name=course_name,
                video_url=video_url,
                video_status=subscription_type
            )

            db.session.add(new_video)
            db.session.commit()
            return redirect("/teacher_profile")
        else:
            return 'no'

    return render_template("create_video.html")



@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/logout")
def logout():

    session.clear()
    return 'Logged out successfully'

@app.route("/add", methods=["GET","POST"])
def add():
    user_id = session.get('user_id')
    user_role = session.get('user_role')

    # Assuming 'teacher' is the role for teachers
    if user_id and user_role == 'user':

        if request.method == "POST":
            parent_phone = session.get('user_phone')
            child_name = request.form.get("child_name")
            phone = request.form.get("phone")
            password = request.form.get("password")
            parent = User.query.filter_by(phone=parent_phone).first()
            parent_name = parent.name

            new_student = Students(
                parent_name=parent_name,
                parent_phone=parent_phone,
                name=child_name
            )

            db.session.add(new_student)

            new_user = User(
                name=child_name,
                phone=phone,
                password=password,
                role='student'
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
        return render_template("add_child.html")
    # If the user is not a teacher, you may want to redirect them or show an error
    return "Only parent can add children"



@app.route("/child_profile/<int:id>")
def child_profile(id):
    child = Students.query.filter_by(id=id).first()

    # Assume you have some way of identifying the current user (parent or child)
    current_user_phone = session.get('parent_name')  # Replace with your actual session key

    if child.parent_name == current_user_phone:
        # This is the child's own profile
        return render_template("child_profile.html", user_name=child.name, is_child=True)
    else:
        # This is the parent viewing the child's profile
        return render_template("child_profile.html", user_name=child.name, is_child=False)

@app.route("/admin_dashboard")
def admin_dashboard():
    user_phone = session.get('user_phone')
    user = User.query.filter_by(phone=user_phone).first()

    if user and user.role == 'admin':
        pending_requests = Teacher.query.filter_by(status='pending').all()
        pending_courses = Courses.query.filter_by(status='pending').all()
    else:
        return ("Method not allowed")

    return render_template("admin_dashboard.html", pending_requests=pending_requests, pending_courses=pending_courses)

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    # Check if the user has the role 'teacher'
    if session.get('user_role') != 'teacher':
        # Redirect to a different page or display an error message
        return render_template('error.html', message='Access denied. You must be a teacher.')

    if request.method == 'POST':
        try:
            # Extract data from the form
            num_questions = int(request.form.get('num_questions'))

            for i in range(1, num_questions + 1):
                course_name = request.form.get(f'course_name_{i}')
                question_text = request.form.get(f'question_{i}')
                answer_texts = [request.form.get(f'answer_{i}_{j}') for j in range(1, 5)]
                correct_answer_index_str = request.form.get(f'correct_answer_{i}')
                correct_answer_index = int(correct_answer_index_str) if correct_answer_index_str.strip() else None

                # Create a new question
                # Create a new question
                question = Question(course_name=course_name, question_text=question_text)
                db.session.add(question)
                db.session.commit()

                # Create answers for the question
                for j, answer_text in enumerate(answer_texts):
                    is_correct = (j + 1 == correct_answer_index)  # Adjusted to 1-based index
                    answer = Answer(answer_text=answer_text, is_correct=is_correct, question=question)
                    db.session.add(answer)

                    # Save the correct answer for the question
                    if is_correct:
                        question.correct_answer = answer

                db.session.commit()

            return redirect(url_for('add_question'))

        except Exception as e:
            # Handle exceptions (e.g., validation errors)
            return render_template('error.html', message=str(e))

    return render_template('add_question.html')


@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    # Redirect to the profile page or another page after submitting the entire quiz
    return redirect(url_for('profile_page'))





@app.route('/quiz/<course_name>', methods=['GET', 'POST'])
def quiz(course_name):
    if session.get('user_role') != 'student':
        # Redirect to a different page or display an error message
        return render_template('error.html', message='Access denied. You must be a student.')

    user_id = session.get('user_id')
    user_name = session.get('user_name')

    # Check if the user has already taken the quiz for the specified course
    existing_result = QuizResult.query.filter_by(course_name=course_name, user_id=user_id).first()
    if existing_result:
        # If the user has already taken the quiz, redirect or display a message
        return render_template('error.html', message='You have already taken the quiz for this course.')

    if request.method == 'GET':
        # Retrieve questions for the specified course
        questions = Question.query.filter_by(course_name=course_name).all()

        return render_template('quiz.html', course_name=course_name, questions=questions)

    elif request.method == 'POST':
        # Retrieve the student record based on the user_name
        student = Students.query.filter_by(name=user_name).first()

        if student:
            parent_name = student.parent_name

            # Assuming the form is submitted with answer choices
            student_answers = request.form.to_dict()

            # Evaluate the student's answers
            score = evaluate_quiz(course_name, student_answers)

            # Save the quiz result to the database
            mark = QuizResult(
                course_name=course_name,
                user_id=user_id,
                name=user_name,
                score=score,
                parent_name=parent_name
            )
            db.session.add(mark)
            db.session.commit()

            return render_template('quiz_result.html', score=score)




def evaluate_quiz(course_name, student_answers):
    # Retrieve questions for the specified course
    questions = Question.query.filter_by(course_name=course_name).all()

    # Initialize the score
    score = 0

    for question in questions:
        # Get the correct answer for the question
        correct_answer = next((answer.answer_text for answer in question.answers if answer.is_correct), None)

        # Check if the student's answer matches the correct answer
        student_answer = student_answers.get(f'question_{question.id}')
        if student_answer and student_answer == correct_answer:
            score += 1

    return score


@app.route("/children_score", methods=["POST", "GET"])
def children_score():
    user_id = session.get('user_id')
    user_name = session.get('user_name')

    # Assuming Students model has a 'parent_name' property
    student = Students.query.filter_by(parent_name=user_name).first()
    parent_name = user_name

    children_score = []

    if parent_name:
        # Assuming QuizResult model has 'parent_name', 'child_name', and 'score' properties
        quiz_results = QuizResult.query.filter_by(parent_name=parent_name).all()

        for result in quiz_results:
            children_score.append({
                'child_name': result.name,
                'course_name':result.course_name,
                'score': result.score
            })

    return render_template("children_result.html", children_score=children_score)


@app.route("/result", methods=["POST", "GET"])
def result():
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_role = session.get('user_role')
    if user_id and user_role == 'student':
        result = QuizResult.query.all()
        children_score = []
        for mark in result:
            if mark.name==user_name:
                children_score.append(mark)
        return render_template("result.html", children_score=children_score)
    return "Only for children"
@app.route("/my_courses")
def my_courses():
    user_name = session.get('user_name')
    user_phone = session.get('user_phone')
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    courses = Courses.query.all()
    my_courses = []
    for course in courses:
        if course.teacher_name == user_name and course.teacher_phone == user_phone:
            my_courses.append(course)
    return render_template("my_courses.html", user_id=user_id, user_name=user_name, user_phone=user_phone, my_courses=my_courses)

@app.route('/my_course_detail/<int:id>')
def my_course_detail(id):
    course = Courses.query.filter_by(id=id).first()
    course_id = course.id
    course_name = course.course_name

    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_phone = session.get('user_phone')
    all_videos = Videos.query.all()
    videos = []

    if course:
        course_name = course.course_name
        teacher_name = course.teacher_name
        teacher_phone = course.teacher_phone
        price = course.course_price
        for video in all_videos:
            if video.course_name == course_name and video.teacher_name == teacher_name:
                videos.append(video)

    return render_template("my_course_detail.html", videos=videos, current_name=course.course_name, user_id=user_id, user_name=user_name, user_phone=user_phone, course=course)

@app.route("/my_students")
def my_students():
    user_name = session.get('user_name')
    user_phone = session.get('user_phone')
    courses = Paid_courses.query.all()
    my_students = []
    for student in courses:
        if student.teacher_name==user_name and student.teacher_phone==user_phone:
            my_students.append(student)
    return render_template("my_students.html", my_students=my_students)

if __name__ == "__main__":
    app.run(debug=True)