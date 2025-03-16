import adsk.core, adsk.fusion, adsk.cam, traceback

_handlers = []  # Lista local para armazenar os handlers

def start_com_table(ui, handlers, on_data_received=None):
    try:
        cmdDef = ui.commandDefinitions.itemById('CoMTableCommand')
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition(
                'CoMTableCommand',
                'Tabela Centro de Massa',
                'Tabela para entrada das coordenadas do centro de massa',
                ''
            )
        
        onCmdCreated = CoMCommandCreatedHandler(on_data_received)
        cmdDef.commandCreated.add(onCmdCreated)
        handlers.append(onCmdCreated)
        
        cmdDef.execute()
        adsk.autoTerminate(False)
    except Exception as e:
        pass

def stop_com_table(ui):
    try:
        cmdDef = ui.commandDefinitions.itemById('CoMTableCommand')
        if cmdDef:
            cmdDef.deleteMe()
    except Exception as e:
        pass

class CoMCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self, on_data_received=None):
        super().__init__()
        self.on_data_received = on_data_received

    def notify(self, args):
        try:
            cmd = args.command
            inputs = cmd.commandInputs

            # Cria a tabela com 1 linha de dados e 3 colunas
            table = inputs.addTableCommandInput('comTable', 'Centro de Massa', 3, '')
            table.maximumVisibleRows = 2
            table.columnSpacing = 1
            table.rowSpacing = 1
            table.hasGrid = False

            headers = ['X', 'Y', 'Z']
            for col, header in enumerate(headers):
                headerInput = inputs.addStringValueInput(f'header_{col}', '', header)
                headerInput.isReadOnly = True
                table.addCommandInput(headerInput, 0, col, 0, 0)

            for col in range(3):
                input_id = f'com_row1_col{col}'
                dataInput = inputs.addStringValueInput(input_id, '', '0.0')
                table.addCommandInput(dataInput, 1, col, 0, 0)

            onExecute = CoMTableOKHandler(self.on_data_received)
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)
        except Exception as e:
            pass

class CoMTableOKHandler(adsk.core.CommandEventHandler):
    def __init__(self, on_data_received=None):
        super().__init__()
        self.on_data_received = on_data_received

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = eventArgs.command.commandInputs

            # Coleta os valores da linha de dados da tabela
            com_values = []
            for col in range(3):
                input_id = f'com_row1_col{col}'
                dataInput = inputs.itemById(input_id)
                com_values.append(dataInput.value if dataInput else '0.0')

            # Chama o callback passando os dados do CoM
            if self.on_data_received:
                self.on_data_received(com_values)
        except Exception as e:
            pass
