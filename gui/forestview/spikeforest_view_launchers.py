from .spikeforest_views.currentstateview import CurrentStateView
from .spikeforest_views.recordingtableview import RecordingTableView
from .recording_views.electrodegeometryview import ElectrodeGeometryView
from .recording_views.timeseriesview import TimeseriesView
from .recording_views.templatesview import TemplatesView
from .recording_views.recordingsummaryview import RecordingSummaryView
from .recording_views.unitstableview import UnitsTableView
from .recording_views.sortingresultstableview import SortingResultsTableView

def get_spikeforest_view_launchers(context):
    launchers=[]
    groups=[]
    ret = dict(
        groups=groups,
        launchers=launchers
    )

    # General
    groups.append(dict(name='general',label=''))

    launchers.append(dict(
        group='general', name='recording-table', label='Recording table',
        view_class=RecordingTableView,
        context=context, opts=dict(),
        enabled=True
    ))
    launchers.append(dict(
        group='general', name='current-state', label='Current state',
        view_class=CurrentStateView,
        context=context, opts=dict(),
        enabled=True
    ))
    
    recording_context = context.recordingContext(context.currentRecordingId())

    # Recording
    if recording_context:
        groups.append(dict(name='recording',label='Recording'))
    
        launchers.append(dict(
            group='recording', name='recording-summary', label='Recording summary',
            view_class=RecordingSummaryView,
            context=recording_context, opts=dict(),
            enabled=(recording_context is not None)
        ))
        launchers.append(dict(
            group='recording', name='electrode-geometry', label='Electrode geometry',
            view_class=ElectrodeGeometryView,
            context=recording_context, opts=dict(),
            enabled=(recording_context is not None)
        ))
        launchers.append(dict(
            group='recording', name='timeseries', label='Timeseries',
            view_class=TimeseriesView,
            context=recording_context, opts=dict(),
            enabled=(recording_context is not None)
        ))
        if recording_context.hasIntraRecording():
            launchers.append(dict(
                group='recording', name='intra-timeseries', label='Intra-timeseries',
                view_class=TimeseriesView,
                context=recording_context.intraRecordingContext(),
                opts=dict(),
                enabled=(recording_context is not None)
            ))
        launchers.append(dict(
            group='recording', name='sorting-results-table', label='Sorting results table',
            view_class=SortingResultsTableView,
            context=recording_context, opts=dict(),
            enabled=(len(recording_context.sortingResultNames()) > 0)
        ))

    # True sorting
    if recording_context and recording_context.trueSortingContext():
        true_sorting_context = recording_context.trueSortingContext()

        groups.append(dict(name='true-sorting',label='True sorting'))
        launchers.append(dict(
            group='true-sorting', name='true-templates', label='Templates',
            view_class=TemplatesView,
            context=true_sorting_context, opts=dict(),
            enabled=(true_sorting_context is not None)
        ))
        launchers.append(dict(
            group='true-sorting', name='true-units-info', label='Units info',
            view_class=UnitsTableView,
            context=true_sorting_context, opts=dict(),
            enabled=(true_sorting_context is not None)
        ))
    
        dict(name='unit',label='Unit')
        launchers.append(dict(
            group='true-sorting', name='test', label='Test',
            view_class=TemplatesView,
            context=true_sorting_context, opts=dict(),
            enabled=(true_sorting_context.currentUnitId() is not None)
        ))

    # True sorting
    if recording_context and recording_context.currentSortingResult():
        srname = recording_context.currentSortingResult()
        sorting_result_context = recording_context.sortingResultContext(srname)

        groups.append(dict(name='sorting-result',label='Sorting result ({})'.format(srname)))
        launchers.append(dict(
            group='sorting-result', name='templates', label='Templates',
            view_class=TemplatesView,
            context=sorting_result_context, opts=dict(),
            enabled=(true_sorting_context is not None)
        ))
        launchers.append(dict(
            group='sorting-result', name='units-info', label='Units info',
            view_class=UnitsTableView,
            context=sorting_result_context, opts=dict(),
            enabled=(sorting_result_context is not None)
        ))
    
        dict(name='unit',label='Unit')
        launchers.append(dict(
            group='sorting-result', name='test', label='Test',
            view_class=TemplatesView,
            context=sorting_result_context, opts=dict(),
            enabled=(sorting_result_context.currentUnitId() is not None)
        ))
    
    
    return ret
