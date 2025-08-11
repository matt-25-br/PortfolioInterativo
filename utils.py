import os
import uuid
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename
from app import db
from models import Notification

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file, folder, max_size=(800, 600)):
    """Save uploaded image with resizing and unique filename"""
    if not allowed_file(file.filename):
        return None
    
    # Generate unique filename
    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
    
    # Create folder path
    folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Full file path
    file_path = os.path.join(folder_path, filename)
    
    # Open and resize image
    try:
        image = Image.open(file.stream)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Resize image while maintaining aspect ratio
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save image
        image.save(file_path, 'JPEG', quality=85, optimize=True)
        
        return filename
    except Exception as e:
        current_app.logger.error(f"Error saving image: {str(e)}")
        return None

def create_notification(user_id, message):
    """Create a new notification for a user"""
    notification = Notification(
        user_id=user_id,
        message=message
    )
    db.session.add(notification)
    return notification

def get_linkedin_share_url(project):
    """Generate LinkedIn share URL for a project"""
    base_url = "https://www.linkedin.com/sharing/share-offsite/"
    project_url = f"https://yourportfolio.com/project/{project.id}"  # Replace with actual domain
    
    params = {
        'url': project_url,
        'title': project.title,
        'summary': project.description
    }
    
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{query_string}"
