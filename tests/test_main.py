from fastapi.testclient import TestClient
import unittest
import pytest
from typing import Dict, List
import sys
import base64

#Se agrega la carpeta src al path para poder importar el main.py
sys.path.append('../')
from src import main

#Se crea un cliente de prueba
@pytest.fixture
def client():
    with TestClient(main.app) as client:
        yield client

#Se crea la función de manera asíncrona para la ejecución de las pruebas
@pytest.mark.asyncio
async def test_message(client: TestClient):
    #Función para convertir la imagen a base64
    def image_to_base64(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            return encoded_string.decode('utf-8')
    #Data de prueba
    data = {
  1: [
    {
      "image": image_to_base64('imagen.jpg'),
      "date": "2023-05-22"
    },
    {
      "image": image_to_base64('imagen.jpg'),
      "date": "2023-05-23"
    }
  ],
  2: [
    {
      "image": image_to_base64('imagen.jpg'),
      "date": "2023-05-24"
    }
  ]
}
    #Realizar solicitud HTTP al endpoint de la api
    response = client.post('/message', json=data)

    #Verificar la respouesta
    assert response.status_code == 200


#Se crea la función de manera asíncrona para la ejecución de las pruebas
@pytest.mark.asyncio
async def test_prueba_carga(client: TestClient):
    #El escenario de prueba es obtener la cantidad de blobs antes de enviar los datos, 
    # y validar la diferencia de la cantidad luego de enviar 
    
    #Se obtiene la cantidad de blobs en el contenedor
    response_before = client.get('/prueba_carga')
    data_before = response_before.json()
    #Se obtiene la cantidad de blobs a partir de la respuesta
    cantidad_before = data_before['Cantidad_blobs']

    #Función para convertir la imagen a base64
    def image_to_base64(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            return encoded_string.decode('utf-8')
    #Data de prueba
    data = {
  1: [
    {
      "image": image_to_base64('imagen.jpg'),
      "date": "2023-05-22"
    },
    {
      "image": image_to_base64('imagen.jpg'),
      "date": "2023-05-23"
    }
  ],
  2: [
    {
      "image": image_to_base64('imagen.jpg'),
      "date": "2023-05-24"
    }
  ]
}
    #Realizar solicitud HTTP al endpoint de la api
    response = client.post('/message', json=data)
    #Se  obtiene la cantidad de blobs en el contenedor después de enviar los datos
    response_after = client.get('/prueba_carga')
    data_after = response_after.json()
    #Se obtiene la cantidad de blobs a partir de la respuesta
    cantidad_after = data_after['Cantidad_blobs']
    #Diferencia entre las cantidades
    difference = cantidad_after - cantidad_before
    #Esta diferencia debe ser igual a la cantidad de blobs enviados
    assert difference == sum(len(lst) for lst in data.values())

if __name__ == '__main__':
    unittest.main()