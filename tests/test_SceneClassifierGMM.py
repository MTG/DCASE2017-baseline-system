""" Unit tests for SceneClassifierGMM """

import nose.tools
import sys
sys.path.append('..')
import json
import os
from dcase_framework.features import FeatureContainer
from dcase_framework.metadata import MetaDataItem
from dcase_framework.learners import SceneClassifierGMM
import tempfile
from IPython import embed


def test_learn():
    feature_container = FeatureContainer(filename=os.path.join('material', 'test.mfcc.cpickle'))

    data = {
        'file1.wav': feature_container,
        'file2.wav': feature_container,
    }

    annotations = {
        'file1.wav': MetaDataItem(
            {
                'file': 'file1.wav',
                'scene_label': 'scene1',
            }
        ),
        'file2.wav': MetaDataItem(
            {
                'file': 'file2.wav',
                'scene_label': 'scene2',
            }
        ),
    }

    sc = SceneClassifierGMM(
        method='gmm',
        class_labels=['scene1', 'scene2'],
        params={
            'n_components': 6,
            'covariance_type': 'diag',
            'tol': 0.001,
            'reg_covar': 0,
            'max_iter': 40,
            'n_init': 1,
            'init_params': 'kmeans',
            'random_state': 0,
        },
        filename=os.path.join('material', 'test.model.cpickle'),
        disable_progress_bar=True,
    )

    sc.learn(data=data, annotations=annotations)

    # Test model count
    nose.tools.eq_(len(sc.model), 2)

    # Test model dimensions
    nose.tools.eq_(sc.model['scene1'].means_.shape[0], 6)


def test_predict():
    feature_container = FeatureContainer(filename=os.path.join('material', 'test.mfcc.cpickle'))

    data = {
        'file1.wav': feature_container,
        'file2.wav': feature_container,
    }

    annotations = {
        'file1.wav': MetaDataItem(
            {
                'file': 'file1.wav',
                'scene_label': 'scene1',
            }
        ),
        'file2.wav': MetaDataItem(
            {
                'file': 'file2.wav',
                'scene_label': 'scene2',
            }
        ),
    }

    sc = SceneClassifierGMM(
        method='gmm',
        class_labels=['scene1', 'scene2'],
        params={
            'n_components': 6,
            'covariance_type': 'diag',
            'tol': 0.001,
            'reg_covar': 0,
            'max_iter': 40,
            'n_init': 1,
            'init_params': 'kmeans',
            'random_state': 0,
        },
        filename=os.path.join('material', 'test.model.cpickle'),
        disable_progress_bar=True,
    )

    sc.learn(data=data, annotations=annotations)
    recognizer_params = {
        'frame_accumulation': {
            'enable': True,
            'type': 'sum',
        },
        'frame_binarization': {
            'enable': False,
        },
        'decision_making': {
            'enable': True,
            'type': 'maximum',
        }
    }
    result = sc.predict(
        feature_data=feature_container,
        recognizer_params=recognizer_params
    )

    # Test result
    nose.tools.eq_(result, 'scene1')

    # Test errors
    recognizer_params['frame_accumulation']['type'] = 'test'
    nose.tools.assert_raises(AssertionError, sc.predict, feature_container, recognizer_params)

    recognizer_params['frame_accumulation']['type'] = 'sum'
    recognizer_params['decision_making']['type'] = 'test'
    nose.tools.assert_raises(AssertionError, sc.predict, feature_container, recognizer_params)