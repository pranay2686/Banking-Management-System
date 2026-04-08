from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Account, Transaction, Loan

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to restrict access to admins only."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('accounts.dashboard'))
        return f(*args, **kwargs)
    return decorated


# ── Admin Dashboard ───────────────────────
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users        = User.query.count()
    total_accounts     = Account.query.count()
    total_transactions = Transaction.query.count()
    pending_loans      = Loan.query.filter_by(status='pending').count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_loans = Loan.query.order_by(Loan.applied_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
        total_users        = total_users,
        total_accounts     = total_accounts,
        total_transactions = total_transactions,
        pending_loans      = pending_loans,
        recent_users       = recent_users,
        recent_loans       = recent_loans
    )


# ── Manage Users ──────────────────────────
@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/manage_users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot deactivate another admin.', 'danger')
        return redirect(url_for('admin.manage_users'))
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.email} has been {status}.', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def change_role(user_id):
    user     = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role not in ['admin', 'staff', 'customer']:
        flash('Invalid role.', 'danger')
        return redirect(url_for('admin.manage_users'))
    user.role = new_role
    db.session.commit()
    flash(f'Role updated to {new_role} for {user.email}.', 'success')
    return redirect(url_for('admin.manage_users'))


# ── Manage Loans ──────────────────────────
@admin_bp.route('/loans')
@login_required
@admin_required
def manage_loans():
    loans = Loan.query.order_by(Loan.applied_at.desc()).all()
    return render_template('admin/manage_loans.html', loans=loans)


@admin_bp.route('/loans/<int:loan_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    if loan.status != 'pending':
        flash('Loan is not in pending state.', 'warning')
        return redirect(url_for('admin.manage_loans'))

    # Credit loan amount to the linked account
    account          = Account.query.get(loan.account_id)
    account.balance += loan.amount

    txn = Transaction(
        transaction_type = 'deposit',
        amount           = loan.amount,
        balance_after    = account.balance,
        description      = f'Loan disbursement - {loan.loan_type}',
        account_id       = account.id
    )

    loan.status      = 'approved'
    loan.approved_at = datetime.utcnow()

    db.session.add(txn)
    db.session.commit()

    flash(f'Loan #{loan_id} approved and ₹{loan.amount} credited to account.', 'success')
    return redirect(url_for('admin.manage_loans'))


@admin_bp.route('/loans/<int:loan_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    if loan.status != 'pending':
        flash('Loan is not in pending state.', 'warning')
        return redirect(url_for('admin.manage_loans'))

    loan.status = 'rejected'
    db.session.commit()

    flash(f'Loan #{loan_id} has been rejected.', 'info')
    return redirect(url_for('admin.manage_loans'))