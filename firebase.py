import firebase_admin
from firebase_admin import db
from datetime import datetime 
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
CREDENTIALS = os.getenv('CREDENTIALS')

class User():
    def __init__(self,id, first_name, last_name, photo_url, auth_date, campo_id):
        self.id=id
        self.first_name=first_name
        self.last_name=last_name
        self.photo_url=photo_url
        self.auth_date=auth_date
        self.campo_id=campo_id

    def __str__(self):
        return f'Usuario: {self.first_name} {self.last_name}'


class FirebaseDB():
    def __init__(self):
        firebase_admin.initialize_app(firebase_admin.credentials.Certificate(CREDENTIALS), {'databaseURL':DATABASE_URL})

    def authenticate(self, user_id):
        _user_data = db.reference(f"user/{user_id}").get()
        if _user_data:
            _user_data.update({'id':user_id})
            return User(**_user_data)       
        return None         

    
    def create_user(self):
        reference = db.reference("user")
        _user_data ={'id': 657977867,
                    'first_name': 'Prueba', 
                    'last_name': 'Prueba', 
                    'photo_url': 'https://t.me/i/userpic/320/J-dTesjUFxLC-XWoavzXoocxHHakHq1Ux8TTkwnUVCk.jpg', 
                    'auth_date': '1653826990', 
                    'campo_id': 1}     
        reference.set({_user_data.pop('id'):_user_data})


    def send_realtime_data(self, user_id, data):
        user = self.authenticate(user_id)
        if data and user: 
            campo_id=user.campo_id
            now = str(datetime.now().date())
            if data:
                for key, value in data.items():
                    db.reference(f'campo/{campo_id}/{now}/{key}').set(value)