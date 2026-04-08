import random
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Account, Transaction

accounts_bp = Blueprint('accounts', __name__)

def generate_account_number():
    return 'BMS' + str(random.randint(1000000000, 9999999999))


# ── Dashboard ─────────────────────────────
@accounts_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    accounts = Account.query.filter_by(
        user_id=current_user.id, is_active=True
    ).all()
    return render_template('accounts/dashboard.html', accounts=accounts)


# ── Create Account ────────────────────────
@accounts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_account():
    if request.method == 'POST':
        account_type    = request.form.get('account_type')
        initial_deposit = float(request.form.get('initial_deposit', 0))

        if initial_deposit < 500:
            flash('Minimum initial deposit is ₹500.', 'danger')
            return redirect(url_for('accounts.create_account'))

        # Generate unique account number
        acc_number = generate_account_number()
        while Account.query.filter_by(account_number=acc_number).first():
            acc_number = generate_account_number()

        account = Account(
            account_number = acc_number,
            account_type   = account_type,
            balance        = initial_deposit,
            user_id        = current_user.id
        )
        db.session.add(account)
        db.session.flush()

        # Record initial deposit as transaction
        txn = Transaction(
            transaction_type = 'deposit',
            amount           = initial_deposit,
            balance_after    = initial_deposit,
            description      = 'Initial deposit on account opening',
            account_id       = account.id
        )
        db.session.add(txn)
        db.session.commit()

        flash(f'Account {acc_number} created successfully!', 'success')
        return redirect(url_for('accounts.dashboard'))

    return render_template('accounts/create_account.html')


# ── Account Detail ────────────────────────
@accounts_bp.route('/<int:account_id>')
@login_required
def account_detail(account_id):
    account = Account.query.get_or_404(account_id)

    # Only owner, admin or staff can view
    if account.user_id != current_user.id and current_user.role not in ['admin', 'staff']:
        flash('Access denied.', 'danger')
        return redirect(url_for('accounts.dashboard'))

    transactions = Transaction.query.filter_by(account_id=account_id)\
                    .order_by(Transaction.created_at.desc()).limit(20).all()

    return render_template('accounts/account_detail.html',
                           account=account,
                           transactions=transactions)