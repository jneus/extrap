# This file is part of the Extra-P software (http://www.scalasca.org/software/extra-p)
#
# Copyright (c) 2020-2022, Technical University of Darmstadt, Germany
#
# This software may be modified and distributed under the terms of a BSD-style license.
# See the LICENSE file in the base directory for details.

import itertools

from extrap.entities.named_entity import NamedEntityWithTags, NamedEntityWithTagsSchema


class Callpath(NamedEntityWithTags):
    """
    This class represents a callpath of an application.
    """

    TYPENAME = 'Callpath'

    ID_COUNTER = itertools.count()
    """
    Counter for global callpath ids
    """

    EMPTY: 'Callpath'
    """
    Empty callpath. Can be used as placeholder.
    """


class CallpathSchema(NamedEntityWithTagsSchema):
    def create_object(self):
        return Callpath('')

