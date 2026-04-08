from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# ─────────────────────────────────────────
#  USER MODEL
# ─────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    phone         = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.Enum('admin', 'staff', 'customer'), default='customer')
    is_active     = db.Column(db.Boolean, default=True)
    otp           = db.Column(db.String(6), nullable=True)
    otp_expiry    = db.Column(db.DateTime, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    accounts      = db.relationship('Account', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email} [{self.role}]>'


# ─────────────────────────────────────────
#  ACCOUNT MODEL
# ─────────────────────────────────────────
class Account(db.Model):
    __tablename__ = 'accounts'

    id             = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    account_type   = db.Column(db.Enum('savings', 'current', 'fixed'), default='savings')
    balance        = db.Column(db.Float, default=0.0)
    is_active      = db.Column(db.Boolean, default=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Key
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    transactions   = db.relationship('Transaction', backref='account', lazy=True)

    def __repr__(self):
        return f'<Account {self.account_number} ₹{self.balance}>'


# ─────────────────────────────────────────
#  TRANSACTION MODEL
# ─────────────────────────────────────────
class Transaction(db.Model):
    __tablename__ = 'transactions'

    id                = db.Column(db.Integer, primary_key=True)
    transaction_type  = db.Column(db.Enum('deposit', 'withdrawal', 'transfer'), nullable=False)
    amount            = db.Column(db.Float, nullable=False)
    balance_after     = db.Column(db.Float, nullable=False)
    description       = db.Column(db.String(255), nullable=True)
    status            = db.Column(db.Enum('success', 'failed', 'pending'), default='success')
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Keys
    account_id        = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    target_account_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<Transaction {self.transaction_type} ₹{self.amount}>'


# ─────────────────────────────────────────
#  LOAN MODEL
# ─────────────────────────────────────────
class Loan(db.Model):
    __tablename__ = 'loans'

    id            = db.Column(db.Integer, primary_key=True)
    loan_type     = db.Column(db.Enum('personal', 'home', 'education', 'vehicle'), nullable=False)
    amount        = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, default=8.5)
    tenure_months = db.Column(db.Integer, nullable=False)
    emi           = db.Column(db.Float, nullable=True)
    status        = db.Column(db.Enum('pending', 'approved', 'rejected', 'closed'), default='pending')
    reason        = db.Column(db.String(255), nullable=True)
    applied_at    = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at   = db.Column(db.DateTime, nullable=True)

    # Foreign Keys
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id    = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)

    # Relationships
    user          = db.relationship('User', backref='loans')
    account       = db.relationship('Account', backref='loans')

    def calculate_emi(self):
        # EMI = P * r * (1+r)^n / ((1+r)^n - 1)
        r = (self.interest_rate / 100) / 12
        n = self.tenure_months
        if r == 0:
            return self.amount / n
        emi = self.amount * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
        return round(emi, 2)

    def __repr__(self):
        return f'<Loan {self.loan_type} ₹{self.amount} [{self.status}]>'