# This file is part of the Extra-P software (http://www.scalasca.org/software/extra-p)
#
# Copyright (c) 2022, Technical University of Darmstadt, Germany
#
# This software may be modified and distributed under the terms of a BSD-style license.
# See the LICENSE file in the base directory for details.

from itertools import accumulate
from subprocess import call
import warnings
import numpy as np

from typing import Sequence, Optional, Tuple
from extrap.entities import measurement

from extrap.entities.measurement import Measurement
from extrap.entities.model import Model
from extrap.entities.functions import Function, WeigthedFunction
from extrap.modelers.abstract_modeler import AbstractModeler
from extrap.modelers.modeler_options import modeler_options
from extrap.modelers.single_parameter.basic import SingleParameterModeler
from extrap.util.classproperty import classproperty

class HardwareCounterModeler(AbstractModeler):
    NAME = 'Hardware-Counter'
    DESCRIPTION = 'Creates a runtime model based on data of hardware performance counters'
    
    counter_data = {}

    def __init__(self):
        """
        Initialize HardwareCounterModeler object.
        """
        super().__init__(use_median=False)

        self.min_measurement_points = 5

    def accumulate_counter_data(self, measurements: Sequence[Sequence[Measurement]]) -> dict:
        measurements_per_sequence = len(measurements[0])

        counter_data = {
            "PAPI_TOT_INS": [0] * measurements_per_sequence,
            "PAPI_LST_INS": [0] * measurements_per_sequence,
            "PAPI_LD_INS": [0] * measurements_per_sequence,
            "PAPI_SR_INS": [0] * measurements_per_sequence,
            "PAPI_BR_INS": [0] * measurements_per_sequence,
            "PAPI_DP_OPS": [0] * measurements_per_sequence,
            "PAPI_VEC_DP": [0] * measurements_per_sequence,
            "PAPI_SP_OPS": [0] * measurements_per_sequence,
            "PAPI_VEC_SP": [0] * measurements_per_sequence,
            "PAPI_TLB_IM": [0] * measurements_per_sequence,
            "PAPI_TLB_DM": [0] * measurements_per_sequence,
        }

        for callpath in measurements:
            #print(tuple(zip([1,2,3,4,5], callpath)))
            current_metric = str(callpath[0].metric)
            #print(type(current_metric))
            if current_metric in counter_data:
                counter_data[current_metric] = list(map(lambda x: x[0] + x[1].mean, zip(counter_data[current_metric], callpath)))
                #print(current_metric + str(counter_data[current_metric]))
            # for measurement in callpath:
            #     if measurement.metric in counter_data:
            #         pass
        # print(counter_data["PAPI_LST_INS"])
        # print(counter_data["PAPI_LD_INS"])
        # print(counter_data["PAPI_SR_INS"])
        # print([x + y for x, y in zip(counter_data["PAPI_LD_INS"], counter_data["PAPI_SR_INS"])])
        return counter_data

    def determine_counter_weights(self, counter_data):
        pass

    def accumulate_callpath_data(self, measurements: Sequence[Sequence[Measurement]]) -> dict:
        callpath_data = {}
        for measurement_sequence in measurements:
            callpath = measurement_sequence[0].callpath
            if not callpath in callpath_data:
                callpath_data[callpath] = []
            
            callpath_data[callpath].append(measurement_sequence)
        return callpath_data

    def create_function_weight_mapping(self, *models) -> Tuple(Sequence[Function], Sequence[float]):
        pass

    def model(self, measurements: Sequence[Sequence[Measurement]], progress_bar:...) -> Sequence[Model]:
        counter_data = self.accumulate_counter_data(measurements)
        callpath_counter_data = self.accumulate_callpath_data(measurements)
        counter_weight_distribution = {}
        callpath_models = {}
        single_param_modeler = SingleParameterModeler()
        runtime_models = []
        
        for callpath, data in progress_bar(callpath_counter_data.items()):
            callpath_models[callpath] = []
            for counter_data in data:
                callpath_models[callpath].append(single_param_modeler.create_model(counter_data))
            


        
