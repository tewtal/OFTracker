from flask import Flask, g, url_for, redirect, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager, current_user

class OFModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
        
app = Flask(__name__)
app.debug = True
app.config.from_object("OFTracker.settings")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

import OFTracker.models
import OFTracker.auth
import OFTracker.views

admin = Admin(app, name='OFTracker', template_mode='bootstrap3')
admin.add_view(OFModelView(OFTracker.models.User, db.session))
admin.add_view(OFModelView(OFTracker.models.Incentive, db.session))
admin.add_view(OFModelView(OFTracker.models.Donation, db.session))
admin.add_view(OFModelView(OFTracker.models.IPN, db.session))

@login_manager.user_loader
def load_user(id):
    return OFTracker.models.User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user