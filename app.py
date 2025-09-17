import os
import csv
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session, make_response
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Course, ContactMessage, Student, Testimonial, Video, Exam
from forms import CourseForm, ContactForm, LoginForm, StudentRegistrationForm, StudentLoginForm, TestimonialForm, VideoForm, ExamForm
from config import Config

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'student_login'
login_manager.login_message = "الرجاء تسجيل الدخول للوصول إلى هذه الصفحة."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))

with app.app_context():
    db.create_all()
    
    # Add sample data if database is empty
    if Course.query.count() == 0:
        sample_courses = [
            Course(
                title="أساسيات الرياضيات",
                slug="math-basics-high-school",
                short_desc="دورة شاملة في أساسيات الرياضيات للصف الأول والثاني الثانوي",
                content="دورة متكاملة تغطي جميع أساسيات الرياضيات من الجبر إلى الهندسة مع حلول خطوة بخطوة",
                price=150.0,
                featured=True
            ),
            Course(
                title="الجبر والمعادلات المتقدمة",
                slug="advanced-algebra-equations",
                short_desc="تعلم الجبر المتقدم والمعادلات بطريقة مبسطة وممتعة",
                content="دورة تفصيلية في الجبر المتقدم تشمل المعادلات التربيعية والدوال والمخططات البيانية",
                price=200.0,
                featured=True
            ),
            Course(
                title="الهندسة التحليلية والتطبيقات",
                slug="analytical-geometry-applications",
                short_desc="أساسيات الهندسة التحليلية والتطبيقات العملية",
                content="دورة شاملة في الهندسة التحليلية مع التطبيقات العملية والمسائل المتنوعة والحلول الشاملة",
                price=250.0,
                featured=False
            ),
            Course(
                title="التفاضل والتكامل",
                slug="calculus-differentiation-integration",
                short_desc="مفاهيم التفاضل والتكامل بطريقة مبسطة",
                content="دورة شاملة في التفاضل والتكامل مع التطبيقات العملية والأمثلة المحلولة خطوة بخطوة",
                price=300.0,
                featured=True
            ),
            Course(
                title="الإحصاء والاحتمالات",
                slug="statistics-probability",
                short_desc="أساسيات الإحصاء والاحتمالات للثانوية",
                content="دورة متكاملة في الإحصاء والاحتمالات مع التطبيقات العملية وتحليل البيانات",
                price=180.0,
                featured=False
            ),
            Course(
                title="مراجعة شاملة للثانوية",
                slug="comprehensive-secondary-review",
                short_desc="مراجعة شاملة لجميع مواضيع الرياضيات الثانوية",
                content="دورة مراجعة شاملة تغطي جميع المواضيع الرئيسية مع امتحانات تجريبية ونصائح للنجاح",
                price=350.0,
                featured=True
            )
        ]
        
        for course in sample_courses:
            db.session.add(course)
        
        # Add sample testimonials
        sample_testimonials = [
            Testimonial(
                student_name="أحمد محمد",
                content="الأستاذ فضل عادل مدرس رياضة ممتاز، شرحه واضح ومفهوم. استفدت كثيراً من دورة أساسيات الرياضة",
                rating=5,
                course_id=1
            ),
            Testimonial(
                student_name="فاطمة علي",
                content="أفضل مدرس رياضة قابلته. طريقة الشرح مميزة والتمارين واضحة وممتعة",
                rating=5,
                course_id=2
            ),
            Testimonial(
                student_name="محمد حسن",
                content="دورة الرياضة الشاملة كانت رائعة. الأستاذ فضل يبسط المعلومات بطريقة ممتازة والأنشطة متنوعة",
                rating=5,
                course_id=3
            )
        ]
        
        for testimonial in sample_testimonials:
            db.session.add(testimonial)
        
        db.session.commit()

@app.route('/admin/clear-courses')
def admin_clear_courses():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    try:
        num_rows_deleted = db.session.query(Course).delete()
        db.session.commit()
        flash(f'Successfully deleted {num_rows_deleted} courses.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting courses: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# Context processor for current year
@app.context_processor
def inject_current_year():
    return {'current_year': 2024}

# Front pages
@app.route('/')
def index():
    featured_courses = Course.query.filter_by(featured=True).limit(3).all()
    testimonials = Testimonial.query.limit(3).all()
    return render_template('index.html', featured_courses=featured_courses, testimonials=testimonials)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/courses')
def courses():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('courses.html', courses=courses)

@app.route('/course/<slug>')
def course_detail(slug):
    course = Course.query.filter_by(slug=slug).first_or_404()
    return render_template('course_detail.html', course=course)

@app.route('/course/<slug>/subscribe', methods=['POST'])
@login_required
def subscribe_course(slug):
    course = Course.query.filter_by(slug=slug).first_or_404()
    if course in current_user.courses:
        flash('أنت مسجل بالفعل في هذه الدورة', 'info')
    else:
        current_user.courses.append(course)
        db.session.commit()
        flash('تم التسجيل في الدورة بنجاح', 'success')
    return redirect(url_for('course_detail', slug=slug))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(name=form.name.data, email=form.email.data, message=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash('تم إرسال الرسالة بنجاح، سنتواصل معك قريباً', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

# Student registration
from flask_login import login_user

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = StudentRegistrationForm()
    form.course.choices = [(c.id, c.title) for c in Course.query.order_by(Course.title).all()]
    if form.validate_on_submit():
        existing_student = Student.query.filter_by(email=form.email.data).first()
        if existing_student:
            flash('البريد الإلكتروني مستخدم بالفعل', 'danger')
            return render_template('register.html', form=form)
        
        filename = None
        file = request.files.get('profile_picture')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        hashed_password = generate_password_hash(form.password.data)
        student = Student(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            city=form.city.data,
            password_hash=hashed_password,
            profile_picture=filename
        )
        db.session.add(student)
        
        # Add course enrollment
        course = Course.query.get(form.course.data)
        if course:
            student.courses.append(course)
        
        db.session.commit()
        login_user(student)  # Log the student in immediately after registration
        flash('تم التسجيل بنجاح! تم تسجيل دخولك تلقائياً', 'success')
        return redirect(url_for('student_dashboard'))
    return render_template('register.html', form=form)

# Student login
@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if current_user.is_authenticated:
        return redirect(url_for('student_dashboard'))
    form = StudentLoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(email=form.email.data).first()
        if student and check_password_hash(student.password_hash, form.password.data):
            if not student.active:
                flash('الحساب غير مفعل، يرجى التواصل مع الإدارة', 'danger')
                return render_template('student_login.html', form=form)
            login_user(student, remember=form.remember.data)
            flash(f'أهلاً وسهلاً {student.name}', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('student_dashboard'))
        flash('بيانات تسجيل الدخول غير صحيحة', 'danger')
    return render_template('student_login.html', form=form)

# Student logout
@app.route('/student/logout')
def student_logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('index'))

# Student dashboard
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    return render_template('student_dashboard.html', student=current_user)

@app.route('/admin/delete-all-users')
def admin_delete_all_users():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    try:
        num_deleted = Student.query.delete()
        db.session.commit()
        flash(f'تم حذف {num_deleted} مستخدم بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء الحذف: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

# Admin authentication
def is_logged_in():
    return session.get('logged_in')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == app.config['ADMIN_USER'] and form.password.data == app.config['ADMIN_PASS']:
            session['logged_in'] = True
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('بيانات تسجيل الدخول غير صحيحة', 'danger')
    return render_template('admin_login.html', form=form)

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    flash('تم تسجيل الخروج', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    stats = {
        'total_students': Student.query.count(),
        'total_courses': Course.query.count(),
        'new_messages': ContactMessage.query.count()
    }
    courses = Course.query.order_by(Course.created_at.desc()).all()
    
    return render_template('admin_dashboard.html', 
                         stats=stats,
                         courses=courses)

@app.route('/admin/course/<int:course_id>')
def admin_course_detail(course_id):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    course = Course.query.get_or_404(course_id)
    return render_template('admin_course_detail.html', course=course)

@app.route('/admin/course/<int:course_id>/videos', methods=['GET', 'POST'])
def admin_course_videos(course_id):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    course = Course.query.get_or_404(course_id)
    form = VideoForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        video = Video(
            title=form.title.data,
            file_path=filename,
            timestamps=form.timestamps.data,
            course_id=course.id
        )
        db.session.add(video)
        db.session.commit()
        flash('تم إضافة الفيديو بنجاح', 'success')
        return redirect(url_for('admin_course_videos', course_id=course.id))
    
    videos = course.videos.order_by(Video.created_at.desc()).all()
    return render_template('admin_course_videos.html', course=course, videos=videos, form=form)

@app.route('/admin/course/<int:course_id>/video/<int:video_id>/delete', methods=['POST'])
def admin_delete_video(course_id, video_id):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    video = Video.query.get_or_404(video_id)
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], video.file_path))
    except Exception as e:
        flash(f'لم يتمكن من حذف الملف: {e}', 'warning')

    db.session.delete(video)
    db.session.commit()
    flash('تم حذف الفيديو بنجاح', 'success')
    return redirect(url_for('admin_course_videos', course_id=course_id))

@app.route('/admin/course/<int:course_id>/exams', methods=['GET', 'POST'])
def admin_course_exams(course_id):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    course = Course.query.get_or_404(course_id)
    form = ExamForm()
    if form.validate_on_submit():
        try:
            scheduled_date = None
            if form.scheduled_date.data:
                scheduled_date = datetime.strptime(form.scheduled_date.data, '%Y-%m-%d %H:%M')
            
            exam = Exam(
                title=form.title.data,
                description=form.description.data,
                questions=form.questions.data,
                scheduled_date=scheduled_date,
                exam_type=form.exam_type.data,
                course_id=course.id
            )
            db.session.add(exam)
            db.session.commit()
            flash('تم إضافة الامتحان بنجاح', 'success')
        except Exception as e:
            flash(f'حدث خطأ: {e}', 'danger')
        
        return redirect(url_for('admin_course_exams', course_id=course.id))
    
    exams = course.exams.order_by(Exam.created_at.desc()).all()
    return render_template('admin_course_exams.html', course=course, exams=exams, form=form)


# Admin: manage courses
@app.route('/admin/courses')
def admin_courses():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('courses.html', courses=courses)

@app.route('/admin/course/new', methods=['GET', 'POST'])
def admin_new_course():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    form = CourseForm()
    if form.validate_on_submit():
        filename = None
        file = request.files.get('image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        course = Course(
            title=form.title.data,
            slug=form.slug.data,
            short_desc=form.short_desc.data,
            content=form.content.data,
            price=form.price.data or 0.0,
            image=filename,
            featured=form.featured.data
        )
        db.session.add(course)
        db.session.commit()
        flash('تم إضافة الدورة بنجاح', 'success')
        return redirect(url_for('admin_courses'))
    return render_template('course_form.html', form=form, title="إضافة دورة جديدة")

@app.route('/admin/course/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit_course(id):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    course = Course.query.get_or_404(id)
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        filename = course.image
        file = request.files.get('image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        course.title = form.title.data
        course.slug = form.slug.data
        course.short_desc = form.short_desc.data
        course.content = form.content.data
        course.price = form.price.data or 0.0
        course.image = filename
        course.featured = form.featured.data
        
        db.session.commit()
        flash('تم تحديث الدورة بنجاح', 'success')
        return redirect(url_for('admin_courses'))
    return render_template('course_form.html', form=form, course=course, title="تعديل الدورة")

@app.route('/admin/course/delete/<int:id>')
def admin_delete_course(id):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    course = Course.query.get_or_404(id)
    if course.image:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], course.image))
        except Exception:
            pass
    db.session.delete(course)
    db.session.commit()
    flash('تم حذف الدورة', 'info')
    return redirect(url_for('admin_courses'))

# Admin: manage students
@app.route('/admin/students')
def admin_students():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    search = request.args.get('search', '')
    query = Student.query
    if search:
        query = query.filter((Student.name.contains(search)) | (Student.email.contains(search)))
    students = query.order_by(Student.name).all()
    return render_template('admin_students.html', students=students, search=search)

@app.route('/admin/student/toggle_active/<int:id>')
def admin_toggle_student_active(id):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    student = Student.query.get_or_404(id)
    student.active = not student.active
    db.session.commit()
    flash('تم تحديث حالة الطالب', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/student/delete/<int:id>')
def admin_delete_student(id):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    student = Student.query.get_or_404(id)
    if student.profile_picture:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], student.profile_picture))
        except Exception:
            pass
    db.session.delete(student)
    db.session.commit()
    flash('تم حذف الطالب', 'info')
    return redirect(url_for('admin_students'))

@app.route('/admin/students/export')
def admin_export_students():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    students = Student.query.all()
    
    # Create a string buffer for CSV data
    si = StringIO()
    cw = csv.writer(si)
    
    # Write headers
    cw.writerow(['ID', 'Name', 'Email', 'Phone', 'Active', 'Registered At'])
    
    # Write student data
    for student in students:
        cw.writerow([
            student.id,
            student.name,
            student.email,
            student.phone,
            'Yes' if student.active else 'No',
            student.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=students.csv"
    output.headers["Content-type"] = "text/csv"
    return output

# Admin: manage messages
@app.route('/admin/messages')
def admin_messages():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin_messages.html', messages=messages)

@app.route('/admin/stats')
def admin_stats():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    student_count = Student.query.count()
    course_count = Course.query.count()
    message_count = ContactMessage.query.count()
    
    return render_template('admin_stats.html', 
                         student_count=student_count, 
                         course_count=course_count, 
                         message_count=message_count)

# Admin: manage testimonials
@app.route('/admin/testimonials')
def admin_testimonials():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template('admin_testimonials.html', testimonials=testimonials)

@app.route('/admin/testimonial/new', methods=['GET', 'POST'])
def admin_new_testimonial():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    form = TestimonialForm()
    form.course_id.choices = [(0, 'عام')] + [(c.id, c.title) for c in Course.query.order_by(Course.title).all()]
    if form.validate_on_submit():
        testimonial = Testimonial(
            student_name=form.student_name.data,
            content=form.content.data,
            rating=form.rating.data,
            course_id=form.course_id.data if form.course_id.data != 0 else None
        )
        db.session.add(testimonial)
        db.session.commit()
        flash('تم إضافة المراجعة بنجاح', 'success')
        return redirect(url_for('admin_testimonials'))
    return render_template('admin_testimonial_form.html', form=form, title="إضافة مراجعة جديدة")

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)