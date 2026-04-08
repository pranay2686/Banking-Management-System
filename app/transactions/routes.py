from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Account, Transaction

transactions_bp = Blueprint('transactions', __name__)


# ── Deposit ───────────────────────────────
@transactions_bp.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()

    if request.method == 'POST':
        account_id = int(request.form.get('account_id'))
        amount     = float(request.form.get('amount'))
        account    = Account.query.get_or_404(account_id)

        if account.user_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('transactions.deposit'))

        if amount <= 0:
            flash('Amount must be greater than 0.', 'danger')
            return redirect(url_for('transactions.deposit'))

        account.balance += amount

        txn = Transaction(
            transaction_type = 'deposit',
            amount           = amount,
            balance_after    = account.balance,
            description      = request.form.get('description', 'Deposit'),
            account_id       = account.id
        )
        db.session.add(txn)
        db.session.commit()

        flash(f'₹{amount:.2f} deposited successfully!', 'success')
        return redirect(url_for('accounts.account_detail', account_id=account.id))

    return render_template('transactions/deposit.html', accounts=accounts)


# ── Withdraw ──────────────────────────────
@transactions_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()

    if request.method == 'POST':
        account_id = int(request.form.get('account_id'))
        amount     = float(request.form.get('amount'))
        account    = Account.query.get_or_404(account_id)

        if account.user_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('transactions.withdraw'))

        if amount <= 0:
            flash('Amount must be greater than 0.', 'danger')
            return redirect(url_for('transactions.withdraw'))

        if account.balance < amount:
            flash('Insufficient balance.', 'danger')
            return redirect(url_for('transactions.withdraw'))

        account.balance -= amount

        txn = Transaction(
            transaction_type = 'withdrawal',
            amount           = amount,
            balance_after    = account.balance,
            description      = request.form.get('description', 'Withdrawal'),
            account_id       = account.id
        )
        db.session.add(txn)
        db.session.commit()

        flash(f'₹{amount:.2f} withdrawn successfully!', 'success')
        return redirect(url_for('accounts.account_detail', account_id=account.id))

    return render_template('transactions/withdraw.html', accounts=accounts)


# ── Transfer ──────────────────────────────
@transactions_bp.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()

    if request.method == 'POST':
        from_account_id    = int(request.form.get('from_account_id'))
        target_acc_number  = request.form.get('target_account_number').strip()
        amount             = float(request.form.get('amount'))

        from_account = Account.query.get_or_404(from_account_id)
        to_account   = Account.query.filter_by(account_number=target_acc_number, is_active=True).first()

        if from_account.user_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('transactions.transfer'))

        if not to_account:
            flash('Target account not found or inactive.', 'danger')
            return redirect(url_for('transactions.transfer'))

        if from_account.id == to_account.id:
            flash('Cannot transfer to the same account.', 'danger')
            return redirect(url_for('transactions.transfer'))

        if amount <= 0:
            flash('Amount must be greater than 0.', 'danger')
            return redirect(url_for('transactions.transfer'))

        if from_account.balance < amount:
            flash('Insufficient balance.', 'danger')
            return redirect(url_for('transactions.transfer'))

        # Debit sender
        from_account.balance -= amount
        debit_txn = Transaction(
            transaction_type  = 'transfer',
            amount            = amount,
            balance_after     = from_account.balance,
            description       = f'Transfer to {to_account.account_number}',
            account_id        = from_account.id,
            target_account_id = to_account.id
        )

        # Credit receiver
        to_account.balance += amount
        credit_txn = Transaction(
            transaction_type  = 'transfer',
            amount            = amount,
            balance_after     = to_account.balance,
            description       = f'Transfer from {from_account.account_number}',
            account_id        = to_account.id,
            target_account_id = from_account.id
        )

        db.session.add_all([debit_txn, credit_txn])
        db.session.commit()

        flash(f'₹{amount:.2f} transferred to {to_account.account_number} successfully!', 'success')
        return redirect(url_for('accounts.account_detail', account_id=from_account.id))

    return render_template('transactions/transfer.html', accounts=accounts)


# ── History ───────────────────────────────
@transactions_bp.route('/history')
@login_required
def history():
    # Gather all account IDs belonging to the user
    user_account_ids = [a.id for a in Account.query.filter_by(user_id=current_user.id).all()]

    transactions = Transaction.query\
        .filter(Transaction.account_id.in_(user_account_ids))\
        .order_by(Transaction.created_at.desc())\
        .limit(50).all()

    return render_template('transactions/history.html', transactions=transactions)