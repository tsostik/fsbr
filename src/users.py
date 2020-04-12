from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
                      db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(16), unique=True)
    description = db.Column(db.String(64), nullable=True, unique=False)

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
    id = db.Column(db.Integer(), primary_key=True)
    facebook_id = db.Column(db.String(64), nullable=True, unique=False)
    google_id = db.Column(db.String(64), nullable=True, unique=False)
    twitter_id = db.Column(db.String(64), nullable=True, unique=False)
    nickname = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(64), nullable=True)
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    fsbr = db.Column(db.Integer(), nullable=True)

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
