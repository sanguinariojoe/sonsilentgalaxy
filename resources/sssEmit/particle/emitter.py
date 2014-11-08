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
from . import particle


POINT_ALTERNATIVES = ('CENTER', 'VERTEX', 'MESH')
DIR_ALTERNATIVES = ('Z', 'Y', 'X', 'z', 'y', 'x', 'NORMAL')


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
        f = path.join(folder, "sssEmit/scripts/sss_emitter.py")
        if not path.isfile(f):
            continue
        filepath = f
        break
    if not filepath:
        raise Exception('I can not find the script file "sss_emitter.py"')

    # We can try to update it, and if the operation fails is just because the
    # file has not been loaded yet
    try:
        text = bpy.data.texts['sss_emitter.py']
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


def addProperty(name, type_id, value):
    """Test if a property exist in the object, adding it otherwise.

    Keyword arguments:
    name -- Property name
    type_id -- Type of property
    value -- Property value
    """
    obj = bpy.context.object
    if not name in obj.game.properties.keys():
        bpy.ops.object.game_property_new()
        obj.game.properties[-1].name = name
        obj.game.properties[name].type = type_id
        obj.game.properties[name].value = value


def delProperty(name):
    """Remove a property from the object if it exist.

    Keyword arguments:
    name -- Property name
    """
    obj = bpy.context.object
    if not name in obj.game.properties.keys():
        return

    for i, p in enumerate(obj.game.properties):
        if p.name == name:
            bpy.ops.object.game_property_remove(i)
            return


def generateProperties():
    """Ensure that the object has the required properties."""
    addProperty('t', 'TIMER', 0.0)
    addProperty('culling', 'BOOL', True)
    addProperty('culling_radius', 'FLOAT', 0.0)
    addProperty('is_lifetime', 'BOOL', False)
    addProperty('lifetime', 'FLOAT', 0.0)
    addProperty('rate', 'FLOAT', 30.0)
    addProperty('point', 'STRING', POINT_ALTERNATIVES[0])
    addProperty('direction', 'STRING', DIR_ALTERNATIVES[0])
    addProperty('direction_var', 'FLOAT', 0.0)
    addProperty('velocity', 'FLOAT', 0.0)
    addProperty('velocity_var', 'FLOAT', 0.0)
    addProperty('particle', 'STRING', '')


def removeProperties():
    """Remove the properties the object."""
    delProperty('culling')
    delProperty('culling_radius')
    delProperty('is_lifetime')
    delProperty('lifetime')
    delProperty('rate')
    delProperty('point')
    delProperty('direction')
    delProperty('direction_var')
    delProperty('velocity')
    delProperty('velocity_var')
    delProperty('particle')


def updateValues():
    """Update the particles emitter values."""
    generateProperties()
    loadScript()

    obj = bpy.context.object
    obj.game.properties['culling'].value = obj.frustrum_culling
    obj.game.properties['culling_radius'].value = obj.frustrum_radius

    obj.game.properties['is_lifetime'].value = obj.is_lifetime
    obj.game.properties['lifetime'].value = obj.lifetime
    obj.game.properties['rate'].value = obj.rate

    obj.game.properties['point'].value = POINT_ALTERNATIVES[int(obj.point)]
    # We must modify the direction alternatives depending on the selected
    # generation point, due to the mesh normal option will be available if
    # the object center is not selected
    modes = [('0', 'Global Z', 'Global Z direction'),
             ('1', 'Global Y', 'Global Y direction'),
             ('2', 'Global X', 'Global X direction'),
             ('3', 'Local Z', 'Local Z direction'),
             ('4', 'Local Y', 'Local Y direction'),
             ('5', 'Local X', 'Local X direction'),
             ('6', 'Mesh normal', ('Take the normal of the mesh in the'
                                   ' generation point'))]
    if int(obj.point) == 0:
        modes = modes[:-1]
    if int(obj.dir) >= len(modes):
        obj.dir = str(3)  # Default option
    bpy.types.Object.dir = bpy.props.EnumProperty(
        name=bpy.types.Object.dir[1]['name'],
        items=modes,
        default=obj.dir,
        update=bpy.types.Object.dir[1]['update'],
        description=bpy.types.Object.dir[1]['description'])
    obj.game.properties['direction'].value = DIR_ALTERNATIVES[int(obj.dir)]
    obj.game.properties['direction_var'].value = math.radians(obj.dir_var)
    obj.game.properties['velocity'].value = obj.vel
    obj.game.properties['velocity_var'].value = obj.vel_var


def generateObjectProperties(update_callback):
    """Generate the Blender object properties.

    Position arguments:
    update_callback -- Function that must be called when the object is
    modified. It must be included into a bpy.types.Panel class.
    """
    bpy.types.Object.emitter = bpy.props.BoolProperty(default=False)
    bpy.types.Object.draw_type_back = bpy.props.StringProperty()

    bpy.types.Object.frustrum_culling = bpy.props.BoolProperty(
        default=False,
        update=update_callback,
        description=('Allows you to disable the Emitter automatically if it'
                     ' is not viewable (in the camera frustrum)'))
    bpy.types.Object.frustrum_radius = bpy.props.FloatProperty(
        default=0.0,
        min=0,
        update=update_callback,
        description='Distance to the emitter where it is considered'
        ' viewable')

    bpy.types.Object.is_lifetime = bpy.props.BoolProperty(
        default=False,
        update=update_callback,
        description='Should be the emitter destroyed after some time?')
    bpy.types.Object.lifetime = bpy.props.FloatProperty(
        default=0.0,
        min=0.0,
        update=update_callback,
        description='Particles emission time (after this time the object will'
        ' be removed from the escene).')

    bpy.types.Object.rate = bpy.props.FloatProperty(
        default=30.0,
        min=0.0,
        update=update_callback,
        description='Particle emission rate (Hz)')

    modes = [('0', 'Object center', ('The particles are generated in the'
                                     ' center of the emitter object')),
             ('1', 'Random mesh vertex', ('Each particle is generated in a'
                                          'randomly selected mesh vertex')),
             ('2', 'Random point in the mesh', ('Each particle is generated'
                                                'in a randomly selected mesh'
                                                ' point'))]
    bpy.types.Object.point = bpy.props.EnumProperty(
        name="Particles generation point",
        items=modes,
        default='0',
        update=update_callback,
        description="Set the points where a particle can be generated")
    modes = [('0', 'Global Z', 'Global Z direction'),
             ('1', 'Global Y', 'Global Y direction'),
             ('2', 'Global X', 'Global X direction'),
             ('3', 'Local Z', 'Local Z direction'),
             ('4', 'Local Y', 'Local Y direction'),
             ('5', 'Local X', 'Local X direction'),
             ('6', 'Mesh normal', ('Take the normal of the mesh in the'
                                   ' generation point'))]
    # Since the default option is the object center emission, mesh normal
    # option should not be available
    modes = modes[:-1]
    bpy.types.Object.dir = bpy.props.EnumProperty(
        name="Particles generation direction",
        items=modes,
        default='3',
        update=update_callback,
        description="Set the direction for the generated particles")
    bpy.types.Object.dir_var = bpy.props.FloatProperty(
        default=0.0,
        min=0.0,
        update=update_callback,
        description='Direction random variation')
    bpy.types.Object.vel = bpy.props.FloatProperty(
        default=0.0,
        update=update_callback,
        description='Initial velocity')
    bpy.types.Object.vel_var = bpy.props.FloatProperty(
        default=0.0,
        min=0.0,
        update=update_callback,
        description='Initial velocity random variation')


def draw(context, layout):
    """Draw the emitter stuff.

    Position arguments:
    context -- Calling context.
    layout -- Window layout assigned for the emitter.
    """
    obj = bpy.context.object

    row = layout.row()
    row.label("Emitter settings", icon='GREASEPENCIL')

    row = layout.row()
    row.prop(context.object,
             "frustrum_culling",
             text="Frustum based culling")
    if(obj.frustrum_culling):
        row.prop(context.object,
                 "frustrum_radius",
                 text="Radius")

    row = layout.row()
    row.prop(context.object,
             "is_lifetime",
             text="Emitter lifetime")
    if(obj.is_lifetime):
        row.prop(context.object,
                 "lifetime",
                 text="")

    row = layout.row()
    row.prop(context.object,
             "rate",
             text="Emission rate")

    row = layout.row()
    row.label(text="Emission point:")
    row = layout.row()
    row.prop(context.object,
             "point",
             text="")

    row = layout.row()
    row.label(text="Emission direction:")
    row = layout.row()
    row.prop(context.object,
             "dir",
             text="")
    row.label(text="+-")
    row.prop(context.object,
             "dir_var",
             text="")
    row.label(text="degrees")

    row = layout.row()
    row.label(text="Initial velocity:")
    row = layout.row()
    row.prop(context.object,
             "vel",
             text="")
    row.label(text="+-")
    row.prop(context.object,
             "vel_var",
             text="")
    row.label(text="m/s")


class create_emitter(bpy.types.Operator):
    bl_idname = "scene.create_emitter"
    bl_label = "Transform into an emitter"
    bl_description = "Transform the object into an emitter"

    def createLogic(self):
        obj = bpy.context.object
        bpy.context.active_object.draw_type = 'WIRE'
        # One time execution
        bpy.ops.logic.sensor_add(type='ALWAYS', name="sssEmit.init", object="")
        obj.game.sensors[-1].frequency = 0
        obj.game.sensors[-1].use_pulse_true_level = False
        bpy.ops.logic.controller_add(type='PYTHON', name="sssEmit.pyinit", object="")
        obj.game.controllers[-1].mode = 'MODULE'
        obj.game.controllers[-1].module = 'sss_emitter.load'
        obj.game.controllers[-1].link(obj.game.sensors[-1])
        # Per frame executing
        bpy.ops.logic.sensor_add(type='ALWAYS', name="sssEmit.update", object="")
        obj.game.sensors[-1].frequency = 0
        obj.game.sensors[-1].use_pulse_true_level = True
        bpy.ops.logic.controller_add(type='PYTHON', name="sssEmit.pyupdate", object="")
        obj.game.controllers[-1].mode = 'MODULE'
        obj.game.controllers[-1].module = 'sss_emitter.update'
        obj.game.controllers[-1].link(obj.game.sensors[-1])

        # Add a controller to reference the script (but never used). It is
        # useful if the object will be imported from other blender file,
        # inserting the script in the importer scene
        bpy.ops.logic.controller_add(type='PYTHON',
                                     name="sssEmit.reference",
                                     object="")
        text = None
        for t in bpy.data.texts:
            if t.name == 'sss_emitter.py':
                text = t
                break
        if text is None:
            raise Exception('The script "sss_emitter.py is not loaded"')
        obj.game.controllers[-1].mode = 'SCRIPT'
        obj.game.controllers[-1].text = text

    def execute(self, context):
        obj = bpy.context.active_object

        obj.emitter = True
        obj.draw_type_back = obj.draw_type
        obj.draw_type = 'WIRE'
        generateProperties()
        loadScript()
        self.createLogic()

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = obj
        bpy.context.scene.objects[obj.name].select = True

        part_name = particle.create_particle()
        obj.game.properties['particle'].value = part_name

        return{'FINISHED'}


class remove_emitter(bpy.types.Operator):
    bl_idname = "object.remove_emitter"
    bl_label = "Remove the emitter"
    bl_description = "Remove the object emitter stuff"

    def del_particle_logic(self):
        obj = bpy.context.active_object
        bpy.ops.logic.sensor_remove(sensor="Always",
                                    object=obj.name)
        bpy.ops.logic.controller_remove(controller="Python",
                                        object=obj.name)
        bpy.ops.logic.controller_remove(controller="Reference",
                                        object=obj.name)

    def execute(self, context):
        obj = bpy.context.active_object

        particle.remove_particle()

        obj.emitter = False
        obj.draw_type = obj.draw_type_back
        removeProperties()
        self.del_particle_logic()

        return{'FINISHED'}
