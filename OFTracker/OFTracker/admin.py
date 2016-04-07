from flask_admin import expose, Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from sqlalchemy import func
from flask import url_for

class OFModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

class OFAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return super(OFAdminIndexView, self).index()

class EventView(OFModelView):
    can_delete = False
    can_create = False

class IncentiveView(OFModelView):
    list_template = 'incentive_list.html'
    column_list = ('name', 'cutoff_time', 'status', 'amount')
    column_labels = dict(status='Incentive met', amount='Target amount')
    column_editable_list = ['status']
    column_filters = ['status']

class DonationView(OFModelView):
    can_create = False
    can_delete = False
    column_exclude_list = ['hash', 'full_name', 'country', 'email', 'incentive_id', 'ipn_id', 'ipn']
    column_filters = ['status']
    column_editable_list = ['status', 'incentive']
    column_choices = {
        'status': [
            ('0', 'Cancelled'),
            ('1', 'Pending'),
            ('2', 'Paid'),
            ('3', 'Read')
        ]
    }
    form_choices = {
        'status': [
            ('0', 'Cancelled'),
            ('1', 'Pending'),
            ('2', 'Paid'),
            ('3', 'Read')
        ]
    }
    column_formatters = dict(amount=lambda v, c, m, p: round(m.amount/100.0,2))

    