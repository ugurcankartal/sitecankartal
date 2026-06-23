# Personal Portfolio Backend (Flask — Legacy)

> **Deprecated:** Production now uses Django in `../backend/`.  
> This folder is kept for reference and migration scripts only.

Flask backend API for personal portfolio website with MySQL database.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Configuration

Make sure MySQL is running and the database exists:

```sql
CREATE DATABASE IF NOT EXISTS personal_portfolio;
```

The database configuration is in `config.py`:
- Host: 127.0.0.1
- Port: 3306
- Database: personal_portfolio
- User: root
- Password: Dirilen*1998

### 3. Initialize Database

Run the initialization script to create tables and populate with sample data:

```bash
python init_db.py
```

### 4. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Profile
- `GET /api/profile` - Get profile information
- `POST /api/profile` - Create/Update profile

### Timeline
- `GET /api/timeline` - Get all timeline entries
- `POST /api/timeline` - Create timeline entry
- `PUT /api/timeline/<id>` - Update timeline entry
- `DELETE /api/timeline/<id>` - Delete timeline entry

### Skills
- `GET /api/skills` - Get all skills
- `POST /api/skills` - Create skill

### Projects
- `GET /api/projects` - Get all projects
- `GET /api/projects/<id>` - Get single project
- `POST /api/projects` - Create project

### Blog
- `GET /api/blog` - Get all blog posts (supports pagination)
- `GET /api/blog?featured=true` - Get featured posts only
- `GET /api/blog/<id>` - Get single blog post
- `POST /api/blog` - Create blog post

### Contact
- `POST /api/contact` - Submit contact form
- `GET /api/contact/messages` - Get all contact messages (admin)

### Health Check
- `GET /api/health` - Health check endpoint

## Database Schema

- **profiles** - Profile information
- **social_links** - Social media links
- **timeline** - Work experience timeline
- **skills** - Skills with proficiency levels
- **projects** - Portfolio projects
- **blog_posts** - Blog posts
- **contact_messages** - Contact form submissions

## Development

The application runs in debug mode by default. For production, set `FLASK_ENV=production` and configure a proper secret key.
