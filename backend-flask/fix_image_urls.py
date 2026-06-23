"""
Migration script to fix image URLs in database
Converts localhost:5000 URLs to relative paths
"""
from app import app, db
from models import User, Profile, Project, BlogPost
from sqlalchemy import text

def fix_image_urls():
    """Fix all image URLs in database"""
    with app.app_context():
        try:
            print("=== Image URL Fix Script ===")
            print("")
            
            # Fix User profile_image_url
            print("1. Fixing User profile_image_url...")
            users = User.query.all()
            updated_users = 0
            for user in users:
                if user.profile_image_url:
                    original = user.profile_image_url
                    # If it contains localhost:5000, extract the path
                    if 'localhost:5000' in original or '127.0.0.1:5000' in original:
                        if '/static/' in original:
                            # Extract just the filename
                            filename = original.split('/static/uploads/profiles/')[-1]
                            user.profile_image_url = filename
                            updated_users += 1
                            print(f"   User {user.id}: {original} -> {filename}")
                    # If it's already a full path starting with /static, extract filename
                    elif original.startswith('/static/uploads/profiles/'):
                        filename = original.split('/static/uploads/profiles/')[-1]
                        user.profile_image_url = filename
                        updated_users += 1
                        print(f"   User {user.id}: {original} -> {filename}")
            db.session.commit()
            print(f"   ✓ Updated {updated_users} user(s)")
            print("")
            
            # Fix Profile profile_image_url
            print("2. Fixing Profile profile_image_url...")
            profiles = Profile.query.all()
            updated_profiles = 0
            for profile in profiles:
                if profile.profile_image_url:
                    original = profile.profile_image_url
                    if 'localhost:5000' in original or '127.0.0.1:5000' in original:
                        if '/static/' in original:
                            filename = original.split('/static/uploads/profiles/')[-1]
                            profile.profile_image_url = f"/static/uploads/profiles/{filename}"
                            updated_profiles += 1
                            print(f"   Profile {profile.id}: {original} -> /static/uploads/profiles/{filename}")
                    elif not original.startswith('/static/'):
                        # If it's just a filename, make it a full path
                        profile.profile_image_url = f"/static/uploads/profiles/{original}"
                        updated_profiles += 1
                        print(f"   Profile {profile.id}: {original} -> /static/uploads/profiles/{original}")
            db.session.commit()
            print(f"   ✓ Updated {updated_profiles} profile(s)")
            print("")
            
            # Fix Project image_url
            print("3. Fixing Project image_url...")
            projects = Project.query.all()
            updated_projects = 0
            for project in projects:
                if project.image_url:
                    original = project.image_url
                    if 'localhost:5000' in original or '127.0.0.1:5000' in original:
                        # Extract path part
                        if '/static/' in original:
                            path = '/' + original.split('/static/')[1]
                            project.image_url = path
                            updated_projects += 1
                            print(f"   Project {project.id}: {original} -> {path}")
                        else:
                            # Try to extract path
                            from urllib.parse import urlparse
                            parsed = urlparse(original)
                            if parsed.path:
                                project.image_url = parsed.path
                                updated_projects += 1
                                print(f"   Project {project.id}: {original} -> {parsed.path}")
            db.session.commit()
            print(f"   ✓ Updated {updated_projects} project(s)")
            print("")
            
            # Fix BlogPost image_url
            print("4. Fixing BlogPost image_url...")
            posts = BlogPost.query.all()
            updated_posts = 0
            for post in posts:
                if post.image_url:
                    original = post.image_url
                    if 'localhost:5000' in original or '127.0.0.1:5000' in original:
                        # Extract path part
                        if '/static/' in original:
                            path = '/' + original.split('/static/')[1]
                            post.image_url = path
                            updated_posts += 1
                            print(f"   Post {post.id}: {original} -> {path}")
                        else:
                            # Try to extract path
                            from urllib.parse import urlparse
                            parsed = urlparse(original)
                            if parsed.path:
                                post.image_url = parsed.path
                                updated_posts += 1
                                print(f"   Post {post.id}: {original} -> {parsed.path}")
            db.session.commit()
            print(f"   ✓ Updated {updated_posts} post(s)")
            print("")
            
            print("=== Image URL Fix Completed ===")
            print(f"Total updates: {updated_users + updated_profiles + updated_projects + updated_posts}")
            
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_image_urls()
