# Copyright 2021 The ChengduSuperComputingCenter Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Author: JayFu
# ==============================================================================

import numpy as np
import importlib, os
from cosyai.dataset.base import _BaseDataset
from cosyai.util import check_config_none, config


class Segy2dSet(_BaseDataset):
    def __init__(self, conf, preprocess):
        super().__init__(conf)
        self.X = preprocess.traces
        self.Y = preprocess.labels
        check_config_none(conf, ["input_dim", "output_dim", "dataset_size"])
        if conf.data_format == 'img':
            num = 239
        else:
            num = conf.dataset_size
            # TODO change num
        self._create(conf.task, conf.input_dim, conf.output_dim,
                     num, conf.path,
                     conf.split_weight)
        self._transform(conf.backend)

    def _read_memmap(self):
        raise NotImplementedError

    def _create(self,
               task,
               input_dim,
               output_dim,
               num,
               path,
               split_weight):

        split_weight = split_weight or [7, 1, 2]

        indices = np.cumsum(
            np.asarray(split_weight) * num / np.sum(split_weight), dtype=int)
        self.train_set = self.X[:indices[0]], self.Y[:indices[0]]
        self.eval_set = self.X[indices[0]:indices[1]], self.Y[indices[0]:indices[1]]
        self.test_set = self.X[indices[1]:], self.Y[indices[1]:]

    def _transform(self, backend):
        module = importlib.import_module('cosyai.backend.' + backend +
                                                   '.util')
        self.train_set = module.data_transformer(*self.train_set)
        self.eval_set = module.data_transformer(*self.eval_set)
        self.test_set = module.data_transformer(*self.test_set)
