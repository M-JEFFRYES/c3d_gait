from ezc3d import c3d
import numpy as np
import json
from scipy import signal
import os

from gaittrial import *

""" 
c3dpath = "../tests/exampledata/ANON_t.c3d"
c3dobj = c3d(c3dpath)

trial = TrialData(c3dobj)

#########
c3dpath = 'F:\\MSC\\First_Investigation\\C3D\\SUB_15_APP_1_T1.c3d'

trialc3d = c3d(c3dpath)

pointfrequency = trialc3d['header']['points']['frame_rate']
analogfrequnecy = trialc3d['header']['analogs']['frame_rate']

# Get events data
eventdata = [
    list(float(trialc3d['parameters']['EVENT']['TIMES']['value'][1])),
    list(trialc3d['parameters']['EVENT']['CONTEXTS']['value']),
    list(trialc3d['parameters']['EVENT']['LABELS']['value'])
]
eventdata = np.transpose(np.array(eventdata))
eventdata = sorted(eventdata, key=lambda x: float(x[0]))

eves = Events(eventdata, pointfrequency, analogfrequnecy)

# Trial data
pointlabels = trialc3d['parameters']['POINT']['LABELS']['value'] 
pointdata = trialc3d['data']['points']
analogchannels = np.transpose(np.array([trialc3d['parameters']['ANALOG']['LABELS']['value'], trialc3d['parameters']['ANALOG']['DESCRIPTIONS']['value']]))
analogdata = trialc3d['data']['analogs'][0]

# Add kinematic data
kinematics = Kinematics(pointlabels, pointdata, eves.full_cycle_point)

# Add kinetics data
kinetics= Kinetics(pointlabels, pointdata, eves.full_cycle_point)

# Add emg data
emg = EMG(analogchannels,analogdata, eves.full_cycle_analog)

# Slice kinematics from GPS
gps = GPSKinematics(kinematics.kinematics, eves.l_cycle_point, eves.r_cycle_point)

 """