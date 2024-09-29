from market import db
from market import bcrypt
from flask import current_app
from market import login_manager
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)
    email_address = db.Column(db.String(length=64), nullable=False, unique=True)
    password_hash = db.Column(db.String(), nullable=False)
    mobile_number1 = db.Column(db.String(11), nullable=False)
    mobile_number2 = db.Column(db.String(11))
    image_file = db.Column(db.String(20))
    state = db.Column(db.String(), default='لم يكتب شيئا بعد')
    items = db.relationship('Item', backref='owned_user', lazy=True)
    is_verified = db.Column(db.Boolean, default=False)  # Add this line

    @staticmethod
    def generate_verification_token(email):
        serial = Serializer(current_app.config['SECRET_KEY'])
        return serial.dumps({'email': email}, salt=current_app.config['SECURITY_PASSWORD_SALT'])
    
    @staticmethod
    def verify_email_token(token, expires_sec=3600):
        serial = Serializer(current_app.config['SECRET_KEY'])
        try:
            email = serial.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expires_sec)['email']
        except Exception as e:
            print("THE ERROR IS ", e)
            return None
        return email


    def get_token(self):
        # Create a serializer with the secret key and expiration time
        serial = Serializer(current_app.config['SECRET_KEY'])
        
        # Return the token. No need to call decode here because dumps returns a string in URLSafeTimedSerializer
        return serial.dumps({'user_id': self.id}, salt=current_app.config['SECURITY_PASSWORD_SALT'])


    
    @staticmethod
    def verify_token(token, expires_sec=300):
        # Create a serializer with the secret key
        serial = Serializer(current_app.config['SECRET_KEY'])
        
        try:
            # Try to load the token and extract the user_id
            user_id = serial.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expires_sec)['user_id']
        except Exception as e:
            print("THE ERROR IS ", e)
            return None
        return User.query.get(user_id)
    
    
    @property
    def password(self):
        return self.password_hash
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password(self, attempt_password):
        return bcrypt.check_password_hash(self.password, attempt_password)
    
    
    def can_remove(self, item_obj):
        return item_obj in self.items

    def update_info(self, update_form):
            self.name = update_form.name.data
            self.email_address = update_form.email_address.data
            self.mobile_number1 = update_form.mobile_number1.data
            self.mobile_number2 = update_form.mobile_number2.data
            self.state = update_form.state.data
            db.session.commit()


    def remove(self):
        db.session.delete(self)
        db.session.commit()




class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    type = db.Column(db.String(length=12), nullable=False)
    description = db.Column(db.String(length=1024), nullable=False)
    location = db.Column(db.String(), nullable=False)
    delivery = db.Column(db.String(), nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    images = db.relationship('Picture', backref='rel_item', lazy=True)

    def __repr__(self):
        return self.id
    

    def buy(self, current_user):
        self.owner = current_user.id
        current_user.budget -= self.price
        db.session.commit()


    def remove(self):
        db.session.delete(self)
        db.session.commit()
        
    def update_info(self, update_form):
        self.name = update_form.name.data
        self.price = update_form.price.data
        self.type = update_form.type.data
        self.description = update_form.description.data
        self.location = update_form.location.data
        db.session.commit()



class Picture(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    image_name = db.Column(db.String())
    product = db.Column(db.Integer(), db.ForeignKey('item.id'))