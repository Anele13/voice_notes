import firebase_admin
from firebase_admin import db
from datetime import datetime 
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
CREDENTIALS = os.getenv('CREDENTIALS')

class User():
    def __init__(self, *args, **kwargs):
        self.id=kwargs.get('id',None)
        self.first_name=kwargs.get('first_name',None)
        self.last_name=kwargs.get('last_name',None)
        self.auth_date=kwargs.get('auth_date',None)
        self.campo_id=kwargs.get('campo_id',None)

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

    def send_realtime_data(self, user_id, data):
        """
        Modifica solo la informacion diaria del campo
        """
        user = self.authenticate(user_id)
        if user: 
            campo_id=user.campo_id
            _diaria_data = db.reference(f"campo/{campo_id}/diaria/").get()
            d = {}
            for k, v in _diaria_data.items():
                valor = 0
                try:
                    valor = int(v)
                except:
                    pass 
                d[k] = valor

            if isinstance(data, dict):
                for key, value in data.items():
                    d[key] = d[key] + value
            else:
                data['categoria'] = data.categoria.apply(lambda row: f'{row}s')
                for index, row in data.iterrows():
                    if row.accion in ['comprar', 'nacer']:
                        d[row.categoria] = d[row.categoria] + row.cantidad
                    else: #morir, vender 
                        d[row.categoria] = d[row.categoria] - row.cantidad
                
            # Reemplazar por 0 valores negativos
            d2 = {}
            for k, v in d.items():
                d2[k] = v if v >= 0 else 0

            db.reference(f'campo/{campo_id}/diaria/').set(d2)