# Author-
# Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

from .utils import *

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
        design = app.activeProduct

        # pega o root comn
        rootComp = design.rootComponent

        # Inicia a tabela de CoM. O callback on_com_data_received será chamado
        # quando o usuário confirmar os dados.
        start_com_table(ui, handlers, on_data_received=on_com_data_received)

        if rootComp.bRepBodies.count > 0:
            # itera para cada componente
            # val = 1
            # for body in range(rootComp.bRepBodies.count):
            #     val+=1
            # globalCoM, totalMass = computeGlobalCenterOfMass(rootComp)
            # ui.messageBox("total_mass: {}, global_CoM {}".format(totalMass, globalCoM))

            # globalInertia, totalMass, globalCoM = computeGlobalInertiaTensor(rootComp)
            # ui.messageBox("Global Inertia Tensor (normalized): {}\nTotal Mass: {}\nGlobal CoM (mm): {}".format(
            #     globalInertia, totalMass, globalCoM))
            I_total, totalMass, globalCOM_mm = computeGlobalInertia(rootComp)
            ui.messageBox("Tensor Global (kg·mm²):\n{}\nMassa Total: {}\nCentro de Massa Global (mm): {}".format(I_total, totalMass, globalCOM_mm))

        else:
            ui.messageBox("Nenhum corpo encontrado no componente ativo.")
        
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
