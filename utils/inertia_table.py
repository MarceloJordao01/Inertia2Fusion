import adsk.core, adsk.fusion, adsk.cam, traceback

_inertia_handlers = []  # Lista local para armazenar os handlers

def start_inertia_table(ui, handlers):
    try:
        # Cria (ou recupera) a definição do comando para o tensor de inércia.
        cmdDef = ui.commandDefinitions.itemById('InertiaTensorTableCommand')
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition(
                'InertiaTensorTableCommand',
                'Tabela Tensor de Inércia',
                'Insira os valores do tensor de inércia (3x3)',
                ''
            )
        
        onCmdCreated = InertiaTensorTableCommandCreatedHandler()
        cmdDef.commandCreated.add(onCmdCreated)
        handlers.append(onCmdCreated)
        
        cmdDef.execute()
        adsk.autoTerminate(False)
    except Exception as e:
        ui.messageBox('Erro ao iniciar a tabela de tensor de inércia: {}'.format(traceback.format_exc()))

def stop_inertia_table(ui):
    try:
        cmdDef = ui.commandDefinitions.itemById('InertiaTensorTableCommand')
        if cmdDef:
            cmdDef.deleteMe()
    except Exception as e:
        ui.messageBox('Erro ao parar a tabela de tensor de inércia: {}'.format(traceback.format_exc()))

class InertiaTensorTableCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            cmd = args.command
            inputs = cmd.commandInputs

            # Cria a tabela com 4 colunas e 4 linhas (1 linha de cabeçalho + 3 linhas de dados).
            # A coluna 0 será para os rótulos das linhas.
            table = inputs.addTableCommandInput('inertiaTable', 'Tensor de Inércia (3x3)', 4, '1:1:1:1')
            table.minimumVisibleRows = 4
            table.maximumVisibleRows = 4
            table.columnSpacing = 1
            table.rowSpacing = 1
            # Remove as marcações (linhas de grade)
            table.hasGrid = False

            # Cabeçalho da tabela:
            # Coluna 0: vazia (ou pode ser um rótulo para linhas, se desejado)
            headers = ['', 'I_x', 'I_y', 'I_z']
            for col, header in enumerate(headers):
                headerInput = inputs.addStringValueInput(f'inertia_header_{col}', '', header)
                headerInput.isReadOnly = True
                table.addCommandInput(headerInput, 0, col, 0, 0)

            # Rótulos para as linhas de dados.
            rowLabels = ['Ix_', 'Iy_', 'Iz_']
            # Adiciona 3 linhas de dados (linhas 1 a 3):
            for row in range(1, 4):
                # Coluna 0: rótulo da linha (não editável)
                labelInput = inputs.addStringValueInput(f'inertia_label_row{row}', '', rowLabels[row-1])
                labelInput.isReadOnly = True
                table.addCommandInput(labelInput, row, 0, 0, 0)
                # Colunas 1 a 3: campos para entrada dos valores (default "0.0")
                for col in range(1, 4):
                    input_id = f'inertia_row{row}_col{col}'
                    dataInput = inputs.addStringValueInput(input_id, '', '0.0')
                    table.addCommandInput(dataInput, row, col, 0, 0)

            # Conecta o handler para o "OK" do comando
            onExecute = InertiaTensorTableOKHandler()
            cmd.execute.add(onExecute)
            _inertia_handlers.append(onExecute)
        except Exception as e:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Erro ao criar tabela de tensor de inércia: {}'.format(traceback.format_exc()))

class InertiaTensorTableOKHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = eventArgs.command.commandInputs
            table = inputs.itemById('inertiaTable')

            # Coleta os valores das 3 linhas de dados (colunas 1 a 3, pois a coluna 0 é o rótulo)
            tensor_values = []
            for row in range(1, 4):
                row_values = []
                for col in range(1, 4):
                    input_id = f'inertia_row{row}_col{col}'
                    dataInput = inputs.itemById(input_id)
                    row_values.append(dataInput.value if dataInput else '0.0')
                tensor_values.append(row_values)
            
            # Formata os valores coletados em uma matriz 3x3 para exibição
            msg = 'Tensor de Inércia inserido:\n'
            for row in tensor_values:
                msg += ' | '.join(row) + '\n'
            adsk.core.Application.get().userInterface.messageBox(msg)
        except Exception as e:
            adsk.core.Application.get().userInterface.messageBox('Erro ao processar tabela de tensor de inércia: {}'.format(traceback.format_exc()))
