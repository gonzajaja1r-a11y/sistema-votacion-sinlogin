# ================================
# forms.py - Formularios 
# ================================
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError
from models import Usuario, Administrador

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    def validate_email(self, email):
        """Validar que el email termine en @itel.edu.ar"""
        if not email.data.endswith('@itel.edu.ar'):
            raise ValidationError('El email debe terminar en @itel.edu.ar')

class AdminLoginForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])

class CandidatoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    partido = StringField('Partido Político', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')