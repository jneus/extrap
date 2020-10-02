# This file is part of the Extra-P software (http://www.scalasca.org/software/extra-p)
#
# Copyright (c) 2020, Technical University of Darmstadt, Germany
#
# This software may be modified and distributed under the terms of a BSD-style license.
# See the LICENSE file in the base directory for details.

import numpy as np
from marshmallow import fields, post_load

from extrap.entities.callpath import Callpath, CallpathSchema
from extrap.entities.coordinate import Coordinate, CoordinateSchema
from extrap.entities.metric import Metric, MetricSchema
from extrap.util.deprecation import deprecated
from extrap.util.serialization_schema import Schema, NumberField


class Measurement:
    """
    This class represents a measurement, i.e. the value measured for a specific metric and callpath at a coordinate.
    """

    def __init__(self, coordinate: Coordinate, callpath: Callpath, metric: Metric, values):
        """
        Initialize the Measurement object.
        """
        self.coordinate: Coordinate = coordinate
        self.callpath: Callpath = callpath
        self.metric: Metric = metric
        if values is None:
            return
        values = np.array(values)
        self.median: float = np.median(values)
        self.mean: float = np.mean(values)
        self.minimum: float = np.min(values)
        self.maximum: float = np.max(values)
        self.std: float = np.std(values)

    def value(self, use_median):
        return self.median if use_median else self.mean

    @deprecated("Use callpath instead.")
    def get_callpath_id(self):
        """
        Return the callpath id of the measurement.
        """
        return self.callpath.id

    @deprecated("Use metric instead.")
    def get_metric_id(self):
        """
        Return the metric id of the measurement.
        """
        return self.metric.id

    @deprecated("Use coordinate instead.")
    def get_coordinate_id(self):
        """
        Return the coordinate id of the measurement.
        """
        return self.coordinate.id

    @deprecated("Use mean property instead.")
    def get_value_mean(self):
        """
        Return the mean measured value.
        """
        return self.mean

    @deprecated("Use median property instead.")
    def get_value_median(self):
        """
        Return the median measured value.
        """
        return self.median

    @deprecated("Use mean property instead.")
    def set_value_mean(self, value_mean):
        """
        Set the mean measured value to the given value.
        """
        self.mean = value_mean

    @deprecated("Use median property instead.")
    def set_value_median(self, value_median):
        """
        Set the median measured value to the given value.
        """
        self.median = value_median

    def __repr__(self):
        return f"Measurement({self.coordinate}: {self.mean:0.6} median={self.median:0.6})"

    def __eq__(self, other):
        if not isinstance(other, Measurement):
            return False
        elif self is other:
            return True
        else:
            return self.coordinate == other.coordinate and \
                   self.metric == other.metric and \
                   self.callpath == other.callpath and \
                   self.mean == other.mean and \
                   self.median == other.median


class MeasurementSchema(Schema):
    coordinate = fields.Nested(CoordinateSchema)
    metric = fields.Nested(MetricSchema)
    callpath = fields.Nested(CallpathSchema)
    median = NumberField()
    mean = NumberField()
    minimum = NumberField()
    maximum = NumberField()
    std = NumberField()

    @post_load
    def report_progress(self, data, **kwargs):
        if 'progress_bar' in self.context:
            self.context['progress_bar'].update()
        return data

    def create_object(self):
        return Measurement(None, None, None, None)
