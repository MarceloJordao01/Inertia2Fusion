import adsk.core, adsk.fusion, adsk.cam, traceback

def setMaterialForBody(body, materialId):
    """
    Define o material do corpo usando o índice do material na biblioteca do Fusion.
    
    Parâmetros:
      body (BRepBody): Corpo a que o material será atribuído.
      materialId (int): Índice do material desejado na biblioteca de materiais do Fusion.
    
    Retorna:
      bool: True se o material foi atribuído com sucesso, False caso contrário.
    """
    try:
        # Acessa as bibliotecas de materiais
        mLibs = adsk.core.Application.get().materialLibraries                
        # Seleciona a biblioteca de materiais do Fusion (normalmente no índice 3)
        mLib = mLibs.item(3)
        targetMaterial = mLib.materials.item(materialId)
                
        if targetMaterial is None:
            raise ValueError("Material com índice '{}' não encontrado na biblioteca.".format(materialId))
        
        # Atribui o material ao corpo.
        body.material = targetMaterial
        return True
    except Exception as e:
        adsk.core.Application.get().userInterface.messageBox(
            'Erro ao alterar o material:\n{}'.format(traceback.format_exc()))
        return False

def getMaterialOfBody(body):
    """
    Retorna o material atualmente atribuído ao corpo.
    
    Parâmetros:
      body (BRepBody): Corpo a ser verificado.
      
    Retorna:
      Material: Objeto material atribuído ao corpo ou None se ocorrer erro.
    """
    try:
        return body.material
    except Exception as e:
        adsk.core.Application.get().userInterface.messageBox(
            'Erro ao obter o material do corpo:\n{}'.format(traceback.format_exc()))
        return None

def listFusionMaterials():
    """
    Retorna uma lista com os nomes de todos os materiais disponíveis na biblioteca do Fusion.
    
    Observação: Neste exemplo, utiliza-se a biblioteca do Fusion que normalmente está no índice 3.
    
    Retorna:
      list[str]: Lista com os nomes dos materiais.
    """
    try:
        app = adsk.core.Application.get()
        mLibs = app.materialLibraries
        mLib = mLibs.item(3)
        materials = mLib.materials
        matList = []
        for i in range(materials.count):
            matList.append(materials.item(i).name)
        return matList
    except Exception as e:
        adsk.core.Application.get().userInterface.messageBox(
            'Erro ao listar os materiais:\n{}'.format(traceback.format_exc()))
        return []
