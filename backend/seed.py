"""Seed a demo user + a few projects across every kanban column, so the
board isn't empty on first run.

Usage:
    python seed.py
"""
from sqlmodel import Session, select

from app.database import engine, create_db_and_tables
from app.models import User, Project, Script, Asset, ProjectStatus, AssetType
from app.auth import hash_password

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demopass123"


def run():
    create_db_and_tables()
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == DEMO_EMAIL)).first()
        if not user:
            user = User(email=DEMO_EMAIL, hashed_password=hash_password(DEMO_PASSWORD))
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"Created demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        else:
            print(f"Demo user already exists: {DEMO_EMAIL}")

        existing = session.exec(select(Project).where(Project.user_id == user.id)).all()
        if existing:
            print(f"Demo user already has {len(existing)} project(s) — skipping seed.")
            return

        osaka = Project(title="My Trip to Osaka Vlog", status=ProjectStatus.SCRIPTING, user_id=user.id)
        launch = Project(title="Product Launch Ad #3", status=ProjectStatus.PRODUCTION, user_id=user.id)
        cooking = Project(title="5-Minute Pasta Recipe", status=ProjectStatus.IDEA, user_id=user.id)
        review = Project(title="Headphone Review", status=ProjectStatus.COMPLETED, user_id=user.id)
        session.add_all([osaka, launch, cooking, review])
        session.commit()
        for p in (osaka, launch, cooking, review):
            session.refresh(p)

        session.add(Script(
            project_id=osaka.id,
            content="<h2>Scene 1 - Arrival</h2><p>Land at Kansai Airport, first impressions on camera.</p>",
        ))
        session.add(Script(
            project_id=launch.id,
            content="<h2>Scene 1 - Hook</h2><p>Open on the problem this product solves in 5 seconds flat.</p>",
        ))
        session.add(Asset(
            project_id=launch.id,
            file_url="https://placehold.co/600x400?text=Storyboard",
            file_name="storyboard.png",
            asset_type=AssetType.IMAGE,
            size_bytes=0,
        ))
        session.commit()
        print(f"Seeded 4 demo projects for {DEMO_EMAIL}.")


if __name__ == "__main__":
    run()
