from .encryption import encryption as encrypt
from flask import Flask, render_template, request, redirect, session, flash, url_for, Blueprint
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_mail import Mail, Message
from ..db import db

ebp = Blueprint('EmailAuthentication', __name__, url_prefix='/')

#app = current_app._get_current_object()



def send_email(email=None):
    if email is not None:
        token = encrypt.generate_confirmation_token(email)
    confirm_url = url_for('EmailAuthentication.confirm_email', token=token, _external=True)
    # html = render_template('user/activate.html', confirm_url=confirm_url)
    html = render_template('activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    sending_mail_to_mail_server(email, subject, html)


def sending_mail_to_mail_server(to, subject, template):
    mail_server = Mail(current_app)
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    mail_server.send(msg)
    # with app.app_context():
    #     mail_server = Mail(app)
    #     msg = Message(
    #         subject,
    #         recipients=[to],
    #         html=template,
    #         sender=current_app.config['MAIL_DEFAULT_SENDER']
    #     )
    #     mail_server.send(msg)
    return 'Mail Sent'


@ebp.route('/<token>/confirm_email', methods=['GET', 'POST'])
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    db_obj = db.get_db()
    if db_obj.is_connected():
        cursor = db_obj.cursor()

    query_string = "SELECT user_email, user_enabled, user_email_verified FROM users WHERE user_email = %s"
    cursor.execute(query_string, (email,))
    data = cursor.fetchall()
    if len(data) >= 1:
        user_val = data[0]
        email_from_db, enabled , email_verified =  user_val[0].lower(), user_val[1], user_val[2]
    else:
        return 'Email id doesn\'t match in our records'

    if email.lower() == email_from_db and enabled == 0 and email_verified == 'NO':
        update_users = "UPDATE users set user_enabled=1, user_email_verified = 'YES' WHERE user_email = %s"
        cursor.execute(update_users, (email_from_db,))
        db_obj.commit()
    else:
        return 'Email already Authenticated.. Please try to login'

    db_obj.close()
    # user = User.query.filter_by(email=email).first_or_404()
    # if user.confirmed:
    #    flash('Account already confirmed. Please login.', 'success')
    # else:
    #    user.confirmed = True
    #    user.confirmed_on = datetime.datetime.now()
    #    db.session.add(user)
    #    db.session.commit()
    #    flash('You have confirmed your account. Thanks!', 'success')
    return 'Your Email ID has been verified...Thank You !!!'


@ebp.route('/confirm_token/<token>')
def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email
