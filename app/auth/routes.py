import random
import string
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from app import db, mail
from app.models import User

auth_bp = Blueprint('auth', __name__)

# ── Helpers ──────────────────────────────
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(user, otp):
    msg = Message(
        subject='BMS - Your OTP for Login',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email]
    )
    msg.body = f"""
Hello {user.full_name},

Your OTP for BMS login is: {otp}

This OTP is valid for 5 minutes.
Do not share it with anyone.

Regards,
Banking Management System
"""
    mail.send(msg)


# ── Register ─────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('accounts.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email     = request.form.get('email')
        phone     = request.form.get('phone')
        password  = request.form.get('password')
        confirm   = request.form.get('confirm_password')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(phone=phone).first():
            flash('Phone number already registered.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(full_name=full_name, email=email, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# ── Login ─────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('accounts.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        user     = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('Your account has been deactivated. Contact support.', 'danger')
            return redirect(url_for('auth.login'))

        # Generate and store OTP
        otp             = generate_otp()
        user.otp        = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        db.session.commit()

        # Send OTP
        try:
            send_otp_email(user, otp)
            flash(f'OTP sent to {user.email}', 'info')
        except Exception as e:
            print(f'Mail error: {e}')
            flash(f'(Dev mode) Your OTP is: {otp}', 'info')

        session['pre_auth_user_id'] = user.id
        return redirect(url_for('auth.verify_otp'))

    return render_template('auth/login.html')


# ── Verify OTP ────────────────────────────
@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    user_id = session.get('pre_auth_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)

    if request.method == 'POST':
        entered_otp = request.form.get('otp')

        if datetime.utcnow() > user.otp_expiry:
            flash('OTP has expired. Please login again.', 'danger')
            session.pop('pre_auth_user_id', None)
            return redirect(url_for('auth.login'))

        if entered_otp != user.otp:
            flash('Invalid OTP. Try again.', 'danger')
            return redirect(url_for('auth.verify_otp'))

        # Clear OTP after successful verification
        user.otp        = None
        user.otp_expiry = None
        db.session.commit()

        login_user(user)
        session.pop('pre_auth_user_id', None)
        flash(f'Welcome back, {user.full_name}!', 'success')

        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'staff':
            return redirect(url_for('admin.manage_users'))
        else:
            return redirect(url_for('accounts.dashboard'))

    return render_template('auth/otp.html', email=user.email)


# ── Logout ────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))