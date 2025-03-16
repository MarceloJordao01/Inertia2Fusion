# Author-
# Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
from .utils import start_com_table, stop_com_table, start_inertia_table

# Lista global para manter referências aos handlers
handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Inicia o diálogo para a tabela do Centro de Massa
        start_com_table(ui, handlers)
        
        adsk.autoTerminate(False)
    except Exception as e:
        if ui:
            ui.messageBox('Erro:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        stop_com_table(ui)
    except Exception as e:
        if ui:
            ui.messageBox('Erro:\n{}'.format(traceback.format_exc()))
