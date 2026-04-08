from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Loan, Account

loans_bp = Blueprint('loans', __name__)


# ── Apply for Loan ────────────────────────
@loans_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()

    if not accounts:
        flash('You need an active account to apply for a loan.', 'warning')
        return redirect(url_for('accounts.dashboard'))

    if request.method == 'POST':
        loan_type     = request.form.get('loan_type')
        amount        = float(request.form.get('amount'))
        tenure_months = int(request.form.get('tenure_months'))
        account_id    = int(request.form.get('account_id'))
        reason        = request.form.get('reason', '')

        account = Account.query.get_or_404(account_id)

        if account.user_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('loans.apply'))

        if amount <= 0:
            flash('Loan amount must be greater than 0.', 'danger')
            return redirect(url_for('loans.apply'))

        loan = Loan(
            loan_type     = loan_type,
            amount        = amount,
            interest_rate = 8.5,
            tenure_months = tenure_months,
            reason        = reason,
            user_id       = current_user.id,
            account_id    = account_id,
        )
        loan.emi = loan.calculate_emi()

        db.session.add(loan)
        db.session.commit()

        flash(f'Loan application submitted! EMI will be ₹{loan.emi}/month.', 'success')
        return redirect(url_for('loans.status'))

    return render_template('loans/apply.html', accounts=accounts)


# ── Loan Status ───────────────────────────
@loans_bp.route('/status')
@login_required
def status():
    loans = Loan.query.filter_by(user_id=current_user.id)\
                .order_by(Loan.applied_at.desc()).all()
    return render_template('loans/status.html', loans=loans)