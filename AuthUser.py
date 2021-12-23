import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import db
import mysql.connector
bp = Blueprint('AuthUser', __name__, url_prefix='/')
from .email import EmailAuthentication as mail
from flask import current_app
import hashlib


@bp.route('/registerUsers', methods=('GET', 'POST'))
def register_users():
    #import pdb;
    #pdb.set_trace()
    error = None
    if request.method == 'POST':
        fname = request.form['user_first_name']
        lname = request.form['user_last_name']
        email = request.form['user_email']
        phone = request.form['user_phone']
        passwd = request.form['user_pass']
        db_password = passwd + current_app.config['SECURITY_PASSWORD_SALT']
        encoded_pass = hashlib.md5(db_password.encode())
        encrypted_pass = encoded_pass.hexdigest()
        db_obj = db.get_db()
        if db_obj.is_connected():
            cursor = db_obj.cursor()
        if not fname:
            error = 'First Name is required.'
        elif not lname:
            error = 'Last Name is required.'
        elif not email:
            error = 'Email is Required'
        elif not phone:
            error = 'Phone is Required'

        insert_stmt = (
            "INSERT INTO users (user_first_name, user_last_name, user_passwd, user_email, user_phone)"

            " VALUES (%s, %s, %s, %s, %s)"
        )
        data = (fname, lname, encrypted_pass, email, phone)
        if error is None:
            try:
                cursor.execute(insert_stmt, data)
                db_obj.commit()
                mail.send_email(email)
                error = 'User Created... and verification email has been sent to your ' + str(email) + '  ID.\n\n'
                error += 'Please check your email..!!'
            except mysql.connector.IntegrityError as err:
                error = "User Creation Failed" + str(err)

        return error
    else:
        error = 'Use post method for registering the user.'
        return error


@bp.route('/')
@bp.route('/login', methods=['POST', 'GET'])
def login():
    status = True

    if request.method == 'POST':
        email = request.form["uemail"]
        pwd = request.form["upass"]
        salted_pwd = pwd + current_app.config['SECURITY_PASSWORD_SALT']
        db_obj = db.get_db()
        if db_obj.is_connected():
            cursor = db_obj.cursor()
        cursor.execute("select user_id, user_enabled, user_login_attempts, user_email_verified  from users where user_email=%s", (email, ))
        email_data = cursor.fetchone()
        account_locked = False
        email_verification = ''
        if email_data is None:
            data = None
            return 'Email Id is not correct..!!!'
        else:
            email_verification = email_data[3]
            if int(email_data[2]) >= 5:
                account_locked = True
            cursor.execute("select user_id, user_enabled, user_login_attempts, user_email_verified  from users where user_email=%s and user_passwd=md5(%s)", (email, salted_pwd))
            data = cursor.fetchone()
        if not account_locked:
            pass
        else:
            return 'Account Locked due to incorrect credentails ..!!'
        if email_verification == 'NO':
            return 'Your email verification is pending ..!!'
        if data is not None:
            id, enabled, attempts, verified = data[0], data[1], data[2], data[3]
            if verified == 'NO':
                return 'Your email verification is pending ..!!'
            if attempts >= 5:
                return 'Account is locked..!!'
            if enabled and verified == 'YES':
                update_str = "UPDATE users set user_last_login=sysdate(), user_login_attempts=0 WHERE user_email = %s and user_id = %s"
                cursor.execute(update_str, (email, id,))
                db_obj.commit()
                # session['logged_in'] = True
                # session['username'] = str(email)
                return 'Login Successfully' + ' for the user :' + email
        else:
            #if email_data is not None:

            update_str = "UPDATE users SET user_login_attempts  = user_login_attempts  + 1    WHERE user_email = %s and user_email_verified = %s"
            cursor.execute(update_str, (email, 'YES'))
            db_obj.commit()
            return 'Login authentication Failed...!! Please check your input...!!'

    return 'No Data.. Something Wrong...!!!'
