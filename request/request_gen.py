import json
import os
import base64
import random

images_dir = 'D:\PRUEBASPOT\PruebaSpot\pruebas\imagenes'

# Función para convertir imagen en base64
def convert_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode('utf-8')


contenido_imagenes = os.listdir(images_dir)

imagenes = []

for imagen in contenido_imagenes:
    if os.path.isfile(os.path.join(images_dir, imagen)):
        imagenes.append(convert_image_to_base64(os.path.join(images_dir, imagen)))

data = {}

for imagen in imagenes:
    id_camara = random.randint(1, len(imagenes))

    if id_camara not in data.keys():
        data[id_camara] = []

    data[id_camara].append({"image": imagen, "date": "2020-12-12"})


# Guardar los datos en formato JSON en el archivo
with open('base64.json', 'w') as file:
    json.dump(data, file)