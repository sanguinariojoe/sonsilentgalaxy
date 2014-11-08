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

import bge
from bge import logic as g
import math
import mathutils
import os
from os import path

M = 1.0
r = 10.0
rpm = 6.0

w = rpm * 2.0 * math.pi / 60.0
a = r * w**2
G = a * r**2 / M

# Get the owner (should be the camera)
cont = bge.logic.getCurrentController()
own  = cont.owner

# Get the general scene
scene = g.getCurrentScene()


def _locate_resource(file_name):
        if path.isabs(file_name):
            return file_name
        # Default paths
        paths = [path.join(sys.prefix,'share/sonsilentsea/resources'),
                            path.join(path.abspath('./'),'resources'),
                            path.expanduser('~/.sonsilentsea/resources')]
        # Look for the file in the paths
        for p in paths:
            file_path = path.join(p,file_name)
            if path.isfile(file_path):
                return file_path
        return None


def load_blender_file(file_name):
        """ Loads a blender file.
        @param file_name An absolute path to the file, or if a relative path such that
        the file will be looked for in the mission folder, in the user home resources folder,
        in the execution folder, or finally in the installation folder.
        @remarks Full scene will be loaded by default.
        """
        # Locate the file
        file_path = _locate_resource(file_name)
        if not file_path:
            return
        # Load it
        status = g.LibLoad(file_path, 'Scene', load_actions=True, verbose=True, load_scripts=True)


# We will add the objects in the scene origin, and move later
objlist = scene.objects
origin  = objlist.get('Origin')
if not origin:
    raise Exception("Can't find the object 'Origin'")
        
print('Loading Sun object...')
load_blender_file('entities/sun.blend')
active = scene.objects
inactive = scene.objectsInactive
if (not 'Sun' in active) and (not 'Sun' in inactive):
    raise Exception('FAIL! The file was not loaded')

if 'Sun' in inactive:
    sun = scene.addObject('Sun', origin)
else:
    sun = active['Sun']
print('OK!')

print('Loading Earth object...')
load_blender_file('entities/earth.blend')
active = scene.objects
inactive = scene.objectsInactive
if (not 'Earth' in active) and (not 'Earth' in inactive):
    raise Exception('FAIL! The file was not loaded')

if 'Earth' in inactive:
    earth = scene.addObject('Earth', origin)
else:
    earth = active['Earth']

r = 10.0
rpm = 6.0
w = rpm * 2.0 * math.pi / 60.0
k = 1.5  # Desviacion eliptica de la orbita
# k = 2.5

r_earth = k * r
v_earth = w * r / k

earth.worldPosition = mathutils.Vector((r_earth, 0.0, 0.0))
earth.setLinearVelocity(mathutils.Vector((0.0, v_earth, 0.0)))

# Colocamos la camara en el medio del afelio
own.worldPosition.x = 0.5 * r_earth

"""
print('Loading Moon object...')
load_blender_file('entities/moon.blend')
active = scene.objects
inactive = scene.objectsInactive
if (not 'Moon' in active) and (not 'Moon' in inactive):
    raise Exception('FAIL! The file was not loaded')
if 'Moon' in inactive:
    moon = scene.addObject('Moon', origin)
else:
    moon = active['Moon']

r = 2.5
a = G * earth.mass / r**2
w = a / r**2

moon.worldPosition = mathutils.Vector((r_earth - r, 0.0, 0.0))
moon.setLinearVelocity(mathutils.Vector((0.0, v_earth + w * r, 0.0)))

print('OK!')
"""