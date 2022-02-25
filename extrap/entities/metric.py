# This file is part of the Extra-P software (http://www.scalasca.org/software/extra-p)
#
# Copyright (c) 2020-2022, Technical University of Darmstadt, Germany
#
# This software may be modified and distributed under the terms of a BSD-style license.
# See the LICENSE file in the base directory for details.

import itertools

from extrap.entities.named_entity import NamedEntityWithTags, NamedEntityWithTagsSchema


class Metric(NamedEntityWithTags):
    """
    This class represents a metric such as time or FLOPS.
    """
    TYPENAME = "Metric"

    ID_COUNTER = itertools.count()
    """
    Counter for global metric ids
    """


class MetricSchema(NamedEntityWithTagsSchema):
    def create_object(self):
        return Metric('')
