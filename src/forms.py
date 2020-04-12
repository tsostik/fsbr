from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField, SelectField, RadioField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Optional, Length


class AddPlayer(FlaskForm):
    lastname = StringField('Фамилия', validators=[InputRequired(message='Фамилия должна быть заполнена')])
    firstname = StringField('Имя', validators=[InputRequired(message='Имя должна быть заполнено')])
    fathername = StringField('Отчество', validators=[Optional()])
    sex = RadioField('Пол', choices=[('1', 'Мужчина'), ('0', 'Женщина')], default=1)
    city = SelectField('Город')
    birthdate = DateField('Дата рождения',
                          format='%Y/%m/%d',
                          render_kw={'placeholder': 'ГГГГ/ММ/ДД'},
                          validators=[Optional()])
    is_sputnik = BooleanField('Спутник')
    sputnik_first = DateField('Первый турнир',
                              format='%Y/%m/%d',
                              render_kw={'placeholder': 'ГГГГ/ММ/ДД'},
                              validators=[Optional()])
    notes = TextAreaField('Примечания', render_kw={'placeholder': 'Любые примечания, например город, ' +
                                                                  'если его нет в списке'},
                          validators=[Length(max=255, message='Максимальная длина примечания не более 255 символов')])
    submit = SubmitField('Получить ID')
    pass
