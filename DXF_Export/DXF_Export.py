#Author- ChaosComb
#Description- Export multiple DXF files

import adsk.core, adsk.fusion, adsk.cam, traceback, os, datetime

_app = adsk.core.Application.get()
_ui = _app.userInterface
_design = adsk.fusion.Design.cast(_app.activeProduct)

def run(context):
    global _app, _ui, _design

    try:
        folder = 'C:/DXF_Export_and_Combine/'
        if not (os.path.isdir(folder)):
            os.makedirs(folder)
        
        now = datetime.datetime.now()
        folder = folder + now.strftime("%Y%m%d_%H%M%S")
        os.makedirs(folder)

        doc_name = _app.activeDocument.name
        cmp_info = _app.activeProduct.allComponents
        for cmp in (cmp_info):
            if cmp.name == doc_name:
                top_cmp = cmp
                break

        export_num = 0
        sketch_set = []
        for occurence in top_cmp.occurrences:
            body_set = occurence.bRepBodies
            for body in body_set:
                Plane : adsk.fusion.BRepFaces = None
                for face in body.faces:
                    if face.geometry.classType() == adsk.core.Plane.classType():
                        if Plane:
                            if Plane.area < face.area:
                                Plane = face
                        else:
                            Plane = face
                skt = _design.rootComponent.sketches.add(Plane)

                file_name = occurence.name + '_' + body.name
                skt.saveAsDXF(folder + '/' + file_name.replace(':', '_') + '.dxf')
                export_num += 1
                sketch_set.append(skt)
        
        for body in top_cmp.bRepBodies:
            Plane : adsk.fusion.BRepFaces = None
            for face in body.faces:
                if face.geometry.classType() == adsk.core.Plane.classType():
                    if Plane:
                        if Plane.area < face.area:
                            Plane = face
                    else:
                        Plane = face
            skt = _design.rootComponent.sketches.add(Plane)

            file_name = top_cmp.name + '_' + body.name
            skt.saveAsDXF(folder + '/' + file_name.replace(':', '_') + '.dxf')
            export_num += 1

        tgs = _app.activeProduct.timeline.timelineGroups
        grp_num = _app.activeProduct.timeline.count
        tg = tgs.add(grp_num - export_num, grp_num - 1)
        tg.name = 'ExportSVG'
        _ui.messageBox('Finish')
     
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
