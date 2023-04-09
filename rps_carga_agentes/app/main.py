## para el endpoint de carga del archivo
import logging
import shutil

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

#####################################
##############################################################################
# https://fastapi-utils.davidmontague.xyz/user-guide/timing-middleware/
# from fastapi_utils.timing import add_timing_middleware, record_timing
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
##############################################################################

app = FastAPI()

"""
##############################################################################
add_timing_middleware(app, record=logger.info, prefix="app", exclude="untimed")
static_files_app = StaticFiles(directory=".")
app.mount(path="/static", app=static_files_app, name="static")
##############################################################################
"""

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def dame_conjunto_de_archivos(folder):
    """ me da una lista de nombre de archivo """

    conjunto_archivos = set()
    for _, _, files in os.walk(folder):
        for filename in files:
            try:
                conjunto_archivos.add(filename)
            except:
                continue

    return conjunto_archivos
import os

def obtener_directorios(path):
    directorios = []
    # Obtiene todos los nombres de archivo y directorio en el path especificado
    contenidos = os.listdir(path)
    # Itera sobre los nombres de archivo/directorio para obtener solo los directorios
    for contenido in contenidos:
        # Comprueba si el contenido es un directorio y no un archivo
        if os.path.isdir(os.path.join(path, contenido)):
            directorios.append(contenido)
    return directorios


# @app.get("/players/{player_id}")
# def read_item(player_id: str, player_name: Union[str, None] = None, filename: Union[str, None] = None):


def lee_claves():
    try:
        with open('agentes'+os.sep+'claves.csv') as f:
            dict = {}
            for line in f:
                key, value = line.strip().split(',')
                dict[key] = value

        return dict
    except:
        return {}

@app.post("/registro/{player_id}/{password}")
def carga_un_agente(player_id:str,password:str):

    try:
        dicc_claves = lee_claves()
    except:
        m = open('agentes'+os.sep+"claves.csv","w")
        m.close()
        dicc_claves = lee_claves()

    if player_id in dicc_claves.keys():
        return "Usuario ya registrado, utilice otron nombre de usuario"

    m = open('agentes'+os.sep+"claves.csv","a")
    m.write(player_id+","+password+"\n")
    m.close()

    return "Usuario registrado con exito!!"


@app.post("/cargar_agente/{player_id}/{clave}")
def carga_un_agente(player_id:str,clave:str,file: UploadFile = File(...)):

    dicc_claves = lee_claves()
    print(dicc_claves)

    if player_id in dicc_claves:
        if clave != dicc_claves[player_id]:
            return "Clave erronea"
    else:
        return "Usuario no registrado"

    list_of_players_folders = obtener_directorios("agentes")

    directorio_player = "agentes"+os.sep+player_id

    if player_id not in list_of_players_folders:
        os.mkdir(directorio_player)
    
    file_path = os.path.join(directorio_player, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    #request(lo_que_necesitemos)
    
    return "OK"


@app.get("/lista_agentes/{player_id}/")
def carga_un_agente(player_id:str):

    list_of_players_folders = obtener_directorios("agentes")

    if player_id not in list_of_players_folders:
        return "0 agentes para este jugador, carge un agente!!"

    directorio_player = "agentes"+os.sep+player_id

    lista_de_agentes = dame_conjunto_de_archivos(directorio_player)

    return lista_de_agentes


# @app.get("/selecciona_agente/{player_id}/{agente}")
# def carga_un_agente(player_id:str,agente:str):

#     list_of_players_folders = obtener_directorios("agentes")

#     if player_id not in list_of_players_folders:
#         return "0 agentes para este jugador, carge un agente!!"

#     directorio_player = "agentes"+os.sep+player_id

#     lista_de_agentes = dame_conjunto_de_archivos(directorio_player)

#     if agente not in lista_de_agentes:
#         return "Este agente no existe"
    
#     directorio_player = "agentes"+os.sep+player_id+ os.sep + agente
    
#     archivo_original = directorio_player + os.sep + agente
#     ruta_destino = "agentes"+os.sep+"RING"+os.sep+player_id+".py"
    
#     shutil.copy(archivo_original, ruta_destino)
    
#     return archivo_original,ruta_destino