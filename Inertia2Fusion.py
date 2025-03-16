# Author-
# Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
from .utils import start_com_table, stop_com_table, start_inertia_table, stop_inertia_table

handlers = []  # Lista global para manter referências dos handlers

# Variáveis globais para armazenar os valores coletados
com_data = None
inertia_data = None

def on_com_data_received(com_values):
    global com_data
    com_data = com_values
    # Aqui você já tem os dados do centro de massa.
    # Em seguida, inicia a tabela do tensor de inércia.
    start_inertia_table(ui, handlers, on_data_received=on_inertia_data_received)

def on_inertia_data_received(inertia_values):
    global inertia_data
    inertia_data = inertia_values
    # Agora você tem os dados do tensor de inércia.
    # Aqui você pode prosseguir com o processamento dos dados recebidos.
    # Exemplo: exibir os valores no console (ou usar outra lógica).
    app = adsk.core.Application.get()
    ui = app.userInterface
    ui.messageBox("Dados recebidos:\nCoM: {}\nTensor: {}".format(com_data, inertia_data))

def run(context):
    global ui
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Inicia a tabela de CoM. O callback on_com_data_received será chamado
        # quando o usuário confirmar os dados.
        start_com_table(ui, handlers, on_data_received=on_com_data_received)
        
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
        stop_inertia_table(ui)
    except Exception as e:
        if ui:
            ui.messageBox('Erro:\n{}'.format(traceback.format_exc()))
