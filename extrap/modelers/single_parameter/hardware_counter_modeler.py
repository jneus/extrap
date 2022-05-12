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
from extrap.entities.functions import WeigthedFunction
from extrap.entities.metric import Metric
from extrap.entities.hypotheses import HardwareCounterHypothesis, Hypothesis, SingleParameterHypothesis
from extrap.entities.callpath import Callpath
from extrap.modelers.abstract_modeler import AbstractModeler
from extrap.modelers.single_parameter.basic import SingleParameterModeler

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
        self.counter_list = [
            "PAPI_TOT_INS",
            "PAPI_LST_INS",
            "PAPI_LD_INS",
            "PAPI_SR_INS",
            "PAPI_BR_INS",
            "PAPI_DP_OPS",
            "PAPI_SP_OPS",
            "PAPI_VEC_DP",
            "PAPI_VEC_SP",
            "PAPI_TLB_IM",
            "PAPI_TLB_DM"
        ]
        self.coordinates = {}
        self.global_counter_data = {}
        self.counter_weights = {}

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
            current_metric = str(callpath[0].metric)
            if current_metric in counter_data:
                counter_data[current_metric] = list(map(lambda x: x[0] + x[1].mean, zip(counter_data[current_metric], callpath)))
                
        return counter_data

    def determine_counter_weights(self, measurements):
        weights = {}
        weight_modeler = SingleParameterModeler()
        tot_ins = self.global_counter_data["PAPI_TOT_INS"]
        for counter in self.global_counter_data:
            if counter != "PAPI_TOT_INS":
                weight_values = list(map(lambda x: x[0]/x[1], zip(self.global_counter_data[counter], tot_ins)))
                weight_measurements = [
                    Measurement(
                        coordinate=coord, 
                        callpath=Callpath(""),
                        metric=Metric("weight"), 
                        values=weight_values) for coord in self.coordinates
                ]
                weight_model = weight_modeler.create_model(weight_measurements)
                weight_model.measurements = weight_measurements
                weights[counter] = weight_model
        return weights

    def accumulate_callpath_data(self, measurements: Sequence[Sequence[Measurement]]) -> dict:
        callpath_data = {}
        for measurement_sequence in measurements:
            callpath = measurement_sequence[0].callpath
            metric = measurement_sequence[0].metric
            if str(metric) in self.counter_list:
                if not callpath in callpath_data:
                    callpath_data[callpath] = []
                callpath_data[callpath].append(measurement_sequence)
        return callpath_data

    def create_weight_hypothesis(self, models):
        functions = []
        weight_terms = []
        for model in models:
            functions.append(model.hypothesis.function)
            if str(model.metric) not in self.counter_weights:
                raise RuntimeError(f"Cannot assign weight to metric {model.metric}. Metric not in self.counter_list.")
            weight_model = self.counter_weights[str(model.metric)]
            weight_terms.append(weight_model.hypothesis.function)
        
        weight_function = WeigthedFunction(functions, weight_terms)
        hypothesis = HardwareCounterHypothesis(weight_function, self.use_median)
        return hypothesis

    def model(self, measurements: Sequence[Sequence[Measurement]], progress_bar:...) -> Sequence[Model]:
        self.coordinates = [measurement.coordinate for measurement in measurements[0]]
        self.global_counter_data = self.accumulate_counter_data(measurements)
        self.counter_weights = self.determine_counter_weights(measurements)

        callpath_counter_data = self.accumulate_callpath_data(measurements)
        counter_weight_distribution = {}
        callpath_models = {}
        single_param_modeler = SingleParameterModeler()
        runtime_models = []
        
        for callpath, data in progress_bar(callpath_counter_data.items()):
            callpath_models[callpath] = []
            for counter_data in data:
                callpath_model = single_param_modeler.create_model(counter_data)
                callpath_model.callpath = callpath
                callpath_model.metric = counter_data[0].metric
                callpath_model.measurements = counter_data
                if str(callpath_model.metric) != "PAPI_TOT_INS":
                    callpath_models[callpath].append(callpath_model)
            hypothesis = self.create_weight_hypothesis(callpath_models[callpath])
            #hypothesis = SingleParameterHypothesis(weight_callpath_function, self.use_median)
            runtime_model = Model(hypothesis, callpath=callpath, metric=Metric("time"))
            runtime_models.append(runtime_model)
        
        return runtime_models
            


        
