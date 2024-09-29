from flask import session, render_template, redirect, url_for, flash, request, Blueprint, current_app
from market import db
import os
from market.models import Item, User, Picture
from market.users.forms import RegisterForm, LoginForm, RemoveForm, UpdateForm, ResetForm, ChangePasswordForm
from market.items.forms import PostForm, RemoveForm, UpdateItem
from flask_login import login_user, logout_user, login_required, current_user
from wtforms.validators import ValidationError
# from market import cache
from market.users.utils import send_mail, send_verification_email
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from market.items.routes import add_item_picture, remove_item
from market.users.utils import save_profile_picture

users = Blueprint('users', __name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]  # Set rate limits globally
)


@users.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        # Store user data temporarily in the session (or use another temp storage)
        session['new_user_data'] = {
            'name': form.name.data,
            'email_address': form.email_address.data,
            'mobile_number1': form.mobile_number1.data,
            'mobile_number2': form.mobile_number2.data,
            'password': form.password1.data  # Store the plain password temporarily
        }
        
        # Send verification email

        return redirect(url_for('users.resend_verification'))

    if form.errors:
        for error in form.errors.values():
            flash(error, category='danger')
    
    return render_template('register.html', form=form)



@users.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login_page():
    change_password_form = ChangePasswordForm()
    reset_form = ResetForm()
    form = LoginForm()  # Ensure the form is initialized here

    if request.method == 'POST':
        if 'login' in request.form and form.validate_on_submit():
            user = User.query.filter_by(email_address=form.email_address.data).first()
            
            # Check if user exists
            if user is None:
                flash('This username is not registered.', category='danger')
                return redirect(url_for('users.login_page'))

            # Validate password
            if user.check_password(form.password.data):
                login_user(user)
                flash(f'Success! Welcome {user.name}', category='success')
                return redirect(url_for('items.categories_redirect'))  # Redirect to a suitable page after login
            else:
                flash('Invalid password!', category='danger')
                return redirect(url_for('users.login_page'))

    # Handle GET request
    return render_template('login.html', form=form, change_password_form=change_password_form, reset_form=reset_form)



@users.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    return redirect(url_for('items.categories_redirect'))


@users.route('/account', methods=['POST', 'GET'])
@login_required
# @cache.cached(timeout=300)
def profile_page():
    post_form = PostForm()
    remove_form = RemoveForm()
    update_form = UpdateForm(
        name=current_user.name,
        email_address=current_user.email_address,
        mobile_number1=current_user.mobile_number1,
        mobile_number2=current_user.mobile_number2,
        state=current_user.state)

    update_item = UpdateItem()
    owned_items = Item.query.filter_by(owner=current_user.id)

    if request.method == 'POST':
        # Handle item removal
        if 'removed_item' in request.form and remove_form.validate_on_submit():
            removed_item = request.form.get('removed_item')
            item_obj = Item.query.filter_by(id=removed_item).first()
            if item_obj:
                if current_user.can_remove(item_obj):
                    item_obj.remove()
                    flash('تم حذف العنصر بنجاح', category='success')
                else:
                    flash('يمكن لصاحب العنصر فقط حذفه', category='danger')
            else:
                flash('لم يتم العثور على العنصر', category='danger')
            return redirect(url_for('users.profile_page'))  # Redirect after handling removal

        # Handle item posting
        if 'posted_item' in request.form and post_form.validate_on_submit():
            
            if post_form.errors:
                for error in post_form.errors.values():
                    flash(f"{error}", category='danger')
            else:
                new_item = Item(
                    name=post_form.name.data,
                    price=post_form.price.data,
                    location=post_form.location.data,
                    description=post_form.description.data,
                    type=post_form.type.data,
                    delivery=post_form.delivery.data,
                    owner=current_user.id
                )
                db.session.add(new_item)
                db.session.commit()
                flash("تم اضافة العنصر بنجاح", category='success')
                try:
                    files = request.files.getlist('picture')
                    for file in files:
                        image_name = add_item_picture(file, new_item.name, new_item.id)
                        new_pic = Picture(image_name=image_name,
                                        product=new_item.id)
                        db.session.add(new_pic)
                        db.session.commit()
                except Exception as e:
                    flash(f"Error saving picture {e}") 

            return redirect(url_for('users.profile_page'))  # Redirect after posting an item

        # Handle user update
        if 'updated_user' in request.form and update_form.validate_on_submit():
            if update_form.picture.data:
                if current_user.image_file:
                    user_image = current_user.image_file
                    image_path = os.path.join(current_app.root_path, 'static', 'profile_pics', user_image)
                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        print("File deleted successfully.")
                except Exception as e:
                    print(f"Error: {e}")

                picture_file = save_profile_picture(update_form.picture.data)
                current_user.image_file = picture_file
            try:
                current_user.update_info(update_form)
                db.session.commit()  # Ensure you commit after updating
                flash('تم تحديث البيانات بنجاح', category='success')
                return redirect(url_for('users.profile_page'))  # Redirect after updating
            except ValidationError as e:
                flash(str(e), category='danger')  # Show specific validation errors
            except Exception as e:
                flash(f"Unknown Error occurred: {str(e)}", category='danger')

        if 'updated_item' in request.form and update_item.validate_on_submit():
            try:
                # Retrieve the current item from the form
                current_item = request.form.get('updated_item')
                item_obj = Item.query.get(current_item)

                # Update item details
                item_obj.update_info(update_item)

                # Commit the update to the database
                db.session.commit()
                flash('تم تحديث البيانات بنجاح', category='success')

                # Handle file uploads for images
                files = request.files.getlist('images')
                if files:  # Ensure that files are present
                    for file in files:
                        # Save the new image and associate it with the item
                        image_name = add_item_picture(file, item_obj.name, item_obj.id)
                        new_pic = Picture(image_name=image_name, product=item_obj.id)
                        db.session.add(new_pic)

                    # Commit the images to the database
                    db.session.commit()
                else:
                    flash('No images were uploaded.', category='warning')

                # Redirect to the profile page after the update
                return redirect(url_for('users.profile_page'))

            except ValidationError as e:
                # Catch form validation errors
                flash(str(e), category='danger')
            except Exception as e:
                # Catch any other errors and flash them
                flash(f"Unknown Error occurred: {str(e)}", category='danger')


    # Handle GET requests
    return render_template(
        'account.html',
        owned_items=owned_items,
        post_form=post_form,
        remove_form=remove_form,
        update_form=update_form,
        update_item=update_item
    )




@users.route('/owner/<int:owner_id>', methods=['POST', 'GET'])
def owner_profile(owner_id):
    owner = User.query.get_or_404(owner_id)
    remove_form = RemoveForm()
    update_item = UpdateItem()
    
    if request.method == 'POST':
        # Check for the updated item form submission
        if 'updated_item' in request.form and update_item.validate_on_submit():
            try:
                # Retrieve the current item ID from the form
                current_item_id = request.form.get('updated_item')
                item_obj = Item.query.get(current_item_id)

                if item_obj is None:
                    flash('Item not found.', category='danger')
                    return redirect(url_for('users.owner_profile', owner_id=owner_id))

                # Update item details using the form data
                item_obj.update_info(update_item)

                # Handle file uploads for images
                files = request.files.getlist('images')
                if files:  # Ensure that files are present
                    for file in files:
                        # Save the new image and associate it with the item
                        image_name = add_item_picture(file, item_obj.name, item_obj.id)
                        new_pic = Picture(image_name=image_name, product=item_obj.id)
                        db.session.add(new_pic)

                # Commit the update to the database
                db.session.commit()
                flash('تم تحديث البيانات بنجاح', category='success')
            except ValidationError as e:
                # Catch form validation errors
                flash(str(e), category='danger')
            except Exception as e:
                # Catch any other errors and flash them
                flash(f"Unknown error occurred: {str(e)}", category='danger')

            # Redirect to the profile page after the update
            return redirect(url_for('users.owner_profile', owner_id=owner_id))

    # For GET requests, render the profile page
    return render_template('owner.html', update_item=update_item, remove_form=remove_form, owner=owner)


@users.route('/verify_email/<token>')
def verify_email(token):
    email = User.verify_email_token(token)  # Use the email verification method
    if not email:
        flash('The verification link is invalid or has expired.', category='danger')
        
        # Clear the session before redirecting
        session.pop('new_user_data', None)
        return redirect(url_for('users.register_page'))

    # Ensure the session has the correct user data
    if 'new_user_data' not in session or session['new_user_data']['email_address'] != email:
        flash('Something went wrong. Please register again.', category='danger')
        
        # Clear the session before redirecting
        session.pop('new_user_data', None)
        return redirect(url_for('users.register_page'))

    # Create the user now that the email is verified
    new_user_data = session.pop('new_user_data')  # Remove the data from session after use
    new_user = User(
        name=new_user_data['name'],
        email_address=new_user_data['email_address'],
        mobile_number1=new_user_data['mobile_number1'],
        mobile_number2=new_user_data['mobile_number2'],
        password=new_user_data['password'],
        is_verified=True
    )
    
    db.session.add(new_user)
    db.session.commit()

    flash('Email verified successfully! You can now log in.', category='success')
    return redirect(url_for('users.login_page'))



@users.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    reset_form = ResetForm()
    form = LoginForm()  # Initialize your form
    change_password_form = ChangePasswordForm()
    if reset_form.validate_on_submit():
        user = User.query.filter_by(email_address=reset_form.email_address.data).first()
        if user:
            send_mail(user)
            flash('Check your email for a password reset link!', category='success')
            return redirect(url_for('users.login_page'))
        else:
            flash('Email does not exist.', category='danger')
    return render_template('login.html', reset_form=reset_form, form=form, change_password_form=change_password_form)



@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_token(token)  # Assuming you have a verify_token method in your User model
    if not user:
        flash('That is an invalid or expired token. Please try again.', 'danger')
        return redirect(url_for('users.login_page'))

    change_password_form = ChangePasswordForm()  # Initialize the change password form
    if change_password_form.validate_on_submit():
        user.password = change_password_form.new_password.data  # Hash the password if necessary
        db.session.commit()
        flash('Your password has been updated! Please log in.', 'success')
        return "sucess! please login with the new password."
    
    return render_template('change_password.html', change_password_form=change_password_form)


@users.route('/remove_user/<int:user_id>', methods=['POST'])
def remove_user(user_id):
    user = User.query.get(user_id)

    if user:
        if user.image_file:
            user_image = user.image_file
            image_path = os.path.join(current_app.root_path, 'static', 'profile_pics', user_image)
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print("File deleted successfully.")
            except Exception as e:
                print(f"Error: {e}")
        
        if user.items:
            for item in user.items:
                try:
                    item_id = int(item.id) 
                    remove_item(item_id)  
                except Exception as e:
                    print(f"Error removing item with ID {item.id}: {e}")
        user.remove()
        flash(f" User successfully removed.", 'success') 

        
    return redirect(url_for('users.register_page'))



@users.route('/resend_verification', methods=['GET', 'POST'])
def resend_verification():
    # Get the email from the session
    new_user_data = session.get('new_user_data')
    if new_user_data:
        email = new_user_data['email_address']
        user = User.query.filter_by(email_address=email).first()
        if user:
            flash('User not found or already verified.', category='danger')
        
        else:
            send_verification_email(email)
            flash('A new verification email has been sent!', category='success')
    else:
        flash('No pending registration found.', category='danger')

    return render_template('verification.html')