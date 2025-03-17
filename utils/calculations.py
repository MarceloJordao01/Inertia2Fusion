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


# TODO: corrigir a inercia por que ela eh calculada a partir do centro do componente, logo deve-se fazer a translacao primeiro e depois os eixos paralelos
def computeGlobalInertiaTensor(rootComp):
    """
    Calcula o tensor de inércia global do componente, considerando a soma dos tensores
    de inércia de cada corpo (obtidos a partir de getInertiaTensor) com o ajuste pelo teorema
    do eixo paralelo. Os valores de distância (centro de massa) são convertidos de cm para mm
    (multiplicando por 10) e o tensor é convertido de kg·cm² para kg·mm² (multiplicando por 100).
    
    Retorna:
      - normalizedInertia: tensor de inércia global normalizado pela massa total (kg·mm²/kg)
      - totalMass: massa total (kg)
      - globalCoM: centro de massa global em mm (tuple)
    """
    # Calcula o centro de massa global (em cm) e a massa total
    globalCoM_cm, totalMass = computeGlobalCenterOfMass(rootComp)
    # Converte o centro de massa para mm
    globalCoM = (globalCoM_cm[0] * 10, globalCoM_cm[1] * 10, globalCoM_cm[2] * 10)
    
    # Inicializa o tensor global (3x3) com zeros.
    globalInertia = [[0.0, 0.0, 0.0],
                     [0.0, 0.0, 0.0],
                     [0.0, 0.0, 0.0]]
    
    # Matriz identidade 3x3
    I3 = [[1, 0, 0],
          [0, 1, 0],
          [0, 0, 1]]
    
    bodies = rootComp.bRepBodies
    for body in bodies:
        mass = getMass(body)
        # Obtém o tensor de inércia do corpo (em kg·cm²)
        I_body_cm = getInertiaTensor(body)
        if I_body_cm is None:
            continue
        # Converte para kg·mm² (multiplica cada valor por 100)
        I_body = [[val * 100 for val in row] for row in I_body_cm]
        
        # Obtém o centro de massa do corpo (em cm) e converte para mm
        com_body_cm = getCenterOfMass(body)
        com_body = (com_body_cm[0] * 10, com_body_cm[1] * 10, com_body_cm[2] * 10)
        
        # Calcula o vetor de deslocamento d entre o centro do corpo e o centro global (em mm)
        d = (com_body[0] - globalCoM[0],
             com_body[1] - globalCoM[1],
             com_body[2] - globalCoM[2])
        d_norm_sq = d[0]**2 + d[1]**2 + d[2]**2
        
        # Calcula o termo do teorema do eixo paralelo:
        # m * (||d||² * I - d*d^T)
        parallel_term = [[ mass * (d_norm_sq * I3[i][j] - d[i] * d[j]) for j in range(3)] for i in range(3)]
        
        # Soma a contribuição do corpo: tensor do corpo + termo paralelo
        I_total = [[I_body[i][j] + parallel_term[i][j] for j in range(3)] for i in range(3)]
        
        # Acumula no tensor global
        for i in range(3):
            for j in range(3):
                globalInertia[i][j] += I_total[i][j]
    
    # Normaliza dividindo pelo total de massa, se for diferente de zero.
    if totalMass != 0:
        normalizedInertia = [[globalInertia[i][j] / totalMass for j in range(3)] for i in range(3)]
    else:
        normalizedInertia = globalInertia
        
    return normalizedInertia, totalMass, globalCoM

def computeGlobalInertia(rootComp):
    """
    Itera sobre todos os corpos do componente e calcula o tensor de inércia global,
    transferindo cada tensor de inércia para o centro de massa global usando o teorema do eixo paralelo.
    Essa função não realiza a normalização pela massa total.
    
    Notas:
      - As massas são obtidas em kg.
      - Os centros de massa são retornados em cm; multiplicamos por 10 para converter para mm.
      - O tensor obtido por getInertiaTensor é assumido em kg·cm² e, para converter para kg·mm², multiplicamos por 100.
    
    Retorna:
      (I_total, totalMass, globalCOM_mm)
      onde I_total é o tensor de inércia global (kg·mm²), totalMass é a massa total (kg) e
      globalCOM_mm é o centro de massa global em mm (tupla).
    """
    try:
        # Obtém o centro de massa global (em cm) e a massa total
        globalCOM_cm, totalMass = computeGlobalCenterOfMass(rootComp)
        # Converte o centro global de cm para mm
        globalCOM_mm = (globalCOM_cm[0]*10, globalCOM_cm[1]*10, globalCOM_cm[2]*10)
        
        # Inicializa o tensor global 3x3 com zeros
        I_total = [[0.0, 0.0, 0.0],
                   [0.0, 0.0, 0.0],
                   [0.0, 0.0, 0.0]]
        
        # Itera por todos os corpos do componente
        bodies = rootComp.bRepBodies
        for body in bodies:
            m = getMass(body)  # em kg
            com_body_cm = getCenterOfMass(body)  # em cm
            # Converte o centro de massa do corpo para mm
            com_body_mm = (com_body_cm[0]*10, com_body_cm[1]*10, com_body_cm[2]*10)
            
            # Vetor d = globalCOM_mm - com_body_mm (em mm)
            d = [globalCOM_mm[i] - com_body_mm[i] for i in range(3)]
            d2 = d[0]**2 + d[1]**2 + d[2]**2  # norma de d ao quadrado
            
            # Matriz identidade 3x3
            I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            # Aplica o teorema do eixo paralelo: m * (||d||²·I₃ – d*dᵀ)
            addInertia = [[ m * (d2 * I3[i][j] - d[i]*d[j]) for j in range(3)] for i in range(3)]
            
            # Obtém o tensor de inércia do corpo (em kg·cm²) e converte para kg·mm² (multiplica por 100)
            I_body_cm2 = getInertiaTensor(body)
            I_body_mm2 = [[elem * 100 for elem in row] for row in I_body_cm2]
            
            # Tensor do corpo transferido para o centro global:
            I_body_global = [[I_body_mm2[i][j] + addInertia[i][j] for j in range(3)] for i in range(3)]
            
            # Soma o tensor de cada corpo
            for i in range(3):
                for j in range(3):
                    I_total[i][j] += I_body_global[i][j]
        
        return I_total, totalMass, globalCOM_mm
    except Exception as e:
        adsk.core.Application.get().userInterface.messageBox(
            "Erro ao computar o tensor de inércia global (sem normalização):\n{}".format(traceback.format_exc()))
        return None, None, None
