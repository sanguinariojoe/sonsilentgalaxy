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
import mathutils
import math
import random


POINT_ALTERNATIVES = ('CENTER', 'VERTEX', 'MESH')
DIR_ALTERNATIVES = ('Z', 'Y', 'X', 'z', 'y', 'x', 'NORMAL')


def loadColors(obj):
    """Try to load and store the original color of all the children objects"""
    for c in obj.children:
        try:
            c['color'] = c.color.xyz
        except:
            continue


def loadAlphas(obj):
    """Try to load and store the original alpha of all the children objects"""
    for c in obj.children:
        try:
            c['alpha'] = c.color.w
        except:
            continue


def load():
    """Method called one time at the emitter generation"""
    cont = g.getCurrentController()
    obj = cont.owner
    scene = g.getCurrentScene()
    cam = scene.active_camera

    if obj['billboard']:
        obj.worldOrientation = cam.worldOrientation

    if obj['is_scale_fade']:
        obj['scale'] = obj.localScale.xyz

    if obj['is_color_fade']:
        obj['color_fade'] = mathutils.Vector((obj['color_fade.r'],
                                              obj['color_fade.g'],
                                              obj['color_fade.b']))
        loadColors(obj)
    if obj['is_alpha_fade']:
        loadAlphas(obj)


def lifetime(obj):
    """Test the object lifetime"""
    if not obj['is_lifetime']:
        return
    if obj['t'] >= obj['lifetime']:
        obj.endObject()


def scaleFade(obj):
    """Perform the scale fade if it is required"""
    if not obj['is_scale_fade']:
        return
    t = max(obj['t'] - obj['scale_fade_in'], 0.0)
    T = obj['scale_fade_out'] - obj['scale_fade_in']
    f = t/T
    if f > 1.0:
        f = 1.0
        obj['is_scale_fade'] = False
    s = f * obj['scale_fade'] + (1.0 - f)
    obj.localScale = s * obj['scale']


def colorFade(obj):
    """Perform the color fade if it is required"""
    if not obj['is_color_fade']:
        return
    t = max(obj['t'] - obj['color_fade_in'], 0.0)
    T = obj['color_fade_out'] - obj['color_fade_in']
    f = t/T
    if f > 1.0:
        f = 1.0
        obj['is_color_fade'] = False
    ff = 1.0 - f
    for c in obj.children:
        try:
            c.color.xyz = f * obj['color_fade'] + ff * c['color']
        except:
            continue


def alphaFade(obj):
    """Perform the alpha fade if it is required"""
    if not obj['is_alpha_fade']:
        return
    t = max(obj['t'] - obj['alpha_fade_in'], 0.0)
    T = obj['alpha_fade_out'] - obj['alpha_fade_in']
    f = t/T
    if f > 1.0:
        f = 1.0
        obj['is_alpha_fade'] = False
    ff = 1.0 - f
    for c in obj.children:
        try:
            c.color.w = f * obj['alpha_fade'] + ff * c['alpha']
        except:
            continue


def update():
    """Method called each frame while the emitter exist"""
    cont = g.getCurrentController()
    obj = cont.owner
    scene = g.getCurrentScene()
    cam = scene.active_camera

    if obj['billboard']:
        obj.worldOrientation = cam.worldOrientation

    # Fades
    scaleFade(obj)
    colorFade(obj)
    alphaFade(obj)

    # Test if the object must end
    lifetime(obj)

    return
