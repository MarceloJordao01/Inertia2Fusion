import adsk.core, adsk.fusion, adsk.cam, traceback

_handlers = []  # Lista local para manter referências dos handlers

def start_com_table(ui, handlers):
    try:
        # Cria (ou recupera) a definição do comando para a tabela do CoM
        cmdDef = ui.commandDefinitions.itemById('CoMTableCommand')
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition(
                'CoMTableCommand',
                'Tabela Centro de Massa',
                'Tabela para entrada das coordenadas do centro de massa'
            )
        
        # Conecta o evento de criação do comando
        onCmdCreated = CoMCommandCreatedHandler()
        cmdDef.commandCreated.add(onCmdCreated)
        handlers.append(onCmdCreated)
        
        cmdDef.execute()
        adsk.autoTerminate(False)
    except Exception as e:
        ui.messageBox('Erro ao iniciar a tabela de CoM: {}'.format(traceback.format_exc()))

def stop_com_table(ui):
    try:
        cmdDef = ui.commandDefinitions.itemById('CoMTableCommand')
        if cmdDef:
            cmdDef.deleteMe()
    except Exception as e:
        ui.messageBox('Erro ao parar a tabela de CoM: {}'.format(traceback.format_exc()))

class CoMCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            cmd = args.command
            inputs = cmd.commandInputs

            # Cria a tabela com 1 linha de dados e 3 colunas
            table = inputs.addTableCommandInput('comTable', 'Centro de Massa', 3, '')
            table.maximumVisibleRows = 2  # 1 linha de cabeçalho + 1 linha de dados
            table.columnSpacing = 1
            table.rowSpacing = 1
            # Remove as marcações (linhas de grade) da tabela
            table.hasGrid = False

            # Adiciona o cabeçalho: "X", "Y", "Z"
            headers = ['X', 'Y', 'Z']
            for col, header in enumerate(headers):
                headerInput = inputs.addStringValueInput(f'header_{col}', '', header)
                headerInput.isReadOnly = True
                table.addCommandInput(headerInput, 0, col, 0, 0)

            # Adiciona a linha de dados (linha 1)
            for col in range(3):
                input_id = f'com_row1_col{col}'
                dataInput = inputs.addStringValueInput(input_id, '', '0.0')
                table.addCommandInput(dataInput, 1, col, 0, 0)

            # Conecta o handler para o "OK" do comando
            onExecute = CoMTableOKHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)
        except Exception as e:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Erro ao criar tabela de CoM: {}'.format(traceback.format_exc()))

class CoMTableOKHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = eventArgs.command.commandInputs
            table = inputs.itemById('comTable')
            
            # Captura os valores da única linha de dados
            com_values = []
            for col in range(3):
                input_id = f'com_row1_col{col}'
                dataInput = inputs.itemById(input_id)
                com_values.append(dataInput.value if dataInput else '0.0')
            
            # Exibe os valores do CoM
            adsk.core.Application.get().userInterface.messageBox(
                'Centro de Massa:\nX: {}\nY: {}\nZ: {}'.format(com_values[0], com_values[1], com_values[2]))
            
            # Após confirmar os dados do CoM, abre o diálogo do tensor de inércia
            from . import inertia_table
            inertia_table.start_inertia_table(adsk.core.Application.get().userInterface, _handlers)
        except Exception as e:
            adsk.core.Application.get().userInterface.messageBox('Erro ao processar tabela de CoM: {}'.format(traceback.format_exc()))
