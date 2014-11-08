##############################################################################
#                                                                            #
#  This file is part of SonSilentSea, a free ships based combatr game.       #
#  Copyright (C) 2014  Jose Luis Cercos Pita <jlcercos@gmail.com>            #
#                                                                            #
#  AQUAgpusph is free software: you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by      #
#  the Free Software Foundation, either version 3 of the License, or         #
#  (at your option) any later version.                                       #
#                                                                            #
#  AQUAgpusph is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#  GNU General Public License for more details.                              #
#                                                                            #
#  You should have received a copy of the GNU General Public License         #
#  along with AQUAgpusph.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                            #
##############################################################################

import bpy
import math
import mathutils
from os import path


def scriptPaths():
    """Return all the possible locations for the scripts."""
    paths = bpy.utils.script_paths(check_all=True)
    paths.append(path.join(bpy.utils.resource_path('USER'), 'scripts'))
    paths.append(path.join(bpy.utils.resource_path('LOCAL'), 'scripts'))
    paths.append(path.join(bpy.utils.resource_path('SYSTEM'), 'scripts'))
    return paths


def addonsPaths():
    """ Return all the possible locations for the addons """
    paths = []
    for folder in scriptPaths():
        f = path.join(folder, 'addons')
        if path.isdir(f):
            paths.append(f)
        f = path.join(folder, 'addons_extern')
        if path.isdir(f):
            paths.append(f)
    return paths


def loadScript():
    """Load/update the text script in text editor."""
    filepath = None
    for folder in addonsPaths():
        f = path.join(folder, "sssEmit/scripts/sss_particle.py")
        if not path.isfile(f):
            continue
        filepath = f
        break
    if not filepath:
        raise Exception('I can not find the script file "sss_particle.py"')

    # We can try to update it, and if the operation fails is just because the
    # file has not been loaded yet
    try:
        text = bpy.data.texts['sss_particle.py']
        text.clear()
        f = open(filepath, 'r')
        text.write(f.read())
        f.close()
    except:
        bpy.ops.text.open(filepath=filepath,
                          filter_blender=False,
                          filter_image=False,
                          filter_movie=False,
                          filter_python=True,
                          filter_font=False,
                          filter_sound=False,
                          filter_text=True,
                          filter_btx=False,
                          filter_collada=False,
                          filter_folder=True,
                          filemode=9,
                          internal=True)


def getParticle():
    """Get the particle object"""
    name = bpy.context.active_object.game.properties['particle'].value
    return bpy.context.scene.objects[name]


def addProperty(name, type_id, value, obj=None):
    """Test if a property exist in the object, adding it otherwise.

    Keyword arguments:
    name -- Property name
    type_id -- Type of property
    value -- Property value
    """
    if obj is None:
        obj = getParticle()

    # We must select the object before
    obj_backup = bpy.context.active_object
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = obj
    obj.select = True

    if not name in obj.game.properties.keys():
        bpy.ops.object.game_property_new()
        obj.game.properties[-1].name = name
        obj.game.properties[name].type = type_id
        obj.game.properties[name].value = value

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = obj_backup
    obj_backup.select = True


def delProperty(name, obj=None):
    """Remove a property from the object if it exist.

    Keyword arguments:
    name -- Property name
    """
    if obj is None:
        obj = getParticle()
    if not name in obj.game.properties.keys():
        return

    # We must select the object before
    obj_backup = bpy.context.active_object
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = obj
    obj.select = True

    for i, p in enumerate(obj.game.properties):
        if p.name == name:
            bpy.ops.object.game_property_remove(i)
            break

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = obj_backup
    obj_backup.select = True


def generateProperties(obj=None):
    """Ensure that the object has the required properties."""
    if obj is None:
        obj = getParticle()
    addProperty('t', 'TIMER', 0.0, obj)
    addProperty('billboard', 'BOOL', True, obj)
    addProperty('is_lifetime', 'BOOL', False, obj)
    addProperty('lifetime', 'FLOAT', 0.0, obj)
    addProperty('is_scale_fade', 'BOOL', False, obj)
    addProperty('scale_fade', 'FLOAT', 1.0, obj)
    addProperty('scale_fade_in', 'FLOAT', 0.0, obj)
    addProperty('scale_fade_out', 'FLOAT', 0.0, obj)
    addProperty('is_color_fade', 'BOOL', False, obj)
    addProperty('color_fade.r', 'FLOAT', 1.0, obj)
    addProperty('color_fade.g', 'FLOAT', 1.0, obj)
    addProperty('color_fade.b', 'FLOAT', 1.0, obj)
    addProperty('color_fade_in', 'FLOAT', 0.0, obj)
    addProperty('color_fade_out', 'FLOAT', 0.0, obj)
    addProperty('is_alpha_fade', 'BOOL', False, obj)
    addProperty('alpha_fade', 'FLOAT', 1.0, obj)
    addProperty('alpha_fade_in', 'FLOAT', 0.0, obj)
    addProperty('alpha_fade_out', 'FLOAT', 0.0, obj)


def removeProperties(obj=None):
    """Remove the properties the object."""
    if obj is None:
        obj = getParticle()
    delProperty('t')
    delProperty('billboard')
    delProperty('is_lifetime')
    delProperty('lifetime')
    delProperty('is_scale_fade')
    delProperty('scale_fade')
    delProperty('scale_fade_in')
    delProperty('scale_fade_out')
    delProperty('is_color_fade')
    delProperty('color_fade.r')
    delProperty('color_fade.g')
    delProperty('color_fade.b')
    delProperty('color_fade_in')
    delProperty('color_fade_out')
    delProperty('is_alpha_fade')
    delProperty('alpha_fade')
    delProperty('alpha_fade_in')
    delProperty('alpha_fade_out')


def updateValues():
    """Update the particles emitter values."""
    generateProperties()
    loadScript()

    obj = getParticle()
    emit = bpy.context.object

    obj.game.properties['billboard'].value = emit.billboard
    obj.game.properties['is_lifetime'].value = emit.is_part_lifetime
    obj.game.properties['lifetime'].value = emit.part_lifetime
    obj.game.properties['is_scale_fade'].value = emit.is_scale_fade
    obj.game.properties['scale_fade'].value = emit.scale_fade
    obj.game.properties['scale_fade_in'].value = emit.scale_fade_in
    # The minimum value of the scale fade out must be greater than the
    # scale fade in one
    min_fade_out = emit.scale_fade_in + 0.001
    fade_out = max(emit.scale_fade_out, min_fade_out)
    obj.game.properties['scale_fade_out'].value = fade_out
    bpy.types.Object.scale_fade_out = bpy.props.FloatProperty(
        default=fade_out,
        min=min_fade_out,
        precision=bpy.types.Object.scale_fade_out[1]['precision'],
        update=bpy.types.Object.scale_fade_out[1]['update'],
        description=bpy.types.Object.scale_fade_out[1]['description'])
    obj.game.properties['is_color_fade'].value = emit.is_color_fade
    obj.game.properties['color_fade.r'].value = emit.color_fade.r
    obj.game.properties['color_fade.g'].value = emit.color_fade.g
    obj.game.properties['color_fade.b'].value = emit.color_fade.b
    obj.game.properties['color_fade_in'].value = emit.color_fade_in
    # The minimum value of the color fade out must be greater than the
    # color fade in one
    min_fade_out = emit.color_fade_in + 0.001
    fade_out = max(emit.color_fade_out, min_fade_out)
    obj.game.properties['color_fade_out'].value = fade_out
    bpy.types.Object.color_fade_out = bpy.props.FloatProperty(
        default=fade_out,
        min=min_fade_out,
        precision=bpy.types.Object.color_fade_out[1]['precision'],
        update=bpy.types.Object.color_fade_out[1]['update'],
        description=bpy.types.Object.color_fade_out[1]['description'])
    obj.game.properties['is_alpha_fade'].value = emit.is_alpha_fade
    obj.game.properties['alpha_fade'].value = emit.alpha_fade
    obj.game.properties['alpha_fade_in'].value = emit.alpha_fade_in
    # The minimum value of the alpha fade out must be greater than the
    # alpha fade in one
    min_fade_out = emit.alpha_fade_in + 0.001
    fade_out = max(emit.alpha_fade_out, min_fade_out)
    obj.game.properties['alpha_fade_out'].value = fade_out
    bpy.types.Object.alpha_fade_out = bpy.props.FloatProperty(
        default=fade_out,
        min=min_fade_out,
        precision=bpy.types.Object.alpha_fade_out[1]['precision'],
        update=bpy.types.Object.alpha_fade_out[1]['update'],
        description=bpy.types.Object.alpha_fade_out[1]['description'])


def generateObjectProperties(update_callback):
    """Generate the Blender object properties.

    Position arguments:
    update_callback -- Function that must be called when the object is
    modified. It must be included into a bpy.types.Panel class.
    """
    bpy.types.Object.billboard = bpy.props.BoolProperty(
        default=True,
        update=update_callback,
        description=('Set the orientation of the particle such that it will'
                     ' look at the camera all the time (with the local z)'))
    bpy.types.Object.is_part_lifetime = bpy.props.BoolProperty(
        default=False,
        update=update_callback,
        description='Should be the particle destroyed after some time?')
    bpy.types.Object.part_lifetime = bpy.props.FloatProperty(
        default=0.0,
        min=0.0,
        update=update_callback,
        description='Particle lifetime.')
    bpy.types.Object.is_scale_fade = bpy.props.BoolProperty(
        default=False,
        update=update_callback,
        description='Should be the particle scale changed along the time?')
    bpy.types.Object.scale_fade = bpy.props.FloatProperty(
        default=1.0,
        min=0.0,
        update=update_callback,
        description='Final scale (relative factor to the original one).')
    bpy.types.Object.scale_fade_in = bpy.props.FloatProperty(
        default=0.0,
        min=0.0,
        precision=3,
        update=update_callback,
        description='Fade start instant.')
    bpy.types.Object.scale_fade_out = bpy.props.FloatProperty(
        default=0.0,
        min=0.001,
        precision=3,
        update=update_callback,
        description='Fade end instant.')
    bpy.types.Object.is_color_fade = bpy.props.BoolProperty(
        default=False,
        update=update_callback,
        description='Should be the particle color changed along the time?')
    bpy.types.Object.color_fade = bpy.props.FloatVectorProperty(
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        step=1,
        precision=3,
        subtype='COLOR_GAMMA',
        size=3,
        update=update_callback,
        description='Final color.')
    bpy.types.Object.color_fade_in = bpy.props.FloatProperty(
        default=0.0,
        min=0.0,
        precision=3,
        update=update_callback,
        description='Fade start instant.')
    bpy.types.Object.color_fade_out = bpy.props.FloatProperty(
        default=0.0,
        min=0.001,
        precision=3,
        update=update_callback,
        description='Fade end instant.')
    bpy.types.Object.is_alpha_fade = bpy.props.BoolProperty(
        default=False,
        update=update_callback,
        description='Should be the alpha transparency changed along the time?')
    bpy.types.Object.alpha_fade = bpy.props.FloatProperty(
        default=1.0,
        min=0.0,
        update=update_callback,
        description='Final alpha.')
    bpy.types.Object.alpha_fade_in = bpy.props.FloatProperty(
        default=0.0,
        min=0.0,
        precision=3,
        update=update_callback,
        description='Fade start instant.')
    bpy.types.Object.alpha_fade_out = bpy.props.FloatProperty(
        default=0.0,
        min=0.001,
        precision=3,
        update=update_callback,
        description='Fade end instant.')


def draw(context, layout):
    """Draw the particle stuff.

    Position arguments:
    context -- Calling context.
    layout -- Window layout assigned for the emitter.
    """
    row = layout.row()
    row.label("Particle settings", icon='GREASEPENCIL')

    row = layout.row()
    row.prop(context.object,
             "billboard",
             text="Billboard")

    row = layout.row()
    row.prop(context.object,
             "is_part_lifetime",
             text="Particle lifetime")
    if(context.object.is_part_lifetime):
        row.prop(context.object,
                 "part_lifetime",
                 text="")

    row = layout.row()
    row.prop(context.object,
             "is_scale_fade",
             text="Particle scale fade")
    if(context.object.is_scale_fade):
        row.prop(context.object,
                 "scale_fade",
                 text="")
        row = layout.row()
        row.prop(context.object,
                 "scale_fade_in",
                 text="in")
        row.prop(context.object,
                 "scale_fade_out",
                 text="out")

    row = layout.row()
    row.prop(context.object,
             "is_color_fade",
             text="Particle color fade")
    if(context.object.is_color_fade):
        row.prop(context.object,
                 "color_fade",
                 text="")
        row = layout.row()
        row.prop(context.object,
                 "color_fade_in",
                 text="in")
        row.prop(context.object,
                 "color_fade_out",
                 text="out")
    row = layout.row()
    row.prop(context.object,
             "is_alpha_fade",
             text="Particle alpha fade")
    if(context.object.is_alpha_fade):
        row.prop(context.object,
                 "alpha_fade",
                 text="")
        row = layout.row()
        row.prop(context.object,
                 "alpha_fade_in",
                 text="in")
        row.prop(context.object,
                 "alpha_fade_out",
                 text="out")


def createLogic(obj=None):
    if obj is None:
        obj = getParticle()

    # One time execution
    bpy.ops.logic.sensor_add(type='ALWAYS', name="sssParticle.init", object=obj.name)
    obj.game.sensors[-1].frequency = 0
    obj.game.sensors[-1].use_pulse_true_level = False
    bpy.ops.logic.controller_add(type='PYTHON', name="sssParticle.pyinit", object=obj.name)
    obj.game.controllers[-1].mode = 'MODULE'
    obj.game.controllers[-1].module = 'sss_particle.load'
    obj.game.controllers[-1].link(obj.game.sensors[-1])
    # Per frame executing
    bpy.ops.logic.sensor_add(type='ALWAYS', name="sssParticle.update", object=obj.name)
    obj.game.sensors[-1].frequency = 0
    obj.game.sensors[-1].use_pulse_true_level = True
    bpy.ops.logic.controller_add(type='PYTHON', name="sssParticle.pyupdate", object=obj.name)
    obj.game.controllers[-1].mode = 'MODULE'
    obj.game.controllers[-1].module = 'sss_particle.update'
    obj.game.controllers[-1].link(obj.game.sensors[-1])

    # Add a controller to reference the script (but never used). It is
    # useful if the object will be imported from other blender file,
    # inserting the script in the importer scene
    bpy.ops.logic.controller_add(type='PYTHON',
                                 name="sssParticle.reference",
                                 object=obj.name)
    text = None
    for t in bpy.data.texts:
        if t.name == 'sss_particle.py':
            text = t
            break
    if text is None:
        raise Exception('The script "sss_particle.py is not loaded"')
    obj.game.controllers[-1].mode = 'SCRIPT'
    obj.game.controllers[-1].text = text


def createPhysics(obj=None):
    if obj is None:
        obj = getParticle()

    obj.game.physics_type = 'RIGID_BODY'
    obj.game.use_actor = False
    obj.game.use_ghost = True
    mask = [False]*8
    mask[-2] = True
    obj.game.collision_group = mask
    mask = [False]*8
    mask[-1] = True
    obj.game.collision_mask = mask    


def create_particle():
    """Create a particle object in the last layer, and return its name"""
    obj_backup = bpy.context.active_object
    basename = obj_backup.name
    layers = [False]*20
    layers[-1] = True
    bpy.ops.object.empty_add(type='ARROWS', layers=layers)
    obj = bpy.context.active_object

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = obj_backup
    bpy.context.scene.objects[obj_backup.name].select = True

    obj.name = basename + ".sssemit_particle"

    generateProperties(obj)
    loadScript()
    createLogic(obj)
    createPhysics(obj)

    return obj.name


def remove_particle():
    """Remove the particle object associated with the emitter"""
    # To delete the object we need to select it before
    obj_backup = bpy.context.active_object
    name = bpy.context.active_object.game.properties['particle'].value
    obj = bpy.context.scene.objects[name]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = obj
    obj.select = True

    # We also need to move to its active layer
    layers = bpy.context.scene.layers[:]
    bpy.context.scene.layers = obj.layers

    bpy.ops.object.delete()

    # Now we can restore the old selection and layers
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = obj_backup
    obj_backup.select = True
    bpy.context.scene.layers = layers
