
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

import app
from app import login

import psycopg2


class DataBase(object):
    _db_name = app.app.config['DB_NAME']
    _db_user = app.app.config['DB_USER']
    _user_password = app.app.config['USER_PASSWORD']
    _db_host = app.app.config['DB_HOST']
    _db_port = app.app.config['DB_PORT']

    _connection: psycopg2 = None

    @classmethod
    def _to_connect(cls):
        try:
            cls._connection = psycopg2.connect(
                database=cls._db_name,
                user=cls._db_user,
                password=cls._user_password,
                host=cls._db_host,
                port=cls._db_port,
            )
        except psycopg2.OperationalError as ex:
            print(f"{ex}")
        except Exception as ex:
            print(f'{ex}')
        else:
            print("connection is successful")
        return

    @classmethod
    def execute_query(cls, query: str, params: tuple = None, is_returning: bool = False):
        if cls._connection is None:
            cls._to_connect()
        cls._connection.autocommit = True
        cursor = cls._connection.cursor()
        try:
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)
            if is_returning:
                result = cursor.fetchall()
        except psycopg2.OperationalError as ex:
            print(f'{ex}')
        except Exception as ex:
            print(f'{ex}')
        else:
            print("the query is executed")
            if is_returning:
                return result
            else:
                True
        finally:
            cursor.close()
        return None


class User(UserMixin):
    def __init__(self,
                 id: int,
                 login: str,
                 FIO: str,
                 room_number: int,
                 photo: str,
                 organizer: bool,
                 password_hash: str):
        self.id = id
        self.login = login
        self.FIO = FIO
        self.room_number = room_number
        self.photo = photo
        self.organizer = organizer
        self.password_hash = password_hash

    def tuple(self):
        return (self.login,
                self.FIO,
                self.room_number,
                self.photo,
                self.organizer,
                self.password_hash)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_id(cls, id: int):
        query = '''
        SELECT * 
        FROM users
        WHERE id = {}
        '''.format(id)
        result = DataBase.execute_query(query, True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return User(* params)

    @classmethod
    def get_by_login(cls, login):
        query = '''
        SELECT * 
        FROM users
        WHERE login = %s'''
        result = DataBase.execute_query(query, (login,), True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return User(* params)

    @classmethod
    def add(cls, user):
        query = '''
        INSERT INTO USERS (login, FIO, room_number, photo, organizer, password_hash)
        VALUES {}
        '''.format(user.tuple())
        return DataBase.execute_query(query)



class event_type(object):
    def __init__(self,
                 id: int,
                 name: str):
        self.id = id
        self.name = name


class user_event_type(object):
    '''описывает связь многие ко мноогим для таблиц
    event_type и user'''

class place(object):
    def __init__(self,
                 id: int,
                 floor_number:int,
                 name: str):
        self.id = id
        self.floor_number = floor_number
        self.name = name


class event(object):
    def __init__(self,
                 id: int,
                 name: str,
                 description: str,
                 photo: str,
                 event_type_id: int,
                 place_id: int,
                 organiser_id: int):
        self.id = id
        self.name = name
        self.description = description
        self.photo = photo
        self.event_type_id = event_type_id
        self.place_id = place_id
        self.organiser_id = organiser_id


class user_on_event(object):
    '''описывает связь многие ко многим для таблиц
    users и events'''


class comment(object):
    def __init__(self,
                 id: int,
                 message:str,
                 grade: int,
                 event_id: int,
                 user_id: int):
        self.id = id
        self.message = message
        self.grade = grade
        self.event_id = event_id
        self.user_id = user_id



@login.user_loader
def load_user(id: str):
    user = User.get_by_id(int(id))
    return user
