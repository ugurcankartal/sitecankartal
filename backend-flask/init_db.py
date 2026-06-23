"""
Database initialization script
Creates tables and populates with sample data
"""
from app import app, db
from models import User, Profile, SocialLink, UserSocialLink, AboutSection, Timeline, Skill, Project, BlogPost
from datetime import datetime

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        # Drop all tables (use with caution in production!)
        print("Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating tables...")
        db.create_all()
        
        # Create admin user (only one allowed)
        print("Creating admin user...")
        user_count = User.query.count()
        if user_count == 0:
            admin_user = User(
                username="admin",
                full_name="Can Kartal",
                email="ugurcankartal@gmail.com",
                phone="+90 546 882 6330",
                bio="Full-Stack & DevOps Engineer",
                location="İzmir, Türkiye"
            )
            admin_user.set_password("admin123")  # Change this password!
            db.session.add(admin_user)
            db.session.flush()  # Flush to get user.id
            
            # Create user social links
            print("Creating user social links...")
            user_social_links = [
                UserSocialLink(user_id=admin_user.id, platform="GitHub", url="https://github.com", icon_name="Github", display_order=0),
                UserSocialLink(user_id=admin_user.id, platform="LinkedIn", url="https://linkedin.com", icon_name="Linkedin", display_order=1),
                UserSocialLink(user_id=admin_user.id, platform="Email", url="mailto:ugurcankartal@gmail.com", icon_name="Mail", display_order=2),
            ]
            for link in user_social_links:
                db.session.add(link)
            
            db.session.commit()
            print("Admin user created:")
            print("  Username: admin")
            print("  Password: admin123")
            print("  ⚠️  IMPORTANT: Change the password after first login!")
            print(f"  Created {len(user_social_links)} social links for user")
        else:
            print("User already exists, skipping user creation.")
        
        # Create about section config
        print("Creating about section config...")
        about_config = AboutSection.query.first()
        if not about_config:
            about_config = AboutSection(
                title="My Journey",
                subtitle="From code to cloud - a timeline of growth and innovation",
                skills_title="Core Competencies"
            )
            db.session.add(about_config)
            db.session.commit()
            print("About section config created.")
        else:
            print("About section config already exists.")
        
        # Create profile
        print("Creating profile...")
        profile = Profile(
            name="Alex Rivera",
            title="Full-Stack & DevOps Engineer",
            description="Building scalable cloud infrastructure and crafting elegant web experiences. Passionate about automation, CI/CD, and modern web technologies.",
            profile_image_url=None,
            email="alex.rivera@devops.dev",
            phone="+1 (555) 123-4567",
            location="San Francisco, CA"
        )
        db.session.add(profile)
        db.session.flush()
        
        # Create social links
        print("Creating social links...")
        social_links = [
            SocialLink(profile_id=profile.id, platform="GitHub", url="https://github.com", icon_name="Github", display_order=0),
            SocialLink(profile_id=profile.id, platform="LinkedIn", url="https://linkedin.com", icon_name="Linkedin", display_order=1),
            SocialLink(profile_id=profile.id, platform="Email", url="mailto:alex.rivera@devops.dev", icon_name="Mail", display_order=2),
        ]
        for link in social_links:
            db.session.add(link)
        
        # Create timeline entries
        print("Creating timeline entries...")
        timeline_entries = [
            Timeline(
                year="2018",
                title="Frontend Developer",
                company="StartupCo",
                description="Built responsive web applications and component libraries.",
                icon_name="Code2",
                skills="React,TypeScript,Tailwind CSS",
                display_order=0
            ),
            Timeline(
                year="2020",
                title="Full-Stack Engineer",
                company="TechCorp",
                description="Developed scalable APIs and microservices architecture.",
                icon_name="Server",
                skills="Node.js,PostgreSQL,GraphQL,Docker",
                display_order=1
            ),
            Timeline(
                year="2022",
                title="DevOps Engineer",
                company="CloudScale",
                description="Automated infrastructure and optimized deployment pipelines.",
                icon_name="Cloud",
                skills="AWS,Kubernetes,Terraform,CI/CD",
                display_order=2
            ),
            Timeline(
                year="2024",
                title="Senior Full-Stack & DevOps",
                company="InnovateTech",
                description="Leading cloud architecture and full-stack development initiatives.",
                icon_name="Rocket",
                skills="Microservices,Serverless,Monitoring,GitOps",
                display_order=3
            ),
        ]
        for entry in timeline_entries:
            db.session.add(entry)
        
        # Create skills
        print("Creating skills...")
        skills = [
            Skill(name="React & Next.js", level=95, color="cyan", display_order=0),
            Skill(name="Node.js & Python", level=90, color="purple", display_order=1),
            Skill(name="AWS & Cloud Platforms", level=88, color="pink", display_order=2),
            Skill(name="Docker & Kubernetes", level=85, color="cyan", display_order=3),
            Skill(name="CI/CD & Automation", level=92, color="purple", display_order=4),
            Skill(name="Database Design", level=87, color="pink", display_order=5),
        ]
        for skill in skills:
            db.session.add(skill)
        
        # Create projects
        print("Creating projects...")
        projects = [
            Project(
                title="CloudScale Platform",
                description="Enterprise cloud infrastructure management platform with automated scaling and cost optimization.",
                image_url="https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&h=600&fit=crop",
                tags="AWS,Kubernetes,React,Terraform",
                icon_name="Cloud",
                gradient="from-cyan-500 to-blue-500",
                github_url="#",
                demo_url="#",
                status=True,
                display_order=0
            ),
            Project(
                title="DevOps Dashboard",
                description="Real-time monitoring and analytics dashboard for CI/CD pipelines with custom alerting system.",
                image_url="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop",
                tags="TypeScript,Node.js,Docker,Grafana",
                icon_name="BarChart3",
                gradient="from-purple-500 to-pink-500",
                github_url="#",
                demo_url="#",
                status=True,
                display_order=1
            ),
            Project(
                title="E-Commerce Microservices",
                description="Scalable microservices architecture handling 100k+ daily transactions with event-driven design.",
                image_url="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=800&h=600&fit=crop",
                tags="Node.js,MongoDB,RabbitMQ,Redis",
                icon_name="ShoppingCart",
                gradient="from-pink-500 to-red-500",
                github_url="#",
                demo_url="#",
                status=True,
                display_order=2
            ),
            Project(
                title="Mobile App Backend",
                description="High-performance serverless API serving 1M+ users with GraphQL and real-time capabilities.",
                image_url="https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&h=600&fit=crop",
                tags="AWS Lambda,GraphQL,DynamoDB,AppSync",
                icon_name="Smartphone",
                gradient="from-cyan-500 to-teal-500",
                github_url="#",
                demo_url="#",
                status=True,
                display_order=3
            ),
            Project(
                title="Data Pipeline Automation",
                description="Automated ETL pipeline processing terabytes of data daily with machine learning integration.",
                image_url="https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=800&h=600&fit=crop",
                tags="Python,Apache Airflow,Spark,PostgreSQL",
                icon_name="Workflow",
                gradient="from-purple-500 to-indigo-500",
                github_url="#",
                demo_url="#",
                status=True,
                display_order=4
            ),
            Project(
                title="Database Migration Tool",
                description="Zero-downtime database migration tool with rollback capabilities and data validation.",
                image_url="https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=800&h=600&fit=crop",
                tags="Go,PostgreSQL,MySQL,Redis",
                icon_name="Database",
                gradient="from-blue-500 to-cyan-500",
                github_url="#",
                demo_url="#",
                status=True,
                display_order=5
            ),
        ]
        for project in projects:
            db.session.add(project)
        
        # Create blog posts
        print("Creating blog posts...")
        blog_posts = [
            BlogPost(
                title="Building Scalable Microservices with Kubernetes",
                excerpt="Learn how to design, deploy, and manage microservices at scale using Kubernetes and best practices for container orchestration.",
                content="Full content here...",
                image_url="https://images.unsplash.com/photo-1667372393119-3d4c48d07fc9?w=1200&h=600&fit=crop",
                category="DevOps",
                date=datetime(2026, 2, 15),
                read_time="12 min read",
                author="Alex Rivera",
                is_featured=True,
                is_published=True,
                display_order=0
            ),
            BlogPost(
                title="Optimizing React Performance in Large Applications",
                excerpt="Deep dive into React optimization techniques including code splitting, memoization, and virtual list rendering.",
                content="Full content here...",
                image_url="https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&h=600&fit=crop",
                category="React",
                date=datetime(2026, 2, 10),
                read_time="8 min read",
                author="Alex Rivera",
                is_featured=False,
                is_published=True,
                display_order=1
            ),
            BlogPost(
                title="Infrastructure as Code: Terraform Best Practices",
                excerpt="A comprehensive guide to writing maintainable, reusable Terraform modules for cloud infrastructure.",
                content="Full content here...",
                image_url="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=600&fit=crop",
                category="Infrastructure",
                date=datetime(2026, 2, 5),
                read_time="10 min read",
                author="Alex Rivera",
                is_featured=False,
                is_published=True,
                display_order=2
            ),
            BlogPost(
                title="CI/CD Pipeline Automation with GitHub Actions",
                excerpt="Automate your deployment workflow with GitHub Actions, including testing, building, and deploying to multiple environments.",
                content="Full content here...",
                image_url="https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?w=800&h=600&fit=crop",
                category="CI/CD",
                date=datetime(2026, 1, 28),
                read_time="7 min read",
                author="Alex Rivera",
                is_featured=False,
                is_published=True,
                display_order=3
            ),
            BlogPost(
                title="Serverless Architecture: When and How to Use It",
                excerpt="Explore the benefits and challenges of serverless computing, with real-world examples using AWS Lambda.",
                content="Full content here...",
                image_url="https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=800&h=600&fit=crop",
                category="Cloud",
                date=datetime(2026, 1, 20),
                read_time="9 min read",
                author="Alex Rivera",
                is_featured=False,
                is_published=True,
                display_order=4
            ),
            BlogPost(
                title="Database Performance Tuning for High Traffic Apps",
                excerpt="Strategies for optimizing database queries, indexing, and connection pooling to handle millions of requests.",
                content="Full content here...",
                image_url="https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=800&h=600&fit=crop",
                category="Database",
                date=datetime(2026, 1, 15),
                read_time="11 min read",
                author="Alex Rivera",
                is_featured=False,
                is_published=True,
                display_order=5
            ),
        ]
        for post in blog_posts:
            db.session.add(post)
        
        # Commit all changes
        print("Committing changes...")
        db.session.commit()
        
        print("Database initialized successfully!")
        print("\nSample data has been created:")
        print(f"- 1 User (Admin)")
        print(f"- 1 Profile")
        print(f"- {len(social_links)} Social Links")
        print(f"- {len(timeline_entries)} Timeline Entries")
        print(f"- {len(skills)} Skills")
        print(f"- {len(projects)} Projects")
        print(f"- {len(blog_posts)} Blog Posts")

if __name__ == '__main__':
    init_database()
