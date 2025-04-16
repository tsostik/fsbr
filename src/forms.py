from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField, SelectField, RadioField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Optional, Length
from wtforms.widgets import TextInput


#standard DateField widget is type="date" which is locale-dependent and 
#thus conflicts with the date format we want to use (YYYY/MM/DD)
# We need to override the widget to use a standard text input instead

class CustomDateField(DateField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d', **kwargs):
        super().__init__(label, validators, format=format, **kwargs)
        self.widget = TextInput()  # Render as a text input instead of type="date"


class AddPlayer(FlaskForm):
    lastname = StringField('Фамилия', validators=[InputRequired(message='Фамилия должна быть заполнена')])
    firstname = StringField('Имя', validators=[InputRequired(message='Имя должна быть заполнено')])
    fathername = StringField('Отчество', validators=[Optional()])
    sex = RadioField('Пол', choices=[('1', 'Мужчина'), ('0', 'Женщина')], default=1)
    city = SelectField('Город')
    birthdate = CustomDateField('Дата рождения',
                                format='%Y/%m/%d',
                                render_kw={'placeholder': 'ГГГГ/ММ/ДД'},
                                validators=[Optional()])
    is_sputnik = BooleanField('Спутник')
    sputnik_first = CustomDateField('Первый турнир',
                                    format='%Y/%m/%d',
                                    render_kw={'placeholder': 'ГГГГ/ММ/ДД'},
                                    validators=[Optional()])
    notes = TextAreaField('Примечания', render_kw={'placeholder': 'Любые примечания, например город, ' +
                                                                      'если его нет в списке'},
                          validators=[Length(max=255, message='Максимальная длина примечания не более 255 символов')])
    submit = SubmitField('Получить ID')
