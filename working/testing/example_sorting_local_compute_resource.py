#!/usr/bin/env python

# IMPORTANT: before running this example, you must start a local compute resource via:
# > compute-resource-start local-test --parallel 4

import spikeforest_analysis as sa
from mountaintools import client as mt
from spikeforest import example_datasets
from spikeforest import SFMdaRecordingExtractor, SFMdaSortingExtractor
import os
import shutil
import sfdata as sf
import numpy as np
import pytest


def main():
    # specify the compute resource
    # You will need to first start this local compute resource as described above
    compute_resource = dict(
        resource_name='local-test',
        collection='',
        share_id=''
    )

    # generate toy recordings
    if not os.path.exists('recordings'):
        os.mkdir('recordings')

    delete_recordings = False

    recpath = 'recordings/example1'
    if os.path.exists(recpath) and (delete_recordings):
        shutil.rmtree(recpath)
    if not os.path.exists(recpath):
        rx, sx_true = example_datasets.toy_example1(
            duration=60, num_channels=4, samplerate=30000, K=10)
        SFMdaRecordingExtractor.write_recording(
            recording=rx, save_path=recpath)
        SFMdaSortingExtractor.write_sorting(
            sorting=sx_true, save_path=recpath + '/firings_true.mda')

    # for downloading containers if needed
    mt.configDownloadFrom(['spikeforest.spikeforest2'])

    # Use this to control whether we force the processing to re-run (by default it uses cached results)
    os.environ['MLPROCESSORS_FORCE_RUN'] = 'FALSE'  # FALSE or TRUE

    # This is the id of the output -- for later retrieval by GUI's, etc
    output_id = 'toy_example_local'

    # Grab the recordings for testing
    recordings = [
        dict(
            recording_name='example1',
            study_name='toy_examples',
            directory=os.path.abspath('recordings/example1')
        )
    ]

    recordings = recordings * 10

    studies = [
        dict(
            name='toy_examples',
            study_set='toy_examples',
            directory=os.path.abspath('recordings'),
            description='Toy examples.'
        )
    ]

    # Sorters (algs and params) are defined below
    sorters = _define_sorters()

    # We will be assembling the sorting results here
    sorting_results = []

    for sorter in sorters:
        # Sort the recordings
        compute_resource0 = compute_resource
        sortings = sa.sort_recordings(
            sorter=sorter,
            recordings=recordings,
            compute_resource=compute_resource0
        )

        # Append to results
        sorting_results = sorting_results + sortings

    # Summarize the sortings
    sorting_results = sa.summarize_sortings(
        sortings=sorting_results,
        compute_resource=compute_resource
    )

    # Compare with ground truth
    sorting_results = sa.compare_sortings_with_truth(
        sortings=sorting_results,
        compute_resource=compute_resource
    )

    # Save the output
    print('Saving the output')
    mt.saveObject(
        key=dict(
            name='spikeforest_results'
        ),
        subkey=output_id,
        object=dict(
            studies=studies,
            recordings=recordings,
            sorting_results=sorting_results
        )
    )


def _define_sorters():
    sorter_ms4_thr3 = dict(
        name='MountainSort4-thr3',
        processor_name='MountainSort4',
        params=dict(
            detect_sign=-1,
            adjacency_radius=50,
            detect_threshold=3
        )
    )

    # sorter_irc_tetrode = dict(
    #     name='IronClust-tetrode',
    #     processor_name='IronClust',
    #     params=dict(
    #         detect_sign=-1,
    #         adjacency_radius=50,
    #         detect_threshold=5,
    #         prm_template_name="tetrode_template.prm"
    #     )
    # )

    # sorter_irc_drift = dict(
    #     name='IronClust-drift',
    #     processor_name='IronClust',
    #     params=dict(
    #         detect_sign=-1,
    #         adjacency_radius=50,
    #         prm_template_name="drift_template.prm"
    #     )
    # )

    # sorter_irc_static = dict(
    #     name='IronClust-static',
    #     processor_name='IronClust',
    #     params=dict(
    #         detect_sign=-1,
    #         adjacency_radius=50,
    #         prm_template_name="static_template.prm"
    #     )
    # )

    # def sorter_irc_template(prm_template_name):
    #     sorter_irc = dict(
    #         name='IronClust-{}'.format(prm_template_name),
    #         processor_name='IronClust',
    #         params=dict(
    #             detect_sign=-1,
    #             adjacency_radius=50,
    #             prm_template_name="{}_template.prm".format(prm_template_name)
    #         )
    #     )
    #     return sorter_irc

    # sorter_sc = dict(
    #     name='SpykingCircus',
    #     processor_name='SpykingCircus',
    #     params=dict(
    #         detect_sign=-1,
    #         adjacency_radius=50
    #     )
    # )

    # sorter_ks = dict(
    #     name='KiloSort',
    #     processor_name='KiloSort',
    #     params=dict(
    #         detect_sign=-1,
    #         adjacency_radius=50
    #     )
    # )
    # return [sorter_ms4_thr3, sorter_sc, sorter_irc_static]
    # return [sorter_ms4_thr3, sorter_sc, sorter_irc_static]
    return [sorter_ms4_thr3]


if __name__ == "__main__":
    main()
