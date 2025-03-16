import adsk.core, adsk.fusion, adsk.cam, traceback

_inertia_handlers = []  # Lista local para armazenar os handlers

def start_inertia_table(ui, handlers, on_data_received=None):
    try:
        cmdDef = ui.commandDefinitions.itemById('InertiaTensorTableCommand')
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition(
                'InertiaTensorTableCommand',
                'Tabela Tensor de Inércia',
                'Insira os valores do tensor de inércia (3x3)',
                ''
            )
        
        onCmdCreated = InertiaTensorTableCommandCreatedHandler(on_data_received)
        cmdDef.commandCreated.add(onCmdCreated)
        handlers.append(onCmdCreated)
        
        cmdDef.execute()
        adsk.autoTerminate(False)
    except Exception as e:
        pass

def stop_inertia_table(ui):
    try:
        cmdDef = ui.commandDefinitions.itemById('InertiaTensorTableCommand')
        if cmdDef:
            cmdDef.deleteMe()
    except Exception as e:
        pass

class InertiaTensorTableCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self, on_data_received=None):
        super().__init__()
        self.on_data_received = on_data_received

    def notify(self, args):
        try:
            cmd = args.command
            inputs = cmd.commandInputs

            # Cria a tabela com 4 colunas e 4 linhas (1 linha de cabeçalho + 3 linhas de dados)
            table = inputs.addTableCommandInput('inertiaTable', 'Tensor de Inércia (3x3)', 4, '1:1:1:1')
            table.minimumVisibleRows = 4
            table.maximumVisibleRows = 4
            table.columnSpacing = 1
            table.rowSpacing = 1
            table.hasGrid = False

            headers = ['', 'I_x', 'I_y', 'I_z']
            for col, header in enumerate(headers):
                headerInput = inputs.addStringValueInput(f'inertia_header_{col}', '', header)
                headerInput.isReadOnly = True
                table.addCommandInput(headerInput, 0, col, 0, 0)

            rowLabels = ['Ix_', 'Iy_', 'Iz_']
            for row in range(1, 4):
                labelInput = inputs.addStringValueInput(f'inertia_label_row{row}', '', rowLabels[row-1])
                labelInput.isReadOnly = True
                table.addCommandInput(labelInput, row, 0, 0, 0)
                for col in range(1, 4):
                    input_id = f'inertia_row{row}_col{col}'
                    dataInput = inputs.addStringValueInput(input_id, '', '0.0')
                    table.addCommandInput(dataInput, row, col, 0, 0)

            onExecute = InertiaTensorTableOKHandler(self.on_data_received)
            cmd.execute.add(onExecute)
            _inertia_handlers.append(onExecute)
        except Exception as e:
            pass

class InertiaTensorTableOKHandler(adsk.core.CommandEventHandler):
    def __init__(self, on_data_received=None):
        super().__init__()
        self.on_data_received = on_data_received

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = eventArgs.command.commandInputs
            tensor_values = []
            for row in range(1, 4):
                row_values = []
                for col in range(1, 4):
                    input_id = f'inertia_row{row}_col{col}'
                    dataInput = inputs.itemById(input_id)
                    row_values.append(dataInput.value if dataInput else '0.0')
                tensor_values.append(row_values)
            if self.on_data_received:
                self.on_data_received(tensor_values)
        except Exception as e:
            pass
