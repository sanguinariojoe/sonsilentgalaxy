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


def load():
    """Method called one time at the emitter generation"""
    cont = g.getCurrentController()
    obj = cont.owner
    obj['t'] = 0.0  # Emitter lifetime
    obj['pending'] = 0.0  # Number of pending particles to be emitted
    return


def testFrustrum(obj):
    """Test if the object is unactive due to the frsutrum culling"""
    scene = g.getCurrentScene()
    cam = scene.active_camera

    p = obj.worldPosition
    r = obj['culling_radius']
    if obj['culling'] and cam.sphereInsideFrustum(p, r) == cam.OUTSIDE:
        return False
    return True

def getVertexes(obj):
    """Get the vertexes of an object"""
    vertexes = []
    for mesh in obj.meshes:
        for m_index in range(len(mesh.materials)):
            for v_index in range(mesh.getVertexArrayLength(m_index)):
                vertex = mesh.getVertex(m_index, v_index)
                vertexes.append(vertex)
    return vertexes


def meshVertex(obj):
    """Select the emission point and the normal in the vertex mode"""
    v = getVertexes(obj)
    if not v:
        obj['point'] = POINT_ALTERNATIVES[0]
        raise ValueError(
            'Vertex emmision mode selected, but no vertexes found in the'
            ' object (the emission point will be moved to the center)')
    
    i = random.randrange(len(v))
    p = mathutils.Vector(v[i].XYZ)
    n = mathutils.Vector(v[i].normal)

    return p, n


def getPolygons(obj):
    """Get the polygons of an object"""
    polygons = []
    for mesh in obj.meshes:
        for p_index in range(mesh.numPolygons):
            polygon = mesh.getPolygon(p_index)
            polygons.append(polygon)
    return polygons


def meshPoint(obj):
    """Select the emission point and the normal"""
    p = getPolygons(obj)
    if not p:
        obj['point'] = POINT_ALTERNATIVES[0]
        raise ValueError(
            'Polygon emmision mode selected, but no polygons found in the'
            ' object (the emission point will be moved to the center)')

    # Select a random polygon
    p = p[random.randrange(len(p))]

    # Get the vertexes
    m = p.getMesh()
    v = []
    for i in range(p.getNumVertex()):
        m_index = p.getMaterialIndex()
        v_index = p.getVertexIndex(i)
        v.append(m.getVertex(m_index, v_index))

    # Give random weights to the vertexes (normalized)
    norm = 1.0
    weights = []
    for i in range(len(v)):
        weights.append(random.uniform(0.0, norm))
        norm -= weights[-1]
    weights[-1] += norm
    random.shuffle(weights)

    # Compute the averaged value
    p = mathutils.Vector((0.0, 0.0, 0.0))
    n = mathutils.Vector((0.0, 0.0, 0.0))
    for i in range(len(v)):
        p += weights[i]*mathutils.Vector(v[i].XYZ)
        n += weights[i]*mathutils.Vector(v[i].normal)

    return p, n


def point(obj):
    """Select the emission point and the normal"""
    if obj['point'] not in POINT_ALTERNATIVES:
        obj['point'] = POINT_ALTERNATIVES[0]

    if obj['point'] == POINT_ALTERNATIVES[0]:
        return obj.worldPosition, mathutils.Vector((0.0, 0.0, 0.0))

    elif obj['point'] == POINT_ALTERNATIVES[1]:
        p, n = meshVertex(obj)
        p = obj.localOrientation * p + obj.worldPosition
        n = obj.localOrientation * n
        return p,n

    p, n = meshPoint(obj)
    p = obj.localOrientation * p + obj.worldPosition
    n = obj.localOrientation * n
    return p,n


def velocity(obj, n):
    """Select the initial particle velocity"""
    if obj['direction'] not in DIR_ALTERNATIVES:
        obj['direction'] = DIR_ALTERNATIVES[3]

    vel = mathutils.Vector((0.0, 0.0, 0.0))
    if obj['direction'] == DIR_ALTERNATIVES[0]:
        vel = mathutils.Vector((0.0, 0.0, 1.0))
        vel.rotate(mathutils.Euler((
            random.uniform(-obj['direction_var'], obj['direction_var']),
            0.0,
            random.uniform(0, 2.0 * math.pi)),
            'XYZ'))
    elif obj['direction'] == DIR_ALTERNATIVES[1]:
        vel = mathutils.Vector((0.0, 1.0, 0.0))
        vel.rotate(mathutils.Euler((
            random.uniform(-obj['direction_var'], obj['direction_var']),
            random.uniform(0, 2.0 * math.pi),
            0.0),
            'XYZ'))
    elif obj['direction'] == DIR_ALTERNATIVES[2]:
        vel = mathutils.Vector((1.0, 0.0, 0.0))
        vel.rotate(mathutils.Euler((
            random.uniform(0, 2.0 * math.pi),
            0.0,
            random.uniform(-obj['direction_var'], obj['direction_var'])),
            'ZYX'))
    if obj['direction'] == DIR_ALTERNATIVES[3]:
        vel = mathutils.Vector((0.0, 0.0, 1.0))
        vel.rotate(mathutils.Euler((
            random.uniform(-obj['direction_var'], obj['direction_var']),
            0.0,
            random.uniform(0, 2.0 * math.pi)),
            'XYZ'))
        vel = obj.getAxisVect(vel)
    elif obj['direction'] == DIR_ALTERNATIVES[4]:
        vel.rotate(mathutils.Euler((
            random.uniform(-obj['direction_var'], obj['direction_var']),
            random.uniform(0, 2.0 * math.pi),
            0.0),
            'XYZ'))
        vel = obj.getAxisVect(vel)
    elif obj['direction'] == DIR_ALTERNATIVES[5]:
        vel = mathutils.Vector((1.0, 0.0, 0.0))
        vel.rotate(mathutils.Euler((
            random.uniform(0, 2.0 * math.pi),
            0.0,
            random.uniform(-obj['direction_var'], obj['direction_var'])),
            'ZYX'))
        vel = obj.getAxisVect(vel)
    elif obj['direction'] == DIR_ALTERNATIVES[6]:
        vel = mathutils.Vector((0.0, 0.0, 1.0))
        diff = vel.rotation_difference(n)
        vel.rotate(mathutils.Euler((
            random.uniform(-obj['direction_var'], obj['direction_var']),
            0.0,
            random.uniform(0, 2.0 * math.pi)),
            'XYZ'))
        vel.rotate(diff)

    norm = obj['velocity'] + random.uniform(-obj['velocity_var'],
                                            obj['velocity_var'])

    return norm*vel


def initialValues(obj):
    """Compute the initial values for the particle"""
    p, n = point(obj)
    v = velocity(obj, n)
    return p, v


def generateParticle(obj):
    """Generate a particle from the emitter"""
    scene = g.getCurrentScene()
    cam = scene.active_camera

    part = scene.addObject(obj['particle'], obj, 0)

    p, v = initialValues(obj)
    part.worldPosition = p
    part.setLinearVelocity(v)
    if part['billboard']:
        part.worldOrientation = cam.worldOrientation


    obj['pending'] -= 1.0
    return


def lifetime(obj):
    """Test the object lifetime"""
    if not obj['is_lifetime']:
        return
    if obj['t'] >= obj['lifetime']:
        obj.endObject()


def update():
    """Method called each frame while the emitter exist"""
    cont = g.getCurrentController()
    obj = cont.owner

    # Test if we must not work due to the frustrum based culling
    if not testFrustrum(obj):
        return

    # Targeted number of particles and remaining ones to achieve it
    dt = 1.0/g.getLogicTicRate()
    obj['pending'] += dt * obj['rate']

    while(obj['pending'] >= 1.0):
        generateParticle(obj)

    # Test if the object must end
    lifetime(obj)

    return
