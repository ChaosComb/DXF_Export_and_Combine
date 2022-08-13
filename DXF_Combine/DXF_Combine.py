#Author- ChaosComb
#Description- Combines multiple DXF files into one, used with exportDXFs

import adsk.core, adsk.fusion, adsk.cam, traceback, os

def calc_area(profile):
    # バウンディングボックスの面積を計算
    minX = profile.boundingBox.minPoint.x
    minY = profile.boundingBox.minPoint.y
    maxX = profile.boundingBox.maxPoint.x
    maxY = profile.boundingBox.maxPoint.y
    area = (maxX - minX) * (maxY - minY)
    return area

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        rootComp = design.rootComponent
        features = rootComp.features

        cmp = app.activeProduct.allComponents[0]
        Plane = rootComp.xYConstructionPlane

        # DXFファイルのリストを抽出（フォルダ内には.dxfしか存在しないものと仮定）
        mainfolder = 'C:/DXF_Export_and_Combine/'
        modelfolder = os.listdir(mainfolder)

        mf = []
        for f in os.listdir(mainfolder):
            if os.path.isdir(os.path.join(mainfolder, f)):
                mf.append(f)
        modelfolder = mf

        file_list = os.listdir(mainfolder + '/' + modelfolder[-1])
        
        i = 0
        for file_name in file_list:
            # DXFのインポート，履歴の残らない形でスケッチとしてインポートされる．
            dxfFileName = mainfolder + '/' + modelfolder[-1] + '/' + file_name

            importManager = app.importManager
            dxfOptions = importManager.createDXF2DImportOptions(dxfFileName, Plane)
            dxfOptions.isViewFit = False
            dxfOptions.isSingleSketchResult = True

            importManager.importToTarget(dxfOptions, rootComp)
            importSketch = rootComp.sketches[-1]

            # 押し出しでボディ作成
            extFeature = features.extrudeFeatures
            target_prof = []

            # プロファイルの選択，最も範囲が広いものが外周を含むプロファイルなので，それを選択する．
            for prof in importSketch.profiles:
                if target_prof:
                    target_area = calc_area(target_prof)
                    comp_area = calc_area(prof)

                    if comp_area > target_area:
                        target_prof = prof
                else:
                    target_prof = prof

            distance = adsk.core.ValueInput.createByReal(0.1)
            extrude1 = extFeature.addSimple(target_prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)        

            gap = 0.1
            if i > 0:
                # 最終的にプロジェクト関数でボディ表面をスケッチとして取得するので，全てのボディが干渉していない必要がある．
                # そのため，境界ボックスの座標を確認してその隣に移動させる．
                reference_body = cmp.bRepBodies[-2]
                cmp_maxX = reference_body.boundingBox.maxPoint.x
                cmp_minY = reference_body.boundingBox.minPoint.y

                target_body = cmp.bRepBodies[-1]
                body_minX = target_body.boundingBox.minPoint.x
                body_minY = target_body.boundingBox.minPoint.y

                moveFeature = features.moveFeatures

                bodies = adsk.core.ObjectCollection.create()
                bodies.add(target_body)

                vector = adsk.core.Vector3D.create(cmp_maxX + gap - body_minX, cmp_minY - body_minY, 0)
                transform = adsk.core.Matrix3D.create()
                transform.translation = vector

                moveFeatureInput = moveFeature.createInput(bodies, transform)
                moveFeature.add(moveFeatureInput)
            
            i = 1
            if i > 5:
                break
        
        # スケッチ作成，ボディの面情報をプロジェクトで取得
        skt = rootComp.sketches.add(Plane)
        skt.name = 'TotalSketch'
        for body in cmp.bRepBodies:
            skt.project(body.faces[-1])
        skt.saveAsDXF(mainfolder + '/' + 'totalSketch.dxf')
        
        ui.messageBox('Finish')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
