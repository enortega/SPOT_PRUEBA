import json
from typing import Dict, List
from datetime import date
from pydantic import BaseModel

class Message(BaseModel):
    image: str
    date: date

def convert_message_to_dict(message: Message) -> Dict[str, str]:
    return {
        'image': message.image,
        'date': str(message.date)
    }

@app.post('/message')
def message(data: Dict[int, List[Message]]):
    # Resto del código...

    # Convertir los objetos Message a diccionarios
    results = [convert_message_to_dict(result) for result in results]

    # Resto del código...

    return "Archivos subidos exitosamente al contenedor de Azure Storage. Información insertada correctamente en la base de datos"
