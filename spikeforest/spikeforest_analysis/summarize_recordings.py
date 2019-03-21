try:
    # if we are running this outside the container
    from spikeforest import spikeextractors as si
except:
    # if we are in the container
    import spikeextractors as si

# from spikeforest import spikewidgets as sw
import json
import time
from PIL import Image
import os
from copy import deepcopy
from mountaintools import client as mt
import mlprocessors as mlpr
import multiprocessing
# from matplotlib import pyplot as plt
from .compute_units_info import ComputeUnitsInfo
import mtlogging

_CONTAINER='sha1://87319c2856f312ccc3187927ae899d1d67b066f9/03-20-2019/mountaintools_basic.simg'

def _gather_summarized_recording_helper(kwargs):
    return _gather_summarized_recording(**kwargs)

def _gather_summarized_recording(recording, job_info, job_units_info):
    # firings_true_path = recording['directory']+'/firings_true.mda'
    summary=dict()
    
    result0=job_info.result
    summary['computed_info']=mt.loadObject(path=result0.outputs['json_out'])
    
    summary['plots']=dict()

    result0=job_units_info.result
    summary['true_units_info']=mt.saveFile(path=result0.outputs['json_out'],basename='true_units_info.json')

    rec2=deepcopy(recording)
    rec2['summary']=summary
    
    return rec2

@mtlogging.log()
def summarize_recordings(recordings, compute_resource=None):
    print('>>>>>> summarize recordings')

    jobs_info = ComputeRecordingInfo.createJobs([
        dict(
          recording_dir=recording['directory'],
          channels=recording.get('channels',[]),
          json_out={'ext':'.json','upload':True},
          _container='default'
        )
        for recording in recordings
    ])

    jobs_units_info = ComputeUnitsInfo.createJobs([
        dict(
          recording_dir=recording['directory'],
          firings=recording['directory']+'/firings_true.mda',
          unit_ids=recording.get('units_true',None),
          channel_ids=recording.get('channels',None),
          json_out={'ext':'.json','upload':True},
          _container='default'
        )
        for recording in recordings
    ])
    
    # all_jobs=jobs_info+jobs_timeseries_plot+jobs_units_info
    all_jobs=jobs_info+jobs_units_info
    label='Summarize recordings'
    mlpr.executeBatch(jobs=all_jobs,label=label,num_workers=None,compute_resource=compute_resource)

    print('Gathering summarized recordings...')

    pool = multiprocessing.Pool(20)
    summarized_recordings=pool.map(_gather_summarized_recording_helper, [dict(recording=recordings[ii], job_info=jobs_info[ii], job_units_info=jobs_units_info[ii]) for ii in range(len(recordings))])
    pool.close()
    pool.join()

    return summarized_recordings

def read_json_file(fname):
  with open(fname) as f:
    return json.load(f)
  
def write_json_file(fname,obj):
  with open(fname, 'w') as f:
    json.dump(obj, f)

# A MountainLab processor for generating the summary info for a recording
class ComputeRecordingInfo(mlpr.Processor):
  NAME='ComputeRecordingInfo'
  VERSION='0.1.1'
  CONTAINER=_CONTAINER

  recording_dir=mlpr.Input(directory=True,description='Recording directory')
  channels=mlpr.IntegerListParameter(description='List of channels to use.',optional=True,default=[])
  json_out=mlpr.Output('Info in .json file')
    
  def run(self):
    ret={}
    recording=si.MdaRecordingExtractor(dataset_directory=self.recording_dir,download=True)
    if len(self.channels)>0:
      recording=si.SubRecordingExtractor(parent_recording=recording,channel_ids=self.channels)
    ret['samplerate']=recording.getSamplingFrequency()
    ret['num_channels']=len(recording.getChannelIds())
    ret['duration_sec']=recording.getNumFrames()/ret['samplerate']
    write_json_file(self.json_out,ret)

# def save_plot(fname,quality=40):
#     plt.savefig(fname+'.png')
#     plt.close()
#     im=Image.open(fname+'.png').convert('RGB')
#     os.remove(fname+'.png')
#     im.save(fname,quality=quality)

# # A MountainLab processor for generating a plot of a portion of the timeseries
# class CreateTimeseriesPlot(mlpr.Processor):
#   NAME='CreateTimeseriesPlot'
#   VERSION='0.1.7'
#   CONTAINER=_CONTAINER
#   recording_dir=mlpr.Input(directory=True,description='Recording directory')
#   channels=mlpr.IntegerListParameter(description='List of channels to use.',optional=True,default=[])
#   jpg_out=mlpr.Output('The plot as a .jpg file')
  
#   def run(self):
#     R0=si.MdaRecordingExtractor(dataset_directory=self.recording_dir,download=True)
#     if len(self.channels)>0:
#       R0=si.SubRecordingExtractor(parent_recording=R0,channel_ids=self.channels)
#     R=sw.lazyfilters.bandpass_filter(recording=R0,freq_min=300,freq_max=6000)
#     N=R.getNumFrames()
#     N2=int(N/2)
#     channels=R.getChannelIds()
#     if len(channels)>20: channels=channels[0:20]
#     sw.TimeseriesWidget(recording=R,trange=[N2-4000,N2+0],channels=channels,width=12,height=5).plot()
#     save_plot(self.jpg_out)

# # A MountainLab processor for generating a plot of a portion of the timeseries
# class CreateWaveformsPlot(mlpr.Processor):
#   NAME='CreateWaveformsPlot'
#   VERSION='0.1.1'
#   CONTAINER=_CONTAINER
#   recording_dir=mlpr.Input(directory=True,description='Recording directory')
#   channels=mlpr.IntegerListParameter(description='List of channels to use.',optional=True,default=[])
#   units=mlpr.IntegerListParameter(description='List of units to use.',optional=True,default=[])
#   firings=mlpr.Input(description='Firings file')
#   jpg_out=mlpr.Output('The plot as a .jpg file')
  
#   def run(self):
#     R0=si.MdaRecordingExtractor(dataset_directory=self.recording_dir,download=True)
#     if len(self.channels)>0:
#       R0=si.SubRecordingExtractor(parent_recording=R0,channel_ids=self.channels)
#     R=sw.lazyfilters.bandpass_filter(recording=R0,freq_min=300,freq_max=6000)
#     S=si.MdaSortingExtractor(firings_file=self.firings)
#     channels=R.getChannelIds()
#     if len(channels)>20:
#       channels=channels[0:20]
#     if len(self.units)>0:
#       units=self.units
#     else:
#       units=S.getUnitIds()
#     if len(units)>20:
#       units=units[::int(len(units)/20)]
#     sw.UnitWaveformsWidget(recording=R,sorting=S,channels=channels,unit_ids=units).plot()
#     save_plot(self.jpg_out)
    
# def create_waveforms_plot(recording,firings):
#   out=CreateWaveformsPlot.execute(
#     recording_dir=recording['directory'],
#     channels=recording.get('channels',[]),
#     units=recording.get('units_true',[]),
#     firings=firings,
#     jpg_out={'ext':'.jpg'}
#   ).outputs['jpg_out']
#   return ca.saveFile(out,basename='waveforms.jpg')


def _create_jobs_for_recording_old(recording):
    print('Creating jobs for recording: {}/{}'.format(recording.get('study',''),recording.get('name','')))
    dsdir=recording['directory']
    # raw_path=dsdir+'/raw.mda'
    firings_true_path=dsdir+'/firings_true.mda'
    # geom_path=dsdir+'/geom.csv'
    channels=recording.get('channels',None)
    units=recording.get('units_true',None)

    if not mt.findFile(path=firings_true_path):
        raise Exception('firings_true file not found: '+firings_true_path)
    job_info=ComputeRecordingInfo.createJob(
        recording_dir=dsdir,
        channels=recording.get('channels',[]),
        json_out={'ext':'.json','upload':True},
        _container='default'
    )
    job_info.addFilesToRealize([dsdir+'/raw.mda',dsdir+'/firings_true.mda'])
    # job=CreateTimeseriesPlot.createJob(
    #     recording_dir=dsdir,
    #     channels=recording.get('channels',[]),
    #     jpg_out={'ext':'.jpg','upload':True},
    #     _container='default'
    # )
    # jobs_timeseries_plot.append(job)
    job_units_info=ComputeUnitsInfo.createJob(
        recording_dir=dsdir,
        firings=dsdir+'/firings_true.mda',
        unit_ids=units,
        channel_ids=channels,
        json_out={'ext':'.json','upload':True},
        _container='default'
    )
    job_units_info.addFilesToRealize([dsdir+'/raw.mda', dsdir+'/firings_true.mda'])
    return (job_info, job_units_info)