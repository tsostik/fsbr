from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
                      db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))


class Role(db.Model):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(db.Integer(), primary_key=True)
    name: Mapped[str | None] = mapped_column(db.String(16), nullable=True, unique=True)
    description: Mapped[str | None] = mapped_column(db.String(64), nullable=True, unique=False)

    def __repr__(self):
        return str(self.name)+"<"+str(self.id)+">"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, Role):
            return self.name == other.name
        else:
            return other == self


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(db.Integer(), primary_key=True)
    facebook_id: Mapped[str | None] = mapped_column(db.String(64), nullable=True, unique=False)
    google_id: Mapped[str | None] = mapped_column(db.String(64), nullable=True, unique=False)
    twitter_id: Mapped[str | None] = mapped_column(db.String(64), nullable=True, unique=False)
    nickname: Mapped[str | None] = mapped_column(db.String(64), nullable=True)
    email: Mapped[str | None] = mapped_column(db.String(64), nullable=True)
    roles: Mapped[list[Role]] = relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    fsbr: Mapped[int | None] = mapped_column(db.Integer(), nullable=True)

    @property
    def display_name(self) -> str:
        if self.nickname is not None:
            display_name = str(self.nickname)
        elif self.email is not None:
            display_name = str(self.email)
        else:
            display_name = ""
        return display_name

    def __repr__(self):
        return self.display_name + "<" + str(self.id)+">"


class BaseStatus(db.Model):
    __tablename__='flags'
    flag = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Boolean, nullable=False, unique=False)

    def __init__(self, flag: str, value: bool):
        self.flag = flag
        self.value = value


def find_or_add_user(userinfo):
    if userinfo['origin'] == 'facebook':
        user = User.query.filter_by(facebook_id=userinfo['id']).first()
    elif userinfo['origin'] == 'google':
        user = User.query.filter_by(google_id=userinfo['id']).first()
    elif userinfo['origin'] == 'twitter':
        user = User.query.filter_by(twitter_id=userinfo['id']).first()
    else:
        raise ValueError
    if not user:
        user = User()
        if userinfo['origin'] == 'facebook':
            user.facebook_id = userinfo['id']
            user.email = userinfo['email']
        elif userinfo['origin'] == 'google':
            user.google_id = userinfo['id']
            user.email = userinfo['email']
        elif userinfo['origin'] == 'twitter':
            user.twitter_id = userinfo['id']
            user.nickname = userinfo['nickname']
        db.session.add(user)
        db.session.commit()
    return user


def has_permission(user: User, permission: str) -> bool:
    return hasattr(user, 'roles') and permission in user.roles


def get_flag(flagname: str) -> bool:
    flag = BaseStatus.query.filter_by(flag=flagname).first()
    if flag is not None:
        return flag.value
    else:
        return False


def set_flag(name: str, value: bool):
    flag = BaseStatus.query.filter_by(flag=name).first()
    if flag is None:
        flag = BaseStatus(flag=name, value=value)
        db.session.add(flag)
    else:
        flag.value = value
    db.session.commit()


def base_unlocked() -> bool:
    return not get_flag("locked");