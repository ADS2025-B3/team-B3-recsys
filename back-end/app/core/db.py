from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.models import User, UserCreate, UserRole
from app import crud
import logging

logger = logging.getLogger(__name__)
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

def init_db(session: Session) -> None:
    # Create superuser
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            role=UserRole.admin,
        )
        user = crud.user.create_user(session=session, user_create=user_in)
        logger.info("Superuser created.")
    else:
        logger.info("Superuser already exists.")