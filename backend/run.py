from app import create_app, db
from app.models import User, Account, Transaction, Loan

app = create_app('development')

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Account': Account,
        'Transaction': Transaction,
        'Loan': Loan
    }

@app.cli.command('create-admin')
def create_admin():
    """Create a default admin user."""
    if User.query.filter_by(email='admin@bms.com').first():
        print('Admin already exists.')
        return
    admin = User(
        full_name = 'BMS Admin',
        email     = 'admin@bms.com',
        phone     = '9999999999',
        role      = 'admin'
    )
    admin.set_password('Admin@123')
    db.session.add(admin)
    db.session.commit()
    print('✅ Admin created: admin@bms.com / Admin@123')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)