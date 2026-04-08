from app import create_app, db
from app.models import User

app = create_app('development')
with app.app_context():
    # Find your existing account and make it admin
    user = User.query.filter_by(email='pranayvardhansambangi@gmail.com').first()
    if user:
        user.role = 'admin'
        db.session.commit()
        print(f'Success! {user.email} is now admin!')
    else:
        print('User not found!')