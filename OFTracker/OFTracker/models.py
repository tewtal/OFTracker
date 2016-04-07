from datetime import datetime
import time
from OFTracker import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import hashlib

class User(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id', db.Integer, primary_key = True)
    username = db.Column('username', db.String(255), unique=True, index=True)
    password = db.Column('password', db.String(255))
    email = db.Column('email', db.String(255), unique=True, index=True)
    flags = db.Column('flags', db.String(50))
    registered_on = db.Column('registered_on', db.DateTime)
    
    def __init__(self, username = None, password = None, email = None):
        self.username = username
        self.set_password(password)
        self.email = email
        self.flags = ""
        self.registered_on = datetime.utcnow()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return unicode(self.id)
    
    def is_admin(self):
        return 'A' in self.flags

    def __repr__(self):
        return '<User %r>' % (self.username)

class Event(db.Model):
    __tablename__ = "events"
    id = db.Column('event_id', db.Integer, primary_key = True)
    name = db.Column('name', db.String(255))
    description = db.Column('description', db.Text())
    amount = db.Column('target', db.Integer)
    paypal_email = db.Column('paypal_email', db.String(255))
    paypal_sandbox = db.Column('paypal_sandbox', db.Boolean())

    def __init__(self):
        pass

    def paypal_url(self):
        if self.paypal_sandbox == True:
            return "https://www.sandbox.paypal.com/cgi-bin/webscr"
        else:
            return "https://www.paypal.com/cgi-bin/webscr"

    def donations(self):
        sum_int = Donation.query.with_entities(func.sum(Donation.amount)).filter(Donation.status > 1).scalar()
        sum = "0.00"
        if sum_int:
            sum = "%.2f" % (float(sum_int) / 100)
        return sum

class Donation(db.Model):
    __tablename__ = "donations"
    id = db.Column('donation_id', db.Integer, primary_key = True)
    hash = db.Column('hash', db.String(255), unique=True, index=True)
    name = db.Column('name', db.String(255))
    full_name = db.Column('first_name', db.String(255))
    country = db.Column('country', db.String(255))
    email = db.Column('email', db.String(255))
    comment = db.Column('comment', db.Text())
    amount = db.Column('amount', db.Integer)
    status = db.Column('status', db.Integer, index=True)
    incentive_id = db.Column(db.Integer, db.ForeignKey('incentives.incentive_id'))
    ipn_id = db.Column(db.Integer, db.ForeignKey('ipns.ipn_id'))
    ipn = db.relationship('IPN', backref='donation')

    def __init__(self, name = None, email = None, comment = None, amount = 0, incentive = 0):
        self.name = name
        self.email = email
        self.comment = comment
        self.amount = int(amount * 100)
        self.status = 1
        self.hash = hashlib.sha1(self.name + self.email + self.comment + str(self.amount) + str(time.time())).hexdigest()
        self.incentive_id = incentive
        self.full_name = ''
        self.country = ''

    def __repr__(self):
        return '%r ($%r)' % (self.name, round(self.amount/100.0,2))

class Incentive(db.Model):
    __tablename__ = "incentives"
    id = db.Column('incentive_id', db.Integer, primary_key = True)
    name = db.Column('name', db.String(255))
    amount = db.Column('amount', db.Integer)
    cutoff_time = db.Column('cutoff_time', db.DateTime)
    status = db.Column('status', db.Boolean())
    donations = db.relationship('Donation', backref='incentive', lazy='dynamic')

    def __init__(self, name = None, amount = 0, cutoff_time = None):
        self.name = name
        self.amount = int(amount * 100)
        self.cutoff_time = cutoff_time
        self.status = 0

    def __repr__(self):
        return '%s' % (self.name)

    def donated(self):
        donated_int = Donation.query.with_entities(func.sum(Donation.amount)).filter(Donation.incentive_id == self.id).scalar()
        if donated_int: 
            return "%.2f" % (float(donated_int)/100.0)
        else:
            return "0.00"


class IPN(db.Model):
    __tablename__ = "ipns"
    id = db.Column('ipn_id', db.Integer, primary_key = True)
    
    verification_status = db.Column('verification_status', db.String(50))
    payment_date = db.Column('payment_date', db.DateTime)
    payment_status = db.Column('payment_status', db.String(50))
    address_status = db.Column('address_status', db.String(50))
    payer_status = db.Column('payer_status', db.String(50))

    first_name = db.Column('first_name', db.String(255))
    last_name = db.Column('last_name', db.String(255))
    payer_email = db.Column('payer_email', db.String(255))
    payer_id = db.Column('payer_id', db.String(255))
    address_country = db.Column('address_country', db.String(100))

    business = db.Column('business', db.String(255))
    receiver_email = db.Column('receiver_email', db.String(255))
    receiver_id = db.Column('receiver_id', db.String(255))

    mc_currency = db.Column('mc_currency', db.String(10))
    mc_fee = db.Column('mc_fee', db.String(20))
    mc_gross = db.Column('mc_gross', db.String(20))

    txn_type = db.Column('txn_type', db.String(20))
    txn_id = db.Column('txn_id', db.String(20))

    custom = db.Column('custom', db.String(255))

    def __init__(self):
        pass

    def __repr__(self):
        return '%r' % (self.payer_email)
