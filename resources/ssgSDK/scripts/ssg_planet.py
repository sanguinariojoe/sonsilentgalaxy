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


# We should compute a convenient G
M = 1.0
r = 10.0
rpm = 6.0

w = rpm * 2.0 * math.pi / 60.0
a = r * w**2
G = a * r**2 / M  # ~395 vs 6.67*10**-11


class ssgPlanet(bge.types.KX_GameObject):
    def __init__(self, obj):
        self['mass'] = self.mass

    def typeName(self):
        return 'ssgPlanet'

    def gravity(self):
        grav = mathutils.Vector((0.0, 0.0, 0.0))
        r_a = self.worldPosition
        scene = g.getCurrentScene()
        objlist = scene.objects
        for obj in objlist:
            # Discard self detection
            if obj == self:
                continue
            # Analyze just planets or stars
            if not hasattr(obj, 'typeName'):
                continue
            if not obj.typeName() in ('ssgStar', 'ssgPlanet'):
                continue
            # Compute the gravity caused by this object
            m = obj['mass']
            r_b = obj.worldPosition
            v = r_b - r_a
            r = v.length
            v /= r
            grav += G * m / r**2 * v
        return grav

    def update(self):
        self.applyForce(self.gravity() * self.mass)