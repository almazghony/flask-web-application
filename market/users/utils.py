
from market import  mail
from flask_mail import Message
from PIL import Image
from flask import current_app, session
import secrets
import io
import os
from flask import  url_for, flash
from market.models import User
from market.users.forms import LoginForm, ResetForm, ChangePasswordForm
from market.items.routes import remove_item






def send_mail(user):
    token = user.get_token()  # Assuming you have a get_token method in your User model
    msg = Message('Password Reset Request', 
                  recipients=[user.email_address], 
                  sender='yousefzmarket@gmail.com')
    msg.body = f"""
    To reset your password, please click the following link:

    { url_for('users.reset_token', token=token, _external=True)}

    If you did not make this request, please ignore this email.
    """
    mail.send(msg)





def save_profile_picture(form_picture):
    try:
        random_hex = secrets.token_hex(8)
        _, f_extension = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_extension
        picture_path = os.path.join(current_app.root_path, 'static', 'profile_pics', picture_fn)

        # Open the image
        i = Image.open(form_picture)

        # Resize and compress the image
        output_size = (500, 500)
        i.thumbnail(output_size)

        # Save the image with compression
        with io.BytesIO() as output:
            i.save(output, format='JPEG', quality=85)  # Adjust quality for better compression
            output.seek(0)
            i.save(picture_path, 'JPEG')

        return picture_fn
    except Exception as e:
        print(f"Error saving profile picture: {e}")
        return None






def send_verification_email(email):
    
    token = User.generate_verification_token(email)
    verification_link = url_for('users.verify_email', token=token, _external=True)

    msg = Message('Verify Your Email', 
                  recipients=[email], 
                  sender='yousefzmarket@gmail.com')
    msg.body = f"""
    To verify your email, please click the following link:
    
    {verification_link}

    If you did not register, please ignore this email.
    """
    try:
        mail.send(msg)
    except Exception as e:
        flash(f"Failed to send email: {e}", 'danger')  # Log the error

