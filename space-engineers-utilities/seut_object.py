import bpy

from bpy.types  import PropertyGroup
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty,
                        PointerProperty,
                        CollectionProperty
                        )

from .export.seut_export_utils      import get_subpart_reference
from .empties.seut_empties          import SEUT_EmptyHighlights
from .seut_collections              import get_collections, names
from .seut_errors                   import seut_report
from .seut_utils                    import link_subpart_scene, unlink_subpart_scene, get_parent_collection


def update_linkedScene(self, context):
    scene = context.scene
    empty = context.view_layer.objects.active
    collections = get_collections(scene)

    if empty is not None:
        if 'file' in empty:
            empty['file'] = ""
        unlink_subpart_scene(empty)

        if empty.seut.linkedScene is not None:
            empty['file'] = get_subpart_reference(empty, collections)

            if scene.seut.linkSubpartInstances:
                try:
                    link_subpart_scene(self, scene, empty, empty.users_collection[0])
                except AttributeError:
                    seut_report(self, context, 'ERROR', False, 'E002')
                    empty.seut.linkedScene = None


def update_default(self, context):
    scene = context.scene

    if not context.active_object.seut.default:
        return

    objects = bpy.data.collections['Mountpoints (' + scene.seut.subtypeId + ')'].objects
    
    if context.active_object.seut.default and context.active_object.name in objects:
        for obj in objects:
            if obj is context.active_object:
                pass
            elif obj.seut.default:
                obj.seut.default = False


def update_mask_preset(self, context):

    preset = self.mask_preset

    if preset != "custom":
        split = preset.split(":")
        self.exclusion_mask = int(split[0])
        self.properties_mask = int(split[1])


# These prevent the selected scene from being the current scene and the selected object being the current object
def poll_linkedScene(self, object):
    return object != bpy.context.scene and object.seut.sceneType == 'subpart'


class SEUT_Object(PropertyGroup):
    """Holder for the various object properties"""

    version: IntProperty(
        name="SEUT Object Version",
        description="Used as a reference to patch the SEUT object properties to newer versions",
        default=1
    )
    
    linkedScene: PointerProperty(
        name='Subpart Scene',
        description="Which subpart scene this empty links to. Scene must be of type 'Subpart'",
        type=bpy.types.Scene,
        poll=poll_linkedScene,
        update=update_linkedScene
    )
    
    # Deprecated with SEUT 0.9.95
    linkedObject: PointerProperty(
        name='Highlight Object',
        description="Which object this empty links to",
        type=bpy.types.Object
    )

    highlight_objects: CollectionProperty(
        type = SEUT_EmptyHighlights
    )

    highlight_object_index: IntProperty(
        default = 0
    )
    
    default: BoolProperty(
        name='Default',
        description="Whether a Mountpoint Area is the one where a block is first attempted to be placed on",
        default=False,
        update=update_default
    )
    
    pressurized: BoolProperty(
        name='Pressurized When Open',
        description="Whether a mountpoint on a door block stays pressurized when the door is opened",
        default=False
    )

    enabled: BoolProperty(
        name="Enabled",
        description="Whether a mountpoint area should be enabled or not. Disabled areas provide airtightness but don't allow blocks to be placed onto them",
        default=True
    )

    mask_preset: EnumProperty(
        name='Mask Preset',
        description="Masks determine which blocks' mountpoints can be mounted onto this mountpoint area",
        items=(
            ('0:0', 'None', 'No mountpoint mask is used'),
            ('0:1', 'Protrudes', 'The geometry behind this mountpoint portrudes out of its block bounds'),
            ('0:2', 'Narrow', 'Used for window edges and other narrow surfaces at the side of the block'),
            ('1:2', 'Thin', 'Used for catwalks and other thin mountpoints at the side of the block'),
            ('3:3', 'Central', 'Mountpoint in the center of a side but not its edges, used on Sensors, Cameras, Interior Lights etc'),
            ('custom', 'Custom', 'Define custom values for the Exclusion and Properties Mask')
            ),
        default='0:0',
        update=update_mask_preset
    )

    exclusion_mask: IntProperty(
        name="Exclusion Mask",
        description="",
        default=0,
        min=0,
        max=255
    )

    properties_mask: IntProperty(
        name="Properties Mask",
        description="",
        default=0,
        min=0,
        max=255
    )

    # Particles
    particle_id: IntProperty(
        name="Particle ID",
        description="The unique ID of this particle effect",
        min=0
    )
    particle_length: FloatProperty(
        name="Length",
        description="Length of the effect in seconds",
        min=0,
        unit='TIME'
    )
    particle_preload: IntProperty(
        name="Preload",
        description="TBD",
        default=0
    )
    particle_lowres: BoolProperty(
        name="Low Resolution",
        description="TBD",
        default=False
    )
    particle_loop: BoolProperty(
        name="Loop",
        description="Whether the effect is shown continuously",
        default=True
    )
    particle_duration_min: FloatProperty(
        name="Duration Min",
        description="The minimum duration of the effect in seconds",
        min=0,
        unit='TIME'
    )
    particle_duration_max: FloatProperty(
        name="Duration Max",
        description="The maximum duration of the effect in seconds",
        min=0,
        unit='TIME'
    )
    particle_version: IntProperty(
        name="Version",
        description="The current version of the particle effect",
        min=0
    )
    particle_priority: FloatProperty(
        name="Priority",
        description="TBD"
    )
    particle_distance_max: IntProperty(
        name="Distance Max",
        description="TBD",
        min=0,
        default=500
    )