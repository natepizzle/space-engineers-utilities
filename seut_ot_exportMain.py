import bpy
import os

from bpy.types                       import Operator
from .seut_ot_recreateCollections    import SEUT_OT_RecreateCollections
from .seut_ot_export                 import SEUT_OT_Export

class SEUT_OT_ExportMain(Operator):
    """Exports the main model"""
    bl_idname = "object.export_main"
    bl_label = "Export Main"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports the 'Main' collection"""

        scene = context.scene
        preferences = bpy.context.preferences.addons.get(__package__).preferences

        collections = SEUT_OT_RecreateCollections.get_Collections()

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath == "" or os.path.exists(scene.prop_export_exportPath) == False:
            self.report({'ERROR'}, "SEUT: No export folder defined or export folder doesn't exist. (003)")
            return {'CANCELLED'}

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath.find("Models\\") == -1:
            self.report({'ERROR'}, "SEUT: Export folder does not contain 'Models\\'. Cannot be transformed into relative path. (014)")
            return {'CANCELLED'}

        if scene.prop_subtypeId == "":
            self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
            return {'CANCELLED'}

        layerCollection = None
        layerCollection = SEUT_OT_Export.recursiveViewLayerCollectionSearch(context.layer_collection, "Main")

        print("Result: " + str(layerCollection))

        print("up top: " + layerCollection.name + " - " + str(layerCollection.exclude))

        if layerCollection is not None and layerCollection.exclude is True:
            self.report({'ERROR'}, "SEUT: Collection 'Main' excluded from view layer. Export not possible. (019)")
            return {'CANCELLED'}

        if collections['main'] == None:
            self.report({'ERROR'}, "SEUT: Collection 'Main' not found. Export not possible. (002)")
            return {'CANCELLED'}

        if len(collections['main'].objects) == 0:
            self.report({'ERROR'}, "SEUT: Collection 'Main' is empty. Export not possible. (005)")
            return {'CANCELLED'}

        # Export XML if boolean is set.
        if scene.prop_export_xml:
            self.report({'INFO'}, "SEUT: Exporting XML for 'Main'.")
            SEUT_OT_Export.export_XML(self, context, collections['main'])

        # Export FBX if boolean is set.
        if scene.prop_export_fbx:
            self.report({'INFO'}, "SEUT: Exporting FBX for 'Main'.")
            SEUT_OT_Export.export_FBX(self, context, collections['main']) #STOLLIE: This exports the Main Model using Blenders in-built method.

        return {'FINISHED'}