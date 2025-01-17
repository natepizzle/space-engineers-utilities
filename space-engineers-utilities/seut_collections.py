import bpy
import re

from bpy.types  import Operator
from bpy.types  import PropertyGroup
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty,
                        PointerProperty)

from .materials.seut_ot_create_material import create_material

seut_collections = {
    'mainScene':{
        'main': {
            'name': 'Main', 
            'color': 'COLOR_04', 
            'type': 'single'
            },
        'hkt': {
            'name': 'Collision', 
            'color': 'COLOR_08', 
            'type': 'array'
            },
        'lod': {
            'name': 'LOD', 
            'color': 'COLOR_01', 
            'type': 'dict'
            },
        'bs': {
            'name': 'BS', 
            'color': 'COLOR_05', 
            'type': 'dict'
            },
        'bs_lod': {
            'name': 'BS_LOD', 
            'color': 'COLOR_06', 
            'type': 'dict'
            },
        'mountpoints': {
            'name': 'Mountpoints', 
            'color': 'COLOR_03', 
            'type': 'temp'
            },
        'mirroring': {
            'name': 'Mirroring', 
            'color': 'COLOR_03', 
            'type': 'temp'
            },
        'render': {
            'name': 'Render', 
            'color': 'COLOR_03', 
            'type': 'temp'
            }
    },
    'subpart': {
        'main': {
            'name': 'Main', 
            'color': 'COLOR_04', 
            'type': 'single'
            },
        'hkt': {
            'name': 'Collision', 
            'color': 'COLOR_08', 
            'type': 'array'
            },
        'lod': {
            'name': 'LOD', 
            'color': 'COLOR_01', 
            'type': 'dict'
            },
        'bs': {
            'name': 'BS', 
            'color': 'COLOR_05', 
            'type': 'dict'
            },
        'bs_lod': {
            'name': 'BS_LOD', 
            'color': 'COLOR_06', 
            'type': 'dict'
            },
    },
    'character': {
        'main': {
            'name': 'Main', 
            'color': 'COLOR_04', 
            'type': 'single'
            },
        'hkt': {
            'name': 'Collision', 
            'color': 'COLOR_08', 
            'type': 'array'
            },
        'lod': {
            'name': 'LOD', 
            'color': 'COLOR_01', 
            'type': 'dict'
            },
    },
    'character_animation': {
        'main': {
            'name': 'Main', 
            'color': 'COLOR_04', 
            'type': 'single'
            },
    },
    'particle_effect': {
        'main': {
            'name': 'Main', 
            'color': 'COLOR_04', 
            'type': 'single'
            },
    }
}


names = {
    'seut': 'SEUT',
    'main': 'Main',
    'hkt': 'Collision',
    'lod': 'LOD',
    'bs': 'BS',
    'bs_lod': 'BS_LOD',
    'mountpoints': 'Mountpoints',
    'mirroring': 'Mirroring',
    'render': 'Render'
}

colors = {
    'seut': 'COLOR_02',
    'main': 'COLOR_04',
    'hkt': 'COLOR_08',
    'lod': 'COLOR_01',
    'bs': 'COLOR_05',
    'bs_lod': 'COLOR_06',
    'mountpoints': 'COLOR_03',
    'mirroring': 'COLOR_03',
    'render': 'COLOR_03'
}


def update_ref_col(self, context):
    scene = context.scene
    rename_collections(scene)


def poll_ref_col(self, object):
    collections = get_collections(self.scene)

    has_hkt = []

    for col in collections['hkt']:
        if not col.seut is self and not col.seut.ref_col is None:
            has_hkt.append(col.seut.ref_col)

    return self.scene == object.seut.scene and not object.seut.col_type is 'none' and object not in has_hkt and self.col_type == 'hkt' and (object.seut.col_type == 'main' or object.seut.col_type == 'bs')


def update_lod_distance(self, context):
    scene = context.scene
    collections = get_collections(scene)

    if self.col_type is None or self.col_type == 'none':
        return

    if not collections[self.col_type] is None:
        # This is to avoid a non-critical error where Blender expects a string for the contains check only in this particular instance. For reasons beyond human understanding.
        try:
            if self.type_index - 1 in collections[self.col_type]:
                if self.lod_distance <= collections[self.col_type][self.type_index - 1].seut.lod_distance:
                    self.lod_distance = collections[self.col_type][self.type_index - 1].seut.lod_distance + 1

            if self.type_index + 1 in collections[self.col_type]:
                if self.lod_distance >= collections[self.col_type][self.type_index + 1].seut.lod_distance:
                    collections[self.col_type][self.type_index + 1].seut.lod_distance = self.lod_distance + 1
        except TypeError:
            pass


class SEUT_Collection(PropertyGroup):
    """Holder for the varios collection properties"""

    version: IntProperty(
        name="SEUT Collection Version",
        description="Used as a reference to patch the SEUT collection properties to newer versions",
        default=1
    )
    
    scene: PointerProperty(
        type = bpy.types.Scene
    )
    
    col_type: EnumProperty(
        items=(
            ('none', 'None', ''),
            ('seut', 'SEUT', ''),
            ('main', 'Main', ''),
            ('hkt', 'Collision', ''),
            ('lod', 'LOD', ''),
            ('bs', 'BS', ''),
            ('bs_lod', 'BS_LOD', ''),
            ('mountpoints', 'Mountpoints', ''),
            ('mirroring', 'Mirroring', ''),
            ('render', 'Render', ''),
            )
    )

    ref_col: PointerProperty(
        name = "Reference",
        description = "The collection this collection is associated with",
        type = bpy.types.Collection,
        update = update_ref_col,
        poll = poll_ref_col
    )

    type_index: IntProperty(
        default = 0
    )

    lod_distance: IntProperty(
        name = "LOD Distance",
        description = "From what distance this LOD should display",
        default = 25,
        min = 0,
        update = update_lod_distance
    )


class SEUT_OT_RecreateCollections(Operator):
    """Recreates the collections"""
    bl_idname = "scene.recreate_collections"
    bl_label = "Recreate Collections"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        if not 'SEUT' in scene.view_layers:
            scene.view_layers[0].name = 'SEUT'

        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
            scene.seut.subtypeBefore = scene.name
        
        for scn in bpy.data.scenes:
            if scene.seut.subtypeId == scn.seut.subtypeId:
                scene.seut.subtypeId = scene.name
                scene.seut.subtypeBefore = scene.name
                break
    
        if not 'SEUT Node Group' in bpy.data.node_groups or bpy.data.node_groups['SEUT Node Group'].library != None:
            temp_mat = create_material()
            bpy.data.materials.remove(temp_mat)

        create_collections(context)

        tag = ' (' + scene.seut.subtypeId + ')'
        context.view_layer.active_layer_collection = scene.view_layers['SEUT'].layer_collection.children['SEUT' + tag].children['Main' + tag]

        return {'FINISHED'}


class SEUT_OT_CreateCollection(Operator):
    """Creates a specific collection"""
    bl_idname = "scene.create_collection"
    bl_label = "Create Collection"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return 'SEUT' in context.scene.view_layers


    col_type: EnumProperty(
        items = (
            ('hkt', 'Collision', 'A collection containing collision objects, assigned to another collection in the scene'),
            ('lod', 'LOD', 'A Level of Detail (LOD) collection'),
            ('bs', 'BS', 'A Build Stage (BS) collection'),
            ('bs_lod', 'BS_LOD', 'A Build Stage Level of Detail (BS_LOD) collection'),
            ),
        name = "Collection Type"
    )


    def execute(self, context):

        scene = context.scene
        tag = ' (' + scene.seut.subtypeId + ')'
        collections = get_collections(scene)

        if self.col_type == 'lod' or self.col_type == 'bs' or self.col_type == 'bs_lod':

            # This handles the case in which collections are missing from the standard 3
            if 1 not in collections[self.col_type]:
                index = 1
            elif 2 not in collections[self.col_type]:
                index = 2
            elif 3 not in collections[self.col_type]:
                index = 3
            else:
                if len(collections[self.col_type]) + 1 in collections[self.col_type]:
                    temp_key = 4
                    while temp_key in collections[self.col_type]:
                        temp_key += 1
                    index = temp_key
                else:
                    index = len(collections[self.col_type]) + 1

            collection = bpy.data.collections.new(names[self.col_type] + str(index) + tag)
            collection.seut.type_index = index

            if index - 1 in collections[self.col_type]:
                collection.seut.lod_distance = collections[self.col_type][index - 1].seut.lod_distance + 1
        
        elif self.col_type == 'hkt':
            if get_hkt_col(collections, context.view_layer.active_layer_collection.collection) is not None:
                return {'FINISHED'}

            ref_col = context.view_layer.active_layer_collection.collection

            if ref_col.seut is None or ref_col.seut.col_type == 'hkt':
                ref_col = None

            for col in collections['hkt']:
                if col.seut.ref_col == ref_col:
                    ref_col = None
                    break

            if ref_col is None:
                collection = bpy.data.collections.new(names[self.col_type] + " - None" + tag)
            else:

                if ref_col.seut.col_type == 'lod' or ref_col.seut.col_type == 'bs' or ref_col.seut.col_type == 'bs_lod':
                    collection = bpy.data.collections.new(names[self.col_type] + " - " + names[ref_col.seut.col_type] + str(ref_col.seut.type_index) + tag)
                else:
                    collection = bpy.data.collections.new(names[self.col_type] + " - " + names[ref_col.seut.col_type] + tag)

                collection.seut.ref_col = ref_col

        collection.seut.col_type = self.col_type
        collection.seut.scene = scene
        if bpy.app.version >= (2, 91, 0):
            collection.color_tag = colors[self.col_type]
        collections['seut'].children.link(collection)

        return {'FINISHED'}


def get_collections(scene):
    """Scans existing collections to find the SEUT ones"""

    # Use the keys of names to create a new dict
    collections = {}
    for key in names.keys():
        collections[key] = None

    for col in bpy.data.collections:
        if col is None:
            continue
        if not col.seut.scene is scene:
            continue
        
        if col.seut.col_type is 'none':
            continue

        elif col.seut.col_type == 'hkt':
            if collections[col.seut.col_type] is None:
                collections[col.seut.col_type] = []

            collections[col.seut.col_type].append(col)

        elif col.seut.col_type == 'lod' or col.seut.col_type == 'bs' or col.seut.col_type == 'bs_lod':
            if collections[col.seut.col_type] is None:
                collections[col.seut.col_type] = {}

            collections[col.seut.col_type][col.seut.type_index] = col

        else:
            collections[col.seut.col_type] = col
    
    return collections


def rename_collections(scene):
    """Scans existing collections to find the SEUT ones and renames them if the tag has changed"""

    tag = ' (' + scene.seut.subtypeId + ')'
    
    # This ensures that after a full copy of a scene, the collections are reassigned to the new scene
    if scene.view_layers['SEUT'].layer_collection.children[0].collection.name.startswith("SEUT "):
        scene.view_layers['SEUT'].layer_collection.children[0].collection.seut.scene = scene
        for vl_col in scene.view_layers['SEUT'].layer_collection.children[0].children:
            if not vl_col.collection.seut.scene is scene:
                vl_col.collection.seut.scene = scene

    for col in bpy.data.collections:
        if col is None:
            continue
        if not col.seut.scene is scene:
            continue

        if col.seut.col_type == 'none':
            continue
        
        elif col.seut.col_type == 'lod' or col.seut.col_type == 'bs' or col.seut.col_type == 'bs_lod':
            col.name = names[col.seut.col_type] + str(col.seut.type_index) + " (" + col.seut.scene.seut.subtypeId + ")"

        elif col.seut.col_type == 'hkt':

            if col.seut.ref_col is None:
                col.name = names[col.seut.col_type] + " - None" + " (" + col.seut.scene.seut.subtypeId + ")"

            else:
                if col.seut.ref_col.seut.col_type == 'lod' or col.seut.ref_col.seut.col_type == 'bs' or col.seut.ref_col.seut.col_type == 'bs_lod':
                    col.name = names[col.seut.col_type] + " - " + names[col.seut.ref_col.seut.col_type] + str(col.seut.ref_col.seut.type_index) + " (" + col.seut.scene.seut.subtypeId + ")"
                else:
                    col.name = names[col.seut.col_type] + " - " + names[col.seut.ref_col.seut.col_type] + " (" + col.seut.scene.seut.subtypeId + ")"
        
        else:
            col.name = names[col.seut.col_type] + " (" + col.seut.scene.seut.subtypeId + ")"


def create_collections(context):
    """Recreates the collections SEUT requires"""

    scene = context.scene
    tag = ' (' + scene.seut.subtypeId + ')'
    collections = get_collections(scene)

    for key in collections.keys():
        if collections[key] == None:

            if key == 'seut':

                collections[key] = bpy.data.collections.new(names[key] + tag)
                collections[key].seut.scene = scene
                collections[key].seut.col_type = key
                if bpy.app.version >= (2, 91, 0):
                    collections[key].color_tag = colors[key]
                scene.collection.children.link(collections[key])

            elif key == 'main':
                collections[key] = bpy.data.collections.new(names[key] + tag)
                collections[key].seut.scene = scene
                collections[key].seut.col_type = key
                if bpy.app.version >= (2, 91, 0):
                    collections[key].color_tag = colors[key]
                collections['seut'].children.link(collections[key])

            elif key == 'lod' or key == 'bs':

                collections[key] = {}

                # Keeping ['0'] for LOD0 support I may add in the future
                collections[key][1] = bpy.data.collections.new(names[key] + '1' + tag)
                collections[key][1].seut.scene = scene
                collections[key][1].seut.col_type = key
                collections[key][1].seut.type_index = 1
                if bpy.app.version >= (2, 91, 0):
                    collections[key][1].color_tag = colors[key]
                collections['seut'].children.link(collections[key][1])

                collections[key][2] = bpy.data.collections.new(names[key] + '2' + tag)
                collections[key][2].seut.scene = scene
                collections[key][2].seut.col_type = key
                collections[key][2].seut.type_index = 2
                if bpy.app.version >= (2, 91, 0):
                    collections[key][2].color_tag = colors[key]
                collections['seut'].children.link(collections[key][2])

                collections[key][3] = bpy.data.collections.new(names[key] + '3' + tag)
                collections[key][3].seut.scene = scene
                collections[key][3].seut.col_type = key
                collections[key][3].seut.type_index = 3
                if bpy.app.version >= (2, 91, 0):
                    collections[key][3].color_tag = colors[key]
                collections['seut'].children.link(collections[key][3])

                if key == 'lod':
                    collections[key][1].seut.lod_distance = 25
                    collections[key][2].seut.lod_distance = 50
                    collections[key][3].seut.lod_distance = 150

            elif key == 'hkt':
                temp_col = bpy.data.collections.new(names[key] + " - Main" + tag)
                collections[key] = []
                collections[key].append(temp_col)
                temp_col.seut.scene = scene
                temp_col.seut.col_type = key
                if bpy.app.version >= (2, 91, 0):
                    temp_col.color_tag = colors[key]
                collections['seut'].children.link(temp_col)

            elif key == 'bs_lod':
                collections[key] = {}
                collections[key][1] = bpy.data.collections.new(names[key] + '1' + tag)
                collections[key][1].seut.scene = scene
                collections[key][1].seut.col_type = key
                collections[key][1].seut.type_index = 1
                collections[key][1].seut.lod_distance = 50
                if bpy.app.version >= (2, 91, 0):
                    collections[key][1].color_tag = colors[key]
                collections['seut'].children.link(collections[key][1])
    
    # This needs to be separate because else it can cause issues if main doesn't exist yet.
    for col in bpy.data.collections:
        if col is None:
            continue
        if col.seut.scene is None:
            continue

        tag = ' (' + col.seut.scene.seut.subtypeId + ')'
        if col.seut.col_type == 'hkt' and col.seut.ref_col is None and 'Main' + tag in bpy.data.collections:
            col.seut.ref_col = bpy.data.collections['Main' + tag]

    sort_collections(context)

    return collections


def create_seut_collection(context, col_type, type_index, ref_col):

    scene = context.scene
    tag = ' (' + scene.seut.subtypeId + ')'
    collections = get_collections(scene)

    if type_index is None: type_index = 0
    
    if 'seut' not in collections or col_type not in collections:
        create_collections(context)

    if col_type == 'bs' or col_type == 'lod' or col_type == 'bs_lod':
        if type_index in collections[col_type] and not collections[col_type][type_index] is None:
            return collections[col_type][type_index]
        else:
            collection = bpy.data.collections.new(names[col_type] + str(type_index) + tag)
            collection.seut.scene = scene
            collection.seut.col_type = col_type
            collection.seut.type_index = type_index
            if bpy.app.version >= (2, 91, 0):
                collection.color_tag = colors[col_type]
            collections['seut'].children.link(collection)

    elif col_type == 'main':
        if not collections[col_type] is None:
            return collections[col_type]
        
        else:
            collection = bpy.data.collections.new(names[col_type] + tag)
            collection.seut.scene = scene
            collection.seut.col_type = col_type
            if bpy.app.version >= (2, 91, 0):
                collection.color_tag = colors[col_type]
            collections['seut'].children.link(collection)

    return collection


def sort_collections(context):

    scene = context.scene
    collections = get_collections(scene)
    seut_cols = collections['seut'].children
    
    for lod in sorted(collections['lod'].values(), key=lambda lod: lod.name.lower()):
        seut_cols.unlink(lod)
        seut_cols.link(lod)
        hkt = get_hkt_col(collections, lod)
        if not hkt is None:
            seut_cols.unlink(hkt)
            seut_cols.link(hkt)
        
    for bs in sorted(collections['bs'].values(), key=lambda bs: bs.name.lower()):
        seut_cols.unlink(bs)
        seut_cols.link(bs)
        hkt = get_hkt_col(collections, bs)
        if not hkt is None:
            seut_cols.unlink(hkt)
            seut_cols.link(hkt)
        
    for bs_lod in sorted(collections['bs_lod'].values(), key=lambda bs_lod: bs_lod.name.lower()):
        seut_cols.unlink(bs_lod)
        seut_cols.link(bs_lod)
        hkt = get_hkt_col(collections, bs_lod)
        if not hkt is None:
            seut_cols.unlink(hkt)
            seut_cols.link(hkt)


def get_hkt_col(collections, collection):
    for col in collections['hkt']:
        if col.seut.ref_col == collection:
            return col
    return None