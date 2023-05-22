from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict
from azure.storage.blob import BlobServiceClient
import os
from decouple import config
import base64
from concurrent.futures import ThreadPoolExecutor
import uuid
from sqlalchemy.orm import sessionmaker
import pymssql
from datetime import date

#Credenciales a Azure Storage
account = config('AZURE_ACCOUNT')

app = FastAPI()

posts = []

class Message(BaseModel):
    image: str
    date: date

class Result(BaseModel):
    key: int
    image_date: str
    blob_name: str
    blob_url: str
    
@app.post('/message')
def message(data: Dict[int, List[Message]]):
    #Credenciales a Azure Storage
    account = config('AZURE_ACCOUNT')
    account_key = config('AZURE_KEY')
    container_name = config('AZURE_CONTAINER')

    #NÚMERO DE HILOS PARA LA CARGA DEL BLOB
    max_workers = 2

    #Creación del cliente del servicio de Azure Storage
    blob_service_client = BlobServiceClient(account_url=f'https://{account}.blob.core.windows.net', credential=account_key)

    #Creación del cliente del contenedor
    container_client = blob_service_client.get_container_client(container_name) 

    #Inicialización de la lista de tareas a ejecutar en paralelo
    tasks_upload = []
    
    #Se recorre el diccionario de entrada a la API
    for key, lst in data.items():
        for index, element in enumerate(lst):
            
            image_base64 = element.image
            image_date = element.date

            #Decodificación de la imagen
            image_data = base64.b64decode(image_base64)

            #Asignación de nombre aleatorio al blob
            blob_name = str(uuid.uuid4()) + '.jpg'
            #Creación del cliente del container
            blob_client = container_client.get_blob_client(blob_name)
            # Ejecutar la carga del blob en paralelo
            task = blob_client.upload_blob(image_data, overwrite=True)
            tasks_upload.append((key, image_date, task))
    
    #Ejecución de las tareas en paralelo
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = []
        for key, image_date, task in tasks_upload:
            blob_url = blob_client.url
            result = {'key': key, 'image_date': image_date, 'blob_name':  blob_name, 'blob_url': blob_url}
            results.append(result)
            

    #CONEXIÓN A LA BASE DE DATOS
    #Credenciales
    server = config('DB_SERVER')
    database = config('DB_DATABASE')
    username = config('DB_USERNAME')
    password = config('DB_PASSWORD')

    connection_string = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    #CONEXIÓN A LA BASE DE DATOS
    try:
        #Conexión y creación del cursor
        connection = pymssql.connect(server = server, database = 'PRUEBASPOT', username = username, password = password)
        cursor = connection.cursor()
    except Exception as e:
        print(f'ERROR: {e}')
    #Creación de tupla con los valores de los resultados
    values = tuple(tuple(result.values()) for result in results)
    try:
        #Conexión y creación del cursor
        conn = pymssql.connect(server=server, database=database, user=username, password=password)
        cursor = conn.cursor()
        #Query para la inserción de la información
        insert_query = "INSERT INTO info_blobs (id_cam, image_date, blob_name, blob_url) VALUES (%s, %s, %s, %s)"  
        #Ejecución del query para cada uno de los valroes de Result
        cursor.executemany(insert_query, values)
        #Confirmar los cambios en la base de datos
        conn.commit()
        #Cierre del cursor
        conn.close()
    except Exception as e:
        return e
    return "Archivos subidos exitosamente al contenedor de Azure Storage. Información insertada correctamente en la base de datos"


@app.get('/prueba_carga')
def message():
    #Credenciales a Azure Storage
    account = config('AZURE_ACCOUNT')
    account_key = config('AZURE_KEY')
    container_name = config('AZURE_CONTAINER')

    #Creación del cliente de Storage
    blob_service_client = BlobServiceClient(account_url=f'https://{account}.blob.core.windows.net', credential=account_key)

    container_client = blob_service_client.get_container_client(container_name) 
    blob_list = container_client.list_blobs()
    final_list = []
    for blob in blob_list:
        final_list.append(blob.name)

    return f'Lista de blobs: {final_list}'

@app.get('/descarga_imagen')
def descarga_imagen(blob_name: str):
    account = config('AZURE_ACCOUNT')
    account_key = config('AZURE_KEY')
    container_name = config('AZURE_CONTAINER')

    #Creación del cliente de Storage
    blob_service_client = BlobServiceClient(account_url=f'https://{account}.blob.core.windows.net', credential=account_key)
    #Creación del cliente del contenedor
    container_client = blob_service_client.get_container_client(container_name) 
    #Creación de instancia del blob
    blob_client = container_client.get_blob_client(blob_name)
    #Solicitud para descargar el archivo
    with(open(blob_name, 'wb')) as file:
        download_stream = blob_client.download_blob()
        file.write(download_stream.readall())
    
    return "Archivo descargado exitosamente"
