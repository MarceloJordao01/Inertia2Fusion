import adsk.core, adsk.fusion, adsk.cam, traceback


def createBox(rootComp, width, height, depth):
    """
    Cria uma caixa com as dimensões especificadas.
    - width, height, depth são valores em cm (ou nas unidades do design).
    A caixa é criada de forma centrada no plano XY.
    """
    try:
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        
        # Desenha um retângulo centralizado: as coordenadas vão de -width/2 a width/2 etc.
        pt0 = adsk.core.Point3D.create(-width/2, -height/2, 0)
        pt1 = adsk.core.Point3D.create(width/2, height/2, 0)
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(pt0, pt1)
        
        profile = sketch.profiles.item(0)
        
        extrudes = rootComp.features.extrudeFeatures
        distance = adsk.core.ValueInput.createByReal(depth)
        extInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        isFullLength = True
        extInput.setSymmetricExtent(distance, isFullLength)
        extrude = extrudes.add(extInput)
        return extrude.bodies.item(0)
    except Exception as e:
        adsk.core.Application.get().userInterface.messageBox(
            'Erro ao criar o corpo:\n{}'.format(traceback.format_exc()))

def rotateBodyAroundCG_xyz(body, alpha, beta, gamma):
    """
    Rotaciona o corpo em torno do seu centro de massa utilizando três ângulos:
    - alpha: rotação em torno do eixo X (radianos)
    - beta:  rotação em torno do eixo Y (radianos)
    - gamma: rotação em torno do eixo Z (radianos)
    
    Todas as rotações são realizadas em relação ao CG do corpo.
    """
    try:
        # Obtém o centro de massa do corpo (normalmente em cm) e converte para mm.
        cg = body.physicalProperties.centerOfMass
        adsk.core.Application.get().userInterface.messageBox("cg_body: x={}, y={}, z={}".format(cg.x,cg.y,cg.z))
        cg_mm = adsk.core.Point3D.create(cg.x * 10, cg.y * 10, cg.z * 10)
        
        # Cria três matrizes de rotação para cada eixo usando o CG como pivô.
        matrixX = adsk.core.Matrix3D.create()
        matrixX.setToRotation(alpha, adsk.core.Vector3D.create(1, 0, 0), cg_mm)
        
        matrixY = adsk.core.Matrix3D.create()
        matrixY.setToRotation(beta, adsk.core.Vector3D.create(0, 1, 0), cg_mm)
        
        matrixZ = adsk.core.Matrix3D.create()
        matrixZ.setToRotation(gamma, adsk.core.Vector3D.create(0, 0, 1), cg_mm)
        
        # Combina as matrizes de rotação. A ordem de transformação é importante.
        # Aqui, aplicamos primeiro a rotação em X, depois em Y e finalmente em Z.
        compositeMatrix = matrixX
        compositeMatrix.transformBy(matrixY)
        compositeMatrix.transformBy(matrixZ)
        
        # Cria uma coleção com o corpo para a transformação.
        bodies = adsk.core.ObjectCollection.create()
        bodies.add(body)
        
        # Aplica a transformação via moveFeatures.
        moveFeats = body.parentComponent.features.moveFeatures
        moveInput = moveFeats.createInput(bodies, compositeMatrix)
        moveFeats.add(moveInput)
        
    except Exception as e:
        adsk.core.Application.get().userInterface.messageBox(
            'Erro ao rotacionar o corpo:\n{}'.format(traceback.format_exc()))
        
def translateBody(body, tx, ty, tz):
    """
    Translada o corpo (body) pelos deslocamentos tx, ty, tz (em milímetros).
    
    Parâmetros:
      body: O corpo (BRepBody) que será transladado.
      tx, ty, tz: Deslocamentos ao longo dos eixos X, Y e Z, respectivamente, em mm.
    """
    try:
        # Cria um vetor de translação com os valores fornecidos
        translationVec = adsk.core.Vector3D.create(tx, ty, tz)
        
        # Cria uma matriz de transformação e define sua propriedade de translação
        translationMatrix = adsk.core.Matrix3D.create()
        translationMatrix.translation = translationVec
        
        # Cria uma coleção com o corpo a ser movido
        bodies = adsk.core.ObjectCollection.create()
        bodies.add(body)
        
        # Obtém o recurso de moveFeatures do componente pai e aplica a transformação
        moveFeats = body.parentComponent.features.moveFeatures
        moveInput = moveFeats.createInput(bodies, translationMatrix)
        moveFeats.add(moveInput)
        
    except Exception as e:
        adsk.core.Application.get().userInterface.messageBox(
            'Erro ao translade o corpo:\n{}'.format(traceback.format_exc()))