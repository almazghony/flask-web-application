from flask import Blueprint, current_app
from market import db
from PIL import Image
import secrets
import shutil
import io
import os
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, Picture
from market.items.forms import PostForm





items = Blueprint('items', __name__)


@items.route('/categories', methods=['GET'])
def categories_redirect():
    # Redirect to the market page with no category selected
    return redirect(url_for('items.market_page'))


@items.route('/market', methods=['GET'])
def market_page():
    post_form = PostForm()
    
    # Get the category from query params
    category = request.args.get('category')
    price_range = request.args.get('priceRange')
    location = request.args.get('location')
    delivery = request.args.get('delivery')
    
    # Base query - if no category, render the default category page
    if not category:
        return render_template('market.html', type=None)

    # Base query filtered by category
    query = Item.query.filter_by(type=category)

    # Price filtering
    if price_range:
        if price_range == '1':
            query = query.filter(Item.price < 50)
        elif price_range == '2':
            query = query.filter(Item.price.between(50, 100))
        elif price_range == '3':
            query = query.filter(Item.price > 100)

    # Location filtering
    if location:
        query = query.filter(Item.location.ilike(f"%{location}%"))

    # Delivery filtering
    if delivery:
        query = query.filter(Item.delivery == delivery)

    # Fetching the items for the selected category
    market_items = query.all()
    
    return render_template('market.html',
                           market_items=market_items,
                           post_form=post_form,
                           type=category)







def add_item_picture(form_picture, item_name, item_id):
    random_hex = secrets.token_hex(8)  
    _, f_extension = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_extension
    directory_path = os.path.join(current_app.root_path, 'static', 'image_pics', str(item_id))
    
    # Create the directory if it doesn't exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    picture_path = os.path.join(directory_path, picture_fn)

    # Open the image
    i = Image.open(form_picture)

    # Resize and compress the image
    output_size = (800, 800)  # Adjust size as needed
    i.thumbnail(output_size)

    # Save the image with compression
    with io.BytesIO() as output:
        i.save(output, format='JPEG', quality=85)  # Adjust quality for better compression
        output.seek(0)
        i.save(picture_path, 'JPEG')

    return picture_fn




@items.route('/remove_image/<int:image_id>', methods=['POST'])
def remove_image(image_id):
    # Fetch the image from the database using image_id
    picture = Picture.query.get(image_id)

    if picture:
        # Construct the path to the image file
        image_name = picture.image_name
        product_id = str(picture.product)
        directory_path = os.path.join(current_app.root_path, 'static', 'image_pics', product_id)
        file_path = os.path.join(directory_path, image_name)

        # Attempt to remove the file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                flash("File deleted successfully.", 'success')
            else:
                flash(f"File does not exist: {file_path}", 'warning')
        except Exception as e:
            flash(f"Error occurred while deleting file: {e}", 'error')

        # Remove the image record from the database
        try:
            db.session.delete(picture)
            db.session.commit()
            flash('Image removed successfully!', 'success')
        except Exception as e:
            flash(f"Error occurred while removing image from database: {e}", 'error')
            db.session.rollback()  # Rollback the transaction on error
    else:
        flash('Image not found!', 'error')

    # Redirect back to the referring page
    return redirect(request.referrer or url_for('default_route'))


@items.route('/remove_item/<int:item_id>', methods=['POST'])
def remove_item(item_id):
    # Fetch the item from the database using item_id
    product = Item.query.get(item_id)
    
    if product:
        try:
            # Path to the directory associated with the item
            directory_path = os.path.join(current_app.root_path, 'static', 'image_pics', str(item_id))
            
            # Check if the directory exists before attempting to delete it
            if os.path.exists(directory_path):
                shutil.rmtree(directory_path)

            # Attempt to remove the item from the database
            db.session.delete(product)  # Use db.session.delete to remove the item
            db.session.commit()          # Commit the changes to the database
            flash(f"Item successfully removed.", 'success')

        except Exception as e:
            # Handle any exceptions during the removal process
            db.session.rollback()  # Rollback the transaction if an error occurs
            flash(f"An error occurred while removing the item: {str(e)}", 'danger')

    else:
        flash("Item not found.", 'warning')

    # Redirect back to the referring page
    return redirect(request.referrer or url_for('default_route'))

