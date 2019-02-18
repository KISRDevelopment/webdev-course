from flask_wtf import FlaskForm
from wtforms import StringField, FileField, validators, widgets, Field, HiddenField
from wtforms.fields.html5 import DateField
import re

vals = validators
range_regex = re.compile(r"^(?P<fromhour>\d{1,2})\s*(:\s*(?P<fromminute>\d{1,2}))?\s*(?P<fromampm>am|pm)?\s*\-\s*(?P<tohour>\d{1,2})\s*(:\s*(?P<tominute>\d{1,2}))?\s*(?P<toampm>am|pm)?$", flags=re.IGNORECASE)

range_validator = vals.Regexp(range_regex,
                                    message='Time range format is invalid. Examples of valid inputs are 11-1pm, 10:30am-11:00am, etc.')
class PresentationForm(FlaskForm):
    
    title = StringField('Title', validators=[vals.Length(min=4, message="Title has to be at least 4 characters long")])
    presenters = StringField('Presenter(s)', validators=[
        vals.Length(min=4, message="List of presenters has to be at least 4 alphabetical characters long"), 
        vals.Regexp(r'^[a-zA-Z\s&\-\.]+$', message="Only alphabetical characters are allowed in the presenters list")
    ])
    scheduled = DateField('Date', validators=[vals.DataRequired()])
    time_range = StringField('Time', validators=[vals.DataRequired(), range_validator])
    notes = StringField('Notes', widget=widgets.TextArea())
    attachments = FileField('Attachments')
    