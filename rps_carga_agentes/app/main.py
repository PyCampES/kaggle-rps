## para el endpoint de carga del archivo
import json
import logging
import shutil
import os
from pathlib import Path

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

AGENT_DIR = os.getenv("AGENT_DIR", "agents")

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


def claves_path() -> Path:
    full_path = Path(AGENT_DIR +os.sep + "claves.json")
    if not full_path.exists():
        full_path.write_text("{}")
    return full_path


def lee_claves():
    path = claves_path()
    return json.loads(path.read_text())

@app.post("/registro/{player_id}/{password}")
def carga_un_agente(player_id:str,password:str):
    dicc_claves = lee_claves()
    if player_id in dicc_claves.keys():
        return "Usuario ya registrado, utilice otron nombre de usuario"
    dicc_claves[player_id] = password
    dumped = json.dumps(dicc_claves)
    claves_path().write_text(dumped)
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

    list_of_players_folders = obtener_directorios(AGENT_DIR)


    directorio_player = Path(AGENT_DIR+os.sep+player_id)
    directorio_player.mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(directorio_player, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    #request(lo_que_necesitemos)
    
    return "OK"


@app.get("/lista_agentes/{player_id}/")
def carga_un_agente(player_id:str):

    list_of_players_folders = obtener_directorios(AGENT_DIR)

    if player_id not in list_of_players_folders:
        return "0 agentes para este jugador, carge un agente!!"

    directorio_player = AGENT_DIR+os.sep+player_id

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