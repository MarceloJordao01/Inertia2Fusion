# Author-
# Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

from .utils import *
import math

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
    design = app.activeProduct
    rootComp = design.rootComponent

    # Exemplo: cria uma caixa com dimensões:
    # width = 10 mm, height = 20 mm, depth = 30 mm
    # Se as unidades do design forem cm, converta 10 mm = 1 cm, etc.
    width = 1.0    # 10 mm
    height = 2.0   # 20 mm
    depth = 3.0    # 30 mm
    
    
    box = createBox(rootComp, width, height, depth)

    # Rotaciona o corpo com 30° em X, 45° em Y e 60° em Z:
    rotateBodyAroundCG_xyz(box, math.radians(30), math.radians(45), math.radians(60))

    # Translada o corpo para x=10mm
    translateBody(box, 10, 0, 0)

    ui.messageBox("Dados recebidos:\nCoM: {}\nTensor: {}".format(com_data, inertia_data))
    adsk.autoTerminate(True)


def run(context):
    global ui
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # pega o root comn
        rootComp = design.rootComponent

        
        if rootComp.bRepBodies.count > 0:
            # pega a inercia total, massa total, posicao do CoM do componente
            # isso sera usado para calcular o 
            I_total, totalMass, globalCOM_mm = getGlobalInertia(rootComp)
            # ui.messageBox("Tensor Global (kg·mm²):\n{}\nMassa Total: {}\nCentro de Massa Global (mm): {}".format(I_total, totalMass, globalCOM_mm))

        else:
            ui.messageBox("Nenhum corpo encontrado no componente ativo.")
            adsk.autoTerminate(True)

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
