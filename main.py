from flask import Flask, render_template, request, redirect, session
import requests
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app=Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
with app.app_context():
    user_course_association = db.Table(
        'user_course_association',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
    )


    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        phone = db.Column(db.String(100))
        password = db.Column(db.String(100))
        name = db.Column(db.String(1000))
        role = db.Column(db.String(1000), default="user")
        courses = db.relationship('Courses', secondary=user_course_association, back_populates='users')

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
        users = db.relationship('User', secondary=user_course_association, back_populates='courses')

    class Videos(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(1000))
        description = db.Column(db.String(100))
        grade = db.Column(db.Integer)
        teacher_name = db.Column(db.String(100))
        teacher_phone = db.Column(db.String(100))
        course_name = db.Column(db.String(100))
        video_url = db.Column(db.String(200))  # New column for video URL
        teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
        teacher = db.relationship('Teacher', back_populates='videos')

        def __repr__(self):
            return f"<Video {self.name}>"


    # Define the Question model
    class Question(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        text = db.Column(db.String(255), nullable=False)
        answers = db.relationship('Answer', backref='question', lazy=True)


    class Answer(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        text = db.Column(db.String(255), nullable=False)
        is_correct = db.Column(db.Boolean, default=False)
        question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)


    db.create_all()
class MyModelView(ModelView):
    def is_accessible(self):
            return True

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Teacher, db.session))
admin.add_view(MyModelView(Courses, db.session))
admin.add_view(MyModelView(Videos, db.session))
@app.route("/")
def index():
    courses=Courses.query.all()
    teachers=Teacher.query.all()
    return render_template("index.html",courses=courses,teachers=teachers)

@app.route("/detail")
def detail():
    return render_template("detail.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/feature")
def feature():
    return render_template("feature.html")


@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        phone=request.form.get("phone")
        name=request.form.get("name")
        password=request.form.get("password")
        new_user=User(
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
        users = User.query.all()
        for user in users:
            if phone == user.phone and password == user.password and role_user == user.role:
                # Assuming 'id', 'name', and 'phone' are attributes of your User model
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_phone'] = user.phone
                return redirect("/profile")

            if phone == user.phone and password == user.password and role_teacher == user.role:
                # Assuming 'id', 'name', and 'phone' are attributes of your User model
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_phone'] = user.phone
                return redirect("/teacherprofile")

        return redirect("/register")
    return render_template("login.html")


@app.route("/profile")
def profile():
    # Retrieve user information from the session
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_phone = session.get('user_phone')

    # Use the user information in your template
    return render_template("profile.html", user_id=user_id, user_name=user_name, user_phone=user_phone)

@app.route("/teacherprofile")
def teacher_profile():
    # Retrieve user information from the session
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_phone = session.get('user_phone')

    # Use the user information in your template
    return render_template("teacher_profile.html", user_id=user_id, user_name=user_name, user_phone=user_phone)




@app.route("/course")
def course():
    all_courses = Courses.query.filter_by(status='approved').all()

    return render_template("course.html", all_courses=all_courses)

# @app.route('/detail/<int:id>')
# def detail(id):
#     courses=Courses.query.filter_by(id=id).first()
#     print (courses)
#     all_videos=Videos.query.all()
#     videos=[]
#     if courses:
#         course_name = courses.course_name
#         teacher_name=courses.teacher_name
#         price = courses.course_price
#         for i in all_videos:
#             if i.course_name==course_name and i.teacher_name==teacher_name:
#                 videos.append(i)
#
#     return render_template("detail.html",videos=videos,current_name=courses.course_name)

@app.route('/video/<int:id>')
def video_detail(id):
    videos = Videos.query.filter_by(id=id)
    for video in videos:
        name=video.name
        description=video.description
        video_file=video.video_url

    return render_template("video_detail.html", videos=video, name=name,description=description,video_file=video_file)




@app.route("/admin_dashboard")
def admin_dashboard():
    # Retrieve pending teacher requests
    pending_requests = Teacher.query.filter_by(status='pending').all()
    pending_courses = Courses.query.filter_by(status='pending').all()

    return render_template("admin_dashboard.html", pending_requests=pending_requests, pending_courses=pending_courses)


@app.route("/maketeacher", methods=["GET", "POST"])
def maketeacher():
    if request.method == "POST":
        phone = request.form.get("phone")
        all_users = User.query.filter_by(phone=phone).all()
        teacher_sample= request.form.get("teacher_sample")
        for user in all_users:
            if phone == user.phone:
                new_teacher = Teacher(
                    name=user.name,
                    phone=user.phone,
                    teacher_sample= teacher_sample,
                    status='pending' ,

                )
                db.session.add(new_teacher)
                db.session.commit()

                return redirect("/admin_dashboard")

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


@app.route("/createcourse", methods=["GET","POST"])
def createcourse():
    if request.method == "POST":
        course_name = request.form.get("course_name")
        teacher_name = request.form.get("teacher_name")
        teacher_phone = request.form.get("teacher_phone")
        course_price = request.form.get("course_price")
        course_sample = request.form.get("course_sample")
        new_course = Courses(
            course_name=course_name,
            teacher_name=teacher_name,
            teacher_phone=teacher_phone,
            course_price=course_price,
            course_sample=course_sample,
            status = 'pending'
        )
        db.session.add(new_course)
        db.session.commit()
        return redirect("teacherprofile")
    return render_template("create_course.html")


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
    courses = Courses.query.filter_by(id=course_id)
    for course in courses:
        course_name=course.course_name
        teacher_name=course.teacher_name
        course_sample=course.course_sample

    return render_template("video_detail.html", course_name=course_name, teacher_name=teacher_name,course_sample=course_sample)


@app.route("/contact")
def contact():
    return render_template("contact.html")


# # Sample data
# question1 = Question(text='What is the capital of France?')
# answer1 = Answer(text='Berlin', is_correct=False, question=question1)
# answer2 = Answer(text='Paris', is_correct=True, question=question1)
# answer3 = Answer(text='Madrid', is_correct=False, question=question1)
#
# question2 = Question(text='Which programming language is this example written in?')
# answer4 = Answer(text='Python', is_correct=True, question=question2)
# answer5 = Answer(text='Java', is_correct=False, question=question2)
# answer6 = Answer(text='C++', is_correct=False, question=question2)
#
# db.session.add_all([question1, answer1, answer2, answer3, question2, answer4, answer5, answer6])
# db.session.commit()
@app.route('/')
def quiz():
    questions = Question.query.all()
    return render_template('quiz.html', questions=questions)

# Route to process quiz submissions
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    score = 0
    questions = Question.query.all()

    for question in questions:
        user_answer_id = int(request.form.get(f'question_{question.id}'))
        user_answer = Answer.query.get(user_answer_id)

        if user_answer and user_answer.is_correct:
            score += 1

    return render_template('result.html', score=score)



if __name__=="__main__":
    app.run(debug=True)