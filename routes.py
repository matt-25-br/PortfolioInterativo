import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
from sqlalchemy import or_
from app import db, csrf
from models import User, Project, Tag, Comment, Like, Notification
from forms import LoginForm, RegisterForm, ProfileForm, ProjectForm, TagForm, CommentForm
from utils import save_image, create_notification

# Main blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get featured projects
    featured_projects = Project.query.filter_by(is_published=True, is_featured=True)\
                                   .order_by(Project.created_at.desc()).limit(3).all()
    
    # Get recent projects
    recent_projects = Project.query.filter_by(is_published=True)\
                                 .order_by(Project.created_at.desc()).limit(6).all()
    
    # Get all tags for filtering
    tags = Tag.query.order_by(Tag.name).all()
    
    return render_template('index.html', 
                         featured_projects=featured_projects,
                         recent_projects=recent_projects,
                         tags=tags)

@main_bp.route('/about')
def about():
    owner = User.query.filter_by(is_owner=True).first()
    return render_template('about.html', owner=owner)

@main_bp.route('/projects')
def projects():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    tag_filter = request.args.get('tag', '', type=str)
    
    query = Project.query.filter_by(is_published=True)
    
    # Apply search filter
    if search:
        query = query.filter(or_(
            Project.title.contains(search),
            Project.description.contains(search)
        ))
    
    # Apply tag filter
    if tag_filter:
        tag = Tag.query.filter_by(name=tag_filter).first()
        if tag:
            query = query.filter(Project.tags.contains(tag))
    
    projects = query.order_by(Project.created_at.desc())\
                   .paginate(page=page, per_page=9, error_out=False)
    
    tags = Tag.query.order_by(Tag.name).all()
    
    return render_template('projects.html', 
                         projects=projects, 
                         tags=tags,
                         search=search,
                         current_tag=tag_filter)

@main_bp.route('/project/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    
    if not project.is_published and (not current_user.is_authenticated or not current_user.is_owner):
        abort(404)
    
    comments = Comment.query.filter_by(project_id=id).order_by(Comment.created_at.desc()).all()
    comment_form = CommentForm()
    
    return render_template('project_detail.html', 
                         project=project, 
                         comments=comments,
                         comment_form=comment_form)

@main_bp.route('/project/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    project = Project.query.get_or_404(id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment()
        comment.content = form.content.data
        comment.user_id = current_user.id
        comment.project_id = project.id
        db.session.add(comment)
        
        # Create notification for owner
        if not current_user.is_owner:
            create_notification(
                project.author.id,
                f"Novo comentário de {current_user.name} no projeto '{project.title}'"
            )
        
        db.session.commit()
        flash('Comentário adicionado com sucesso!', 'success')
    
    return redirect(url_for('main.project_detail', id=id))

@main_bp.route('/project/<int:id>/like', methods=['POST'])
@csrf.exempt
@login_required
def toggle_like(id):
    project = Project.query.get_or_404(id)
    like = Like.query.filter_by(user_id=current_user.id, project_id=project.id).first()
    
    if like:
        db.session.delete(like)
        liked = False
    else:
        like = Like()
        like.user_id = current_user.id
        like.project_id = project.id
        db.session.add(like)
        liked = True
        
        # Create notification for owner (if not self-like)
        if not current_user.is_owner:
            create_notification(
                project.author.id,
                f"{current_user.name} curtiu o projeto '{project.title}'"
            )
    
    db.session.commit()
    
    return jsonify({
        'liked': liked,
        'like_count': project.like_count
    })

# Authentication blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            
            if user.is_owner:
                return redirect(next_page) if next_page else redirect(url_for('owner.dashboard'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('main.index'))
        
        flash('Nome de usuário ou senha inválidos.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
@csrf.exempt
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.name = form.name.data
        user.email = form.email.data
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        
        if form.profile_image.data:
            filename = save_image(form.profile_image.data, 'profiles')
            current_user.profile_image = filename
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', form=form, edit_mode=True)

# Owner blueprint
owner_bp = Blueprint('owner', __name__)

@owner_bp.before_request
def require_owner():
    if not current_user.is_authenticated or not current_user.is_owner:
        abort(403)

@owner_bp.route('/dashboard')
def dashboard():
    total_projects = Project.query.count()
    published_projects = Project.query.filter_by(is_published=True).count()
    total_likes = Like.query.count()
    total_comments = Comment.query.count()
    
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False)\
                                            .order_by(Notification.created_at.desc()).limit(10).all()
    
    return render_template('owner/dashboard.html',
                         total_projects=total_projects,
                         published_projects=published_projects,
                         total_likes=total_likes,
                         total_comments=total_comments,
                         recent_projects=recent_projects,
                         notifications=unread_notifications)

@owner_bp.route('/projects')
def project_list():
    page = request.args.get('page', 1, type=int)
    projects = Project.query.order_by(Project.created_at.desc())\
                          .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('owner/project_list.html', projects=projects)

@owner_bp.route('/project/new', methods=['GET', 'POST'])
def new_project():
    form = ProjectForm()
    
    if form.validate_on_submit():
        project = Project()
        project.title = form.title.data
        project.description = form.description.data
        project.content = form.content.data
        project.demo_url = form.demo_url.data
        project.github_url = form.github_url.data
        project.is_published = form.is_published.data
        project.is_featured = form.is_featured.data
        project.user_id = current_user.id
        
        if form.image.data:
            filename = save_image(form.image.data, 'projects')
            project.image_filename = filename
        
        # Add tags
        selected_tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
        project.tags.extend(selected_tags)
        
        db.session.add(project)
        db.session.commit()
        
        flash('Projeto criado com sucesso!', 'success')
        return redirect(url_for('owner.project_list'))
    
    return render_template('owner/project_form.html', form=form, title='Novo Projeto')

@owner_bp.route('/project/<int:id>/edit', methods=['GET', 'POST'])
def edit_project(id):
    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.content = form.content.data
        project.demo_url = form.demo_url.data
        project.github_url = form.github_url.data
        project.is_published = form.is_published.data
        project.is_featured = form.is_featured.data
        
        if form.image.data:
            filename = save_image(form.image.data, 'projects')
            project.image_filename = filename
        
        # Update tags
        project.tags.clear()
        selected_tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
        project.tags.extend(selected_tags)
        
        db.session.commit()
        
        flash('Projeto atualizado com sucesso!', 'success')
        return redirect(url_for('owner.project_list'))
    
    # Pre-populate tags
    form.tags.data = [tag.id for tag in project.tags]
    
    return render_template('owner/project_form.html', form=form, title='Editar Projeto', project=project)

@owner_bp.route('/project/<int:id>/delete', methods=['POST'])
def delete_project(id):
    project = Project.query.get_or_404(id)
    
    # Delete image file if exists
    if project.image_filename:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'projects', project.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(project)
    db.session.commit()
    
    flash('Projeto excluído com sucesso!', 'success')
    return redirect(url_for('owner.project_list'))

@owner_bp.route('/tags')
def tag_list():
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('owner/tag_list.html', tags=tags)

@owner_bp.route('/tag/new', methods=['GET', 'POST'])
def new_tag():
    form = TagForm()
    
    if form.validate_on_submit():
        tag = Tag()
        tag.name = form.name.data
        tag.color = form.color.data
        db.session.add(tag)
        db.session.commit()
        
        flash('Tag criada com sucesso!', 'success')
        return redirect(url_for('owner.tag_list'))
    
    return render_template('owner/tag_form.html', form=form, title='Nova Tag')

@owner_bp.route('/notifications/mark-read')
def mark_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False)\
                     .update({'is_read': True})
    db.session.commit()
    
    return redirect(url_for('owner.dashboard'))
