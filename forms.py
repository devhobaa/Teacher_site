from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, PasswordField, BooleanField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, NumberRange

class CourseForm(FlaskForm):
    title = StringField('عنوان الدورة', validators=[DataRequired(), Length(max=150)])
    slug = StringField('الرابط المختصر', validators=[DataRequired(), Length(max=160)])
    short_desc = StringField('وصف مختصر', validators=[Length(max=300)])
    content = TextAreaField('المحتوى الكامل')
    price = FloatField('السعر', validators=[Optional(), NumberRange(min=0)])
    image = FileField('صورة الدورة')
    featured = BooleanField('دورة مميزة')

class ContactForm(FlaskForm):
    name = StringField('الاسم', validators=[DataRequired()])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    message = TextAreaField('الرسالة', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])

class StudentRegistrationForm(FlaskForm):
    name = StringField('الاسم الكامل', validators=[DataRequired(), Length(max=120)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    phone = StringField('رقم الهاتف', validators=[Optional(), Length(max=20)])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), EqualTo('confirm', message='كلمات المرور غير متطابقة')])
    confirm = PasswordField('تأكيد كلمة المرور', validators=[DataRequired()])
    course = SelectField('الدورة المطلوبة', coerce=int, validators=[DataRequired()])
    city = StringField('المدينة', validators=[DataRequired(), Length(max=100)])
    profile_picture = FileField('الصورة الشخصية')

class StudentLoginForm(FlaskForm):
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    remember = BooleanField('تذكرني')

class TestimonialForm(FlaskForm):
    student_name = StringField('اسم الطالب', validators=[DataRequired(), Length(max=120)])
    content = TextAreaField('المراجعة', validators=[DataRequired()])
    rating = IntegerField('التقييم', validators=[DataRequired(), NumberRange(min=1, max=5)])
    course_id = SelectField('الدورة', coerce=int, validators=[Optional()])

class VideoForm(FlaskForm):
    title = StringField('عنوان الفيديو', validators=[DataRequired(), Length(max=150)])
    file = FileField('ملف الفيديو', validators=[DataRequired()])
    timestamps = TextAreaField('الطوابع الزمنية (JSON)', validators=[Optional()])

class ExamForm(FlaskForm):
    title = StringField('عنوان الامتحان', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('الوصف', validators=[Optional()])
    questions = TextAreaField('الأسئلة (JSON)', validators=[DataRequired()])
    scheduled_date = StringField('تاريخ ووقت الامتحان (YYYY-MM-DD HH:MM)', validators=[Optional()])
    exam_type = SelectField('نوع الامتحان', choices=[('monthly', 'شهري'), ('post_lecture', 'بعد المحاضرة')], validators=[DataRequired()])