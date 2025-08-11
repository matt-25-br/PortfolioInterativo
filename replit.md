# Portfolio Digital - Flask Web Application

## Overview

This is a personal portfolio web application built with Flask that allows users to showcase projects, interact with content through comments and likes, and manage portfolio content through an admin interface. The application features a clean, responsive design with Bootstrap and includes both public-facing portfolio pages and an owner dashboard for content management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework Architecture
- **Flask-based application** with modular blueprint structure
- **MVC pattern** implementation with separate models, routes, and templates
- **SQLAlchemy ORM** for database operations with declarative base model
- **Flask-Login** for user authentication and session management
- **Flask-WTF** for form handling and CSRF protection (auth endpoints exempt)

### Recent Changes (August 2025)
- **Database tables created** and admin user configured (admin/admin123)
- **CSRF token issues resolved** for authentication forms
- **Template errors fixed** including nl2br filter and JavaScript URL generation
- **System fully operational** with login, dashboard, and project management working

### Database Design
- **PostgreSQL** as the primary database (configurable via DATABASE_URL)
- **User model** with authentication, profile information, and role-based access (owner flag)
- **Project model** with rich content support, publication status, and featured flags
- **Tag system** with many-to-many relationships for project categorization
- **Social features** including Comment and Like models for user interaction
- **Notification system** for user engagement tracking

### Authentication & Authorization
- **Password hashing** using Werkzeug security utilities
- **Role-based access control** with owner privileges for admin features
- **Session-based authentication** with "remember me" functionality
- **CSRF protection** on all forms

### File Management
- **Image upload system** with PIL-based processing and resizing
- **Secure filename handling** with UUID generation
- **Organized upload structure** with separate folders for profiles and projects
- **File type validation** and size restrictions (16MB max)

### Frontend Architecture
- **Bootstrap 5** for responsive UI components
- **Font Awesome** for icons and visual elements
- **Custom CSS** with animations and hover effects
- **JavaScript enhancements** for interactive features (tooltips, image preview, form validation)
- **Jinja2 templating** with template inheritance and modular components

### Content Management
- **Owner dashboard** with statistics and content management tools
- **CRUD operations** for projects and tags with rich form validation
- **Draft/publish workflow** for content visibility control
- **Featured content** system for homepage highlights
- **Tag-based categorization** with color-coded visual system

## External Dependencies

### Core Framework Dependencies
- **Flask** - Main web framework
- **SQLAlchemy** - Database ORM and migration handling
- **Flask-Login** - User session management
- **Flask-WTF** - Form processing and CSRF protection
- **Werkzeug** - WSGI utilities and security helpers
- **Pillow (PIL)** - Image processing and manipulation

### Frontend Dependencies
- **Bootstrap 5** - CSS framework via CDN
- **Font Awesome 6** - Icon library via CDN
- **Custom CSS/JS** - Local static assets for enhanced functionality

### Database
- **PostgreSQL** - Primary database system (development default: localhost/portfolio)
- **Connection pooling** configured with pre-ping and recycling

### Infrastructure
- **ProxyFix middleware** for proper header handling in production
- **Environment-based configuration** for secrets and database URLs
- **Static file serving** for uploaded images and assets
- **Logging system** configured for debugging and monitoring