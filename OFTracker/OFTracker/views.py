from __future__ import print_function
import sys

from sqlalchemy import func
from datetime import datetime
from flask import Flask, session, request, flash, url_for, redirect, render_template, abort, g, jsonify
from OFTracker import app, db
from OFTracker.models import Donation, Incentive, IPN
from OFTracker.forms import DonateForm
from werkzeug.datastructures import ImmutableMultiDict
from dateutil import parser
import requests


def log(*objs):
    print("LOG: ", *objs, file=sys.stderr)

@app.route('/')
def index():
    incentives = Incentive.query.filter_by(status = 0).filter(Incentive.cutoff_time >= datetime.now()).order_by(Incentive.cutoff_time.asc()).limit(5).all()
    return render_template(
        'index.html',
        title='Index',
        sum=sum,
        incentives=incentives,
        event=g.event
    )

@app.route('/incentives')
def incentives():
    incentives = Incentive.query.filter(Incentive.id > 1).all()
    return render_template(
        'incentives.html',
        event=g.event,
        incentives=incentives
    )

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    form = DonateForm(request.form)
    incentives = [(1, 'No incentive')] + [(i.id, i.name) for i in Incentive.query.filter_by(status = 0).all()]
    form.incentive.choices = incentives

    if request.method == 'POST' and form.validate():
        donation = Donation(form.name.data, '', form.comment.data, form.amount.data, form.incentive.data)
        db.session.add(donation)
        db.session.commit()
        db.session.refresh(donation)

        # Redirect to paypal donation page
        form_data = {
            'business' : g.event.paypal_email,
            'cmd' : '_donations',
            'item_name' : g.event.name,
            'amount' : str(round(donation.amount/100.0, 2)),
            'currency_code' : 'USD',
            'return' : url_for('donated', _external=True),
            'notify_url' : url_for('ipn', _external=True),
            'custom' : donation.hash,
            'lc' : 'US'            
        }
        context = { 'form_data' : form_data, 'paypal_url' : g.event.paypal_url() }
        return render_template('donate_paypal.html', **context)
       
    context = { 'form' : form }
    return render_template(
        'donate.html',
        title='Donate',
        event=g.event,
        **context
    )

@app.route('/donated')
def donated():
    flash('Thank you for your donation!')
    return redirect(url_for('index'))

@app.route('/ipn', methods=['POST'])
def ipn():
    request_data = request.get_data()
    validate_url = "%s?cmd=_notify-validate&%s" % (g.event.paypal_url(), request_data)
    status = ''
    r = None
    try:
        r = requests.post(validate_url, timeout = 10)
    except:
        return('', 400)

    if r.status_code != 200:
        return('', 400)

    verification_status = r.text.encode('ascii','ignore')

    log(repr(request.form))

    # always create a IPN post, and if it is verified and complete, link it to a donation
    i = IPN()
    i.verification_status = verification_status
    try:
        i.payment_date = parser.parse(request.form['payment_date'][:33])
    except:
        i.payment_date = datetime.now()

    i.payment_status = request.form['payment_status']
    i.address_status = request.form['address_status']
    i.payer_status = request.form['payer_status']
    i.first_name = request.form['first_name']
    i.last_name = request.form['last_name']
    i.payer_email = request.form['payer_email']
    i.payer_id = request.form['payer_id']
    i.address_country = request.form['address_country']
    i.business = request.form['business']
    i.receiver_email = request.form['receiver_email']
    i.receiver_id = request.form['receiver_id']
    i.mc_currency = request.form['mc_currency']
    i.mc_fee = request.form['mc_fee']
    i.mc_gross = request.form['mc_gross']
    i.txn_type = request.form['txn_type']
    i.txn_id = request.form['txn_id']
    i.custom = request.form['custom']

    db.session.add(i)
    db.session.commit()
    db.session.refresh(i)

    if i.verification_status == "VERIFIED" and i.payment_status == "Completed":
        d = None
        try:
            d = Donation.query.filter_by(hash = i.custom).one()
        except:
            return('', 200)
        if d:
            i_gross = int(float(i.mc_gross)*100)            
            if i_gross == d.amount:
                d.status = 2
            else:
                d.status = 0

            d.ipn_id = i.id
            d.email = i.payer_email
            d.full_name = "%s %s" % (i.first_name, i.last_name)
            d.country = i.address_country
            db.session.add(d)
            db.session.commit()

    return('', 200)