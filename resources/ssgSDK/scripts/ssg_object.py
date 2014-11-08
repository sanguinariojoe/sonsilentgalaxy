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
import @SCRIPT_NAME@


def load():
    """ Initializates the bullet object, conviniently mutating it """
    controller = g.getCurrentController()
    old_object = controller.owner
    mutated_object = @SCRIPT_NAME@.@CLASS_NAME@(controller.owner)

    # After calling the constructor above, references to the old object
    # should not be used.
    assert(old_object is not mutated_object)
    assert(old_object.invalid)
    assert(mutated_object is controller.owner)


def update():
    """ Test if the bullet has crashed against the water,
    and call to the operators after the explosion.
    @note Call this method each frame
    """
    controller = g.getCurrentController()
    obj = controller.owner
    obj.update()
