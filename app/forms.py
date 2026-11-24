from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo
)


class RegistrationForm(FlaskForm):
    username = StringField(
        "Имя пользователя",
        validators=[
            DataRequired(),
            Length(min=3, max=80)
        ]
    )

    email = StringField(
        "Электронная почта",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ]
    )

    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )

    confirm_password = PasswordField(
        "Подтвердите пароль",
        validators=[
            DataRequired(),
            EqualTo("password", message="Пароли должны совпадать.")
        ]
    )

    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    email = StringField(
        "Электронная почта",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Войти")


class PostForm(FlaskForm):
    title = StringField(
        "Заголовок",
        validators=[
            DataRequired(),
            Length(min=3, max=200)
        ]
    )

    content = TextAreaField(
        "Содержание",
        validators=[
            DataRequired(),
            Length(min=10)
        ]
    )

    submit = SubmitField("Сохранить публикацию")