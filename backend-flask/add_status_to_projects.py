"""
Migration script to add 'status' column to projects table and update existing records
Run this script to ensure all projects have status=True by default
"""
from app import app, db
from sqlalchemy import text, inspect

def add_status_column():
    """Add status column to projects table if it doesn't exist, and update existing records"""
    with app.app_context():
        try:
            # Check if column exists using SQLAlchemy inspector (works with MySQL, SQLite, etc.)
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('projects')]
            
            if 'status' not in columns:
                print("Adding 'status' column to projects table...")
                # Get database dialect to use appropriate SQL syntax
                dialect = db.engine.dialect.name
                
                if dialect == 'mysql':
                    db.session.execute(text("""
                        ALTER TABLE projects 
                        ADD COLUMN status BOOLEAN DEFAULT 1
                    """))
                elif dialect == 'sqlite':
                    db.session.execute(text("""
                        ALTER TABLE projects 
                        ADD COLUMN status BOOLEAN DEFAULT 1
                    """))
                else:
                    db.session.execute(text("""
                        ALTER TABLE projects 
                        ADD COLUMN status BOOLEAN DEFAULT TRUE
                    """))
                
                db.session.commit()
                print("✓ Status column added successfully!")
            else:
                print("✓ Status column already exists")
            
            # Update all existing projects to status=True if they are NULL or False
            print("Updating existing projects to status=True...")
            if db.engine.dialect.name == 'mysql':
                # MySQL uses 1/0 for boolean
                result = db.session.execute(text("""
                    UPDATE projects 
                    SET status = 1 
                    WHERE status IS NULL OR status = 0
                """))
            else:
                # SQLite and others
                result = db.session.execute(text("""
                    UPDATE projects 
                    SET status = 1 
                    WHERE status IS NULL OR status = 0
                """))
            
            updated_count = result.rowcount
            db.session.commit()
            
            if updated_count > 0:
                print(f"✓ Updated {updated_count} project(s) to status=True")
            else:
                print("✓ All projects already have status=True")
            
            print("\n✓ Migration completed successfully!")
                
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
            print("\nIf this fails, you may need to:")
            print("1. Check database connection")
            print("2. Manually verify the 'status' column exists in the 'projects' table")
            print("3. Or manually update projects: UPDATE projects SET status = 1 WHERE status IS NULL OR status = 0")

if __name__ == '__main__':
    add_status_column()
