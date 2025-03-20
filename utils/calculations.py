import adsk.fusion, adsk.core, traceback

def getInertiaTensor(body):
    try:
        # Obtém as propriedades físicas com alta precisão.
        physProps = body.physicalProperties
        # Usa o método getCentroidMomentsOfInertia para obter os momentos principais e extrai principais valores.
        returnValue, Ixx, Iyy, Izz, Ixy, Iyz, Ixz = physProps.getXYZMomentsOfInertia()  # Retorna um Vector3D
        

        # Monta o tensor de inércia 3x3 assumindo que os termos fora da diagonal são zero.
        inertiaTensor = [
            [Ixx, Ixy, Ixz],
            [Ixy, Iyy, Iyz],
            [Ixz, Iyz, Izz]
        ]
        return inertiaTensor
    except Exception as e:
        adsk.core.Application.get().userInterface.messageBox('Erro ao obter os momentos de inércia do centro:\n{}'.format(traceback.format_exc()))
        return None
    
def getCenterOfMass(body):
    try:
        physProps = body.physicalProperties
        comPoint = physProps.centerOfMass
        # Retorna as coordenadas do centro de massa como uma tupla.
        return (comPoint.x, comPoint.y, comPoint.z)
    except Exception as e:
        adsk.core.Application.get().userInterface.messageBox(
            'Erro ao obter o centro de massa do corpo:\n{}'.format(traceback.format_exc()))
        return None
    
def getMass(body):
    try:
        physProps = body.physicalProperties
        mass = physProps.mass
        return mass
    except Exception as e:
        adsk.core.Application.get().userInterface.messageBox(
            'Erro ao obter a massa do corpo:\n{}'.format(traceback.format_exc()))
        return None

def computeGlobalCenterOfMass(rootComp):
    """
    Itera sobre todos os corpos (incluindo os aninhados) e calcula o centro de massa global.
    Retorna uma tupla ((globalX, globalY, globalZ), totalMass).
    """
    totalMass = 0.0
    sumWeightedX = 0.0
    sumWeightedY = 0.0
    sumWeightedZ = 0.0
    
    # Usamos allBRepBodies para incluir corpos de todas as ocorrências
    bodies = rootComp.bRepBodies
    for body in bodies:
        mass = getMass(body)
        com = getCenterOfMass(body)
        sumWeightedX += com[0] * mass
        sumWeightedY += com[1] * mass
        sumWeightedZ += com[2] * mass
        totalMass += mass
    
    if totalMass != 0:
        globalX = sumWeightedX / totalMass
        globalY = sumWeightedY / totalMass
        globalZ = sumWeightedZ / totalMass
        return ((globalX, globalY, globalZ), totalMass)
    return ((0,0,0), 0)

def computeGlobalInertia(rootComp):
    """
    Calcula o tensor de inércia global do componente, seguindo dois passos:
      1. Para cada corpo, transfere o tensor de inércia (obtido em kg·cm²)
         da origem (0,0,0) para o centro de massa do corpo (I_cm).
      2. Transfere I_cm para o centro de massa global do componente (I_global)
         usando o teorema dos eixos paralelos.
    
    Conversões aplicadas:
      - Massa: de kg para g (m_g = m * 1000).
      - Centro de massa: de cm para mm (multiplicar por 10).
      - Tensor: de kg·cm² para g·mm² (multiplicar por 100000).
    
    Retorna:
      (I_total, totalMass, globalCOM_mm)
      onde:
        - I_total é o tensor de inércia global (soma de todos os I_global) em g·mm²,
        - totalMass é a massa total em kg,
        - globalCOM_mm é o centro de massa global em mm (tupla).
    """
    try:
        # Primeiro, obtenha o centro de massa global e a massa total usando uma função auxiliar.
        # globalCOM_cm é em cm.
        globalCOM_cm, totalMass = computeGlobalCenterOfMass(rootComp)
        # Converte o centro de massa global para mm:
        globalCOM_mm = (globalCOM_cm[0]*10, globalCOM_cm[1]*10, globalCOM_cm[2]*10)
        
        # Inicializa o tensor global (3x3) com zeros (em g·mm²)
        I_total = [[0.0, 0.0, 0.0],
                   [0.0, 0.0, 0.0],
                   [0.0, 0.0, 0.0]]
        
        # Matriz identidade 3x3
        I3 = [[1, 0, 0],
              [0, 1, 0],
              [0, 0, 1]]
        
        # Itera em todos os corpos (incluindo os aninhados) do componente
        bodies = rootComp.bRepBodies
        for body in bodies:
            # Massa em kg e convertida para g.
            m = getMass(body)  # kg
            m_g = m * 1000     # g
            
            # Centro de massa do corpo (em cm), convertido para mm.
            com_body_cm = getCenterOfMass(body)  # (cm)
            com_body_mm = (com_body_cm[0]*10, com_body_cm[1]*10, com_body_cm[2]*10)
            
            # Obtenha o tensor de inércia do corpo relativo à origem (em kg·cm²) e converta para g·mm².
            I_origin = getInertiaTensor(body)  # 3x3, kg·cm²
            I_origin_gmm2 = [[elem * 100000 for elem in row] for row in I_origin]
            
            # --- Passo 1: Transferir do ponto (0,0,0) para o centro de massa do corpo ---
            # Para isso, usamos:
            # I_cm = I_origin - m_g * (||p||² * I3 - p * p^T)
            # onde p = com_body_mm (vetor do corpo em mm)
            norm_com = com_body_mm[0]**2 + com_body_mm[1]**2 + com_body_mm[2]**2
            I_parallel_sub = [[ m_g * (norm_com * I3[i][j] - com_body_mm[i]*com_body_mm[j]) for j in range(3)] for i in range(3)]
            I_cm = [[ I_origin_gmm2[i][j] - I_parallel_sub[i][j] for j in range(3)] for i in range(3)]
            
            # --- Passo 2: Transferir I_cm para o centro de massa global ---
            # d = globalCOM_mm - com_body_mm (em mm)
            d = [globalCOM_mm[i] - com_body_mm[i] for i in range(3)]
            norm_d = d[0]**2 + d[1]**2 + d[2]**2
            I_parallel_add = [[ m_g * (norm_d * I3[i][j] - d[i]*d[j]) for j in range(3)] for i in range(3)]
            I_global = [[ I_cm[i][j] + I_parallel_add[i][j] for j in range(3)] for i in range(3)]
            
            # Soma o tensor transferido de cada corpo no tensor global
            for i in range(3):
                for j in range(3):
                    I_total[i][j] += I_global[i][j]
        
        return I_total, totalMass, globalCOM_mm
    except Exception as e:
        adsk.core.Application.get().userInterface.messageBox(
            "Erro ao computar o tensor de inércia global:\n{}".format(traceback.format_exc()))
        return None, None, None
    