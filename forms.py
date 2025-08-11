from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectMultipleField, URLField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, URL, ValidationError
from wtforms.widgets import CheckboxInput, ListWidget
from models import User, Tag

class LoginForm(FlaskForm):
    username = StringField('Nome de usuário', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar de mim')

class RegisterForm(FlaskForm):
    username = StringField('Nome de usuário', validators=[DataRequired(), Length(min=3, max=64)])
    name = StringField('Nome completo', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar senha', validators=[DataRequired(), EqualTo('password')])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Nome de usuário já existe. Escolha outro.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email já cadastrado. Use outro email.')

class ProfileForm(FlaskForm):
    name = StringField('Nome completo', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    bio = TextAreaField('Biografia', validators=[Optional(), Length(max=500)])
    profile_image = FileField('Foto do perfil', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Apenas imagens são permitidas!')
    ])

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class ProjectForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Descrição', validators=[DataRequired(), Length(min=10, max=500)])
    content = TextAreaField('Conteúdo detalhado', validators=[Optional()])
    image = FileField('Imagem do projeto', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Apenas imagens são permitidas!')
    ])
    demo_url = URLField('URL da demonstração', validators=[Optional(), URL()])
    github_url = URLField('URL do GitHub', validators=[Optional(), URL()])
    tags = MultiCheckboxField('Tags', coerce=int)
    is_published = BooleanField('Publicar projeto')
    is_featured = BooleanField('Projeto em destaque')
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.tags.choices = [(tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()]

class TagForm(FlaskForm):
    name = StringField('Nome da tag', validators=[DataRequired(), Length(min=2, max=50)])
    color = StringField('Cor (hex)', validators=[DataRequired(), Length(min=7, max=7)])

class CommentForm(FlaskForm):
    content = TextAreaField('Comentário', validators=[DataRequired(), Length(min=5, max=1000)])
