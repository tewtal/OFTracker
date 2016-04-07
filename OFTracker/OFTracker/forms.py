from flask_wtf import Form
from wtforms import SelectField, SelectMultipleField, TextAreaField, StringField, validators, ValidationError, DecimalField

class DonateForm(Form):
    amount = DecimalField(u'Donation Amount', [validators.Required()])
    name = StringField(u'Name', [validators.Required()])
    incentive = SelectField(u'Donation Incentive', [validators.Required()], choices=(), coerce=int)
    comment = TextAreaField(u'Donation Comment', description=u'Enter your donation comment here, keep in mind that offensive comments will not be read on stream')

