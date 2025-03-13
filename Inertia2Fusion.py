# Author-
# Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

from .utils import com_table
# import utils


# Lista global para manter referências aos handlers
handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Cria uma definição de comando para o diálogo de centro de massa.
        cmdDef = ui.commandDefinitions.addButtonDefinition('centerOfMassDialog',
                                                             'Centro de Massa',
                                                             'Insira as coordenadas do centro de massa do objeto',
                                                             '')
        # Adiciona o event handler para a criação do comando.
        onCommandCreated = com_table.CenterOfMassCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
        
        # Executa o comando que abrirá o diálogo.
        cmdDef.execute()
        
        # Impede que o add-in seja finalizado imediatamente
        adsk.autoTerminate(False)
        # start(ui, handlers)

    except Exception as e:
        if ui:
            ui.messageBox('Falha:\n{}'.format(traceback.format_exc()))



# # Handler para a criação do comando (quando o diálogo é iniciado)
# class CenterOfMassCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
#     def notify(self, args):
#         try:
#             cmd = args.command
#             inputs = cmd.commandInputs
            
#             # Cria três campos de texto para as coordenadas X, Y e Z com valores padrão '0.0'
#             inputs.addStringValueInput('xInput', 'Centro de Massa X', '0.0')
#             inputs.addStringValueInput('yInput', 'Centro de Massa Y', '0.0')
#             inputs.addStringValueInput('zInput', 'Centro de Massa Z', '0.0')
            
#             # Adiciona o handler para quando o comando for executado (usuário clicar OK)
#             # onExecute = CenterOfMassCommandExecuteHandler()
#             # cmd.execute.add(onExecute)
#             # handlers.append(onExecute)
#         except Exception as e:
#             app = adsk.core.Application.get()
#             ui = app.userInterface
#             ui.messageBox('Falha ao criar o comando:\n{}'.format(traceback.format_exc()))

# # Handler para a execução do comando (captura dos inputs do usuário)
# class CenterOfMassCommandExecuteHandler(adsk.core.CommandEventHandler):
#     def notify(self, args):
#         try:
#             eventArgs = adsk.core.CommandEventArgs.cast(args)
#             inputs = eventArgs.command.commandInputs
            
#             # Captura os valores dos campos de texto
#             xVal = inputs.itemById('xInput').value
#             yVal = inputs.itemById('yInput').value
#             zVal = inputs.itemById('zInput').value
            
#             # Exibe os valores informados em uma message box
#             adsk.core.Application.get().userInterface.messageBox(
#                 'Centro de Massa inserido:\nX: {}\nY: {}\nZ: {}'.format(xVal, yVal, zVal))
#         except Exception as e:
#             adsk.core.Application.get().userInterface.messageBox(
#                 'Falha na execução do comando:\n{}'.format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        # Remove a definição do comando se ele existir.
        cmdDef = ui.commandDefinitions.itemById('centerOfMassDialog')
        if cmdDef:
            cmdDef.deleteMe()
    except Exception as e:
        if ui:
            ui.messageBox('Falha:\n{}'.format(traceback.format_exc()))
