from flask import Flask, g, url_for, redirect, request
from flask_admin import expose, Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager, current_user
        
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
from OFTracker.admin import OFAdminIndexView, OFModelView, EventView, DonationView, IncentiveView, AdminModelView

admin = Admin(app, url='/admin', name='OFTracker Administration', index_view=OFAdminIndexView(), template_mode='bootstrap3')
admin.add_view(DonationView(OFTracker.models.Donation, db.session))
admin.add_view(IncentiveView(OFTracker.models.Incentive, db.session))
admin.add_view(EventView(OFTracker.models.Event, db.session))
admin.add_view(AdminModelView(OFTracker.models.User, db.session))
admin.add_view(AdminModelView(OFTracker.models.IPN, db.session))


@login_manager.user_loader
def load_user(id):
    return OFTracker.models.User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    g.event = OFTracker.models.Event.query.get(1)
