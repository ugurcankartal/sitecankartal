"""
Migration script to add 'url' column to blog_posts table
Run this script to add the url column to existing blog_posts table
"""
from app import app, db
from sqlalchemy import text, inspect

def add_url_column():
    """Add url column to blog_posts table if it doesn't exist"""
    with app.app_context():
        try:
            # Check if column exists using SQLAlchemy inspector (works with MySQL, SQLite, etc.)
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('blog_posts')]
            
            if 'url' not in columns:
                print("Adding 'url' column to blog_posts table...")
                # Get database dialect to use appropriate SQL syntax
                dialect = db.engine.dialect.name
                
                if dialect == 'mysql':
                    db.session.execute(text("""
                        ALTER TABLE blog_posts 
                        ADD COLUMN url VARCHAR(500) NULL
                    """))
                elif dialect == 'sqlite':
                    db.session.execute(text("""
                        ALTER TABLE blog_posts 
                        ADD COLUMN url VARCHAR(500)
                    """))
                else:
                    db.session.execute(text("""
                        ALTER TABLE blog_posts 
                        ADD COLUMN url VARCHAR(500)
                    """))
                
                db.session.commit()
                print("✓ URL column added successfully!")
            else:
                print("✓ URL column already exists")
            
            print("\n✓ Migration completed successfully!")
                
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
            print("\nIf this fails, you may need to:")
            print("1. Check database connection")
            print("2. Manually verify the 'url' column exists in the 'blog_posts' table")
            print("3. Or manually add column: ALTER TABLE blog_posts ADD COLUMN url VARCHAR(500)")

if __name__ == '__main__':
    add_url_column()
