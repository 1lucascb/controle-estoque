from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.api.infrastructure.models import User
from src.api.schemas.schemas import UserCreate, UserUpdate
from src.api.utils.hash import HashUtils


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Retrieve all users with pagination."""
        return self.db.query(User).filter(User.id > skip, User.is_active == True).limit(limit).all()

    def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieve a user by ID."""
        return self.db.query(User).filter(User.id == user_id, User.is_active == True).first()

    def get_user_by_username(self, username: str) -> User | None:
        """Retrieve a user by username."""
        return self.db.query(User).filter(User.username == username, User.is_active == True).first()

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        if self.get_user_by_username(user_data.username):
            raise Exception(f"User with username '{user_data.username}' already exists")

        user = User(
            username=user_data.username,
            password_hash=HashUtils.generate_pwd("senhapadrao123456"),
            full_name=user_data.full_name,
            role="user",
            is_active=True,
        )
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"User with username '{user_data.username}' already exists")

    def update_user(self, user_id: int, user_data: UserUpdate) -> User | None:
        """Update an existing user."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Failed to update user: username may already exist")

    def delete_user(self, client_id: int, user_id: int) -> bool:
        """Delete a user by ID."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        if user.id == client_id: # can't exclude own user
            return False

        user.is_active = False
        self.db.commit()
        return True

    def authenticate_user(self, username: str, password: str) -> User | None:
        """Authenticate a user by username and password."""
        user = self.get_user_by_username(username)
        if not user:
            return None

        if not HashUtils.check_pwd(password, user.password_hash):
            return None

        if not user.is_active:
            return None

        return user
