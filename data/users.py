from sqlalchemy import Column, Integer, String
from data.db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True)
    hashed_password = Column(String(128))
    record = Column(Integer, default=0)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
    
    # Эти методы требуются Flask-Login
    @property
    def is_active(self):
        return True  # Все пользователи активны по умолчанию

    @property
    def is_authenticated(self):
        return True  # Пользователь аутентифицирован
    
    @property
    def is_anonymous(self):
        return False  # Не анонимный пользователь
    
    def get_id(self):
        return str(self.id)  # Возвращаем id как строку