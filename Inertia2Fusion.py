# Author-
# Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
from . import utils

# Variável global para armazenar a matriz de coordenadas
coords_matrix = []

def run(context):
    global coords_matrix
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        ui.messageBox(f"exec")

    except Exception as e:
        if ui:
            ui.messageBox(f"Failed:\n{traceback.format_exc()}")

def stop(context):
    ui = None
    try:
        # Chamando a função stop para limpar o painel de tabela
        utils.table_stop()
    except Exception as e:
        if ui:
            ui.messageBox(f"Failed:\n{traceback.format_exc()}")

