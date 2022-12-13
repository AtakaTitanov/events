import os

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
                return True
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

    def __repr__(self):
        return f'U id={self.id} login={self.login}'

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
        result = DataBase.execute_query(query, is_returning=True)
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
    def update(cls,
               user_id: int,
               FIO: str,
               room_number: int,
               photo: str = None):
        if photo is None:
            query = '''
            UPDATE users
            SET FIO = '{}' , room_number = {}
            WHERE id = {} '''.format(FIO, room_number, user_id)
        else:
            query = '''
            UPDATE users
            SET FIO = '{}' , room_number = {} , photo = '{}' 
            WHERE id = {} '''.format(FIO, room_number, photo, user_id)
        return DataBase.execute_query(query)


    @classmethod
    def add(cls, user):
        query = '''
        INSERT INTO USERS (login, FIO, room_number, photo, organizer, password_hash)
        VALUES {}
        '''.format(user.tuple())
        return DataBase.execute_query(query)


class Event_type(object):
    def __init__(self,
                 id: int,
                 name: str):
        self.id = id
        self.name = name

    @classmethod
    def get_all_types(cls):
        query = '''
        SELECT * FROM event_type'''
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        return result

    @classmethod
    def get_by_id(cls, event_type_id):
        query = '''
        SELECT * 
        FROM event_type
        WHERE id = {}'''.format(event_type_id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return Event_type(* params)


class User_event_type(object):
    '''описывает связь многие ко мноогим для таблиц
    event_type и user'''

    @classmethod
    def add(cls, user_id: int, event_type_id: int):
        query = '''
        INSERT INTO user_event_type VALUES ({}, {}) 
        '''.format(event_type_id, user_id)
        return DataBase.execute_query(query)

    @classmethod
    def delete_by_user_id(cls, user_id: int):
        query = '''
        DELETE 
        FROM user_event_type
        WHERE user_id = {}'''.format(user_id)
        return DataBase.execute_query(query)

    @classmethod
    def get_user_types(cls, user_id):
        query = '''
        SELECT * FROM event_type INNER JOIN user_event_type ON event_type.id = user_event_type.event_type_id
        WHERE user_event_type.user_id = {}'''.format(user_id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        types = []
        for item in result:
            params = item[0], item[1]
            ev_type = Event_type(* params)
            types.append(ev_type)
        return types


class Place(object):
    def __init__(self,
                 id: int,
                 floor_number:int,
                 name: str):
        self.id = id
        self.floor_number = floor_number
        self.name = name

    @classmethod
    def get_all_places(cls):
        query = '''
        SELECT * 
        FROM place'''
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        result = list(map(lambda x: Place(* x), result))
        return result

    @classmethod
    def get_by_id(cls, place_id):
        query = '''
        SELECT * 
        FROM place
        WHERE id = {}'''.format(place_id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return Place(* params)


class Event(object):
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

    def tuple(self):
        return (self.name,
                self.description,
                self.photo,
                self.event_type_id,
                self.place_id,
                self.organiser_id)

    @classmethod
    def get_by_id(cls, event_id):
        query = '''
        SELECT * FROM event
        WHERE id = {}'''.format(event_id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return Event(* params)


    @classmethod
    def get_all_events(cls):
        query = '''
        SELECT * 
        FROM event'''
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        result = list(map(lambda x: Event(*x), result))
        return result

    @classmethod
    def add(cls, event):
        query = '''
        INSERT INTO event (name, description, photo, event_type_id, place_id, organizer_id)
        VALUES {}'''.format(event.tuple())
        return DataBase.execute_query(query)


class User_on_event(object):
    '''описывает связь многие ко многим для таблиц
    users и events'''

    @classmethod
    def add(cls, user_id, event_id):
        query = '''
        INSERT INTO user_on_event (user_id, event_id)
        VALUES ({}, {})'''.format(user_id, event_id)
        return DataBase.execute_query(query)


    @classmethod
    def delete(cls, user_id, event_id):
        query = '''
        DELETE FROM user_on_event
        WHERE user_id = {} and event_id = {}
        '''.format(user_id, event_id)
        return DataBase.execute_query(query)


    @classmethod
    def is_there(cls, user_id, event_id):
        query = '''
        SELECT * FROM user_on_event
        WHERE user_id = {} and event_id = {}
        '''.format(user_id, event_id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return False
        else:
            return True

    @classmethod
    def get_users_by_event_id(cls, event_id):
        query = '''
        SELECT * FROM users INNER JOIN user_on_event ON users.id = user_on_event.user_id
        WHERE user_on_event.event_id = {}'''.format(event_id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        users = []
        for item in result:
            params = item[:len(item)-2:]
            user = User(*params)
            users.append(user)
        return users



class Comment(object):
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
        self.user = User.get_by_id(user_id)

    def tuple(self):
        return (self.message,
                self.grade,
                self.event_id,
                self.user_id)

    @classmethod
    def add(cls, comment):
        query = '''
        INSERT INTO comment (message, grade, event_id, user_id)
        VALUES {}'''.format(comment.tuple())
        return DataBase.execute_query(query)

    @classmethod
    def get_by_event_id(cls, event_id):
        query = '''
        SELECT * 
        FROM comment
        WHERE event_id = {}
        '''.format(event_id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        result = list(map(lambda x: Comment(* x), result))
        return result


@login.user_loader
def load_user(id: str):
    user = User.get_by_id(int(id))
    print(f'user {user} loaded')
    return user
