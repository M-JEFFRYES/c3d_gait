from ezc3d import c3d
import numpy as np
import json
from scipy import signal

import pickle


def pull_events(trial):
    """ 
    This function pulls the event information form the c3d object. It outpus a list of lists
    [time (seconds), analog frame, points frame, context(side), label]. 
        Arguments:
            trial(C3D Object): The gait trial object
        Returns:
            events(Dictionary): Metadata for the events

    """

    times = trial['parameters']['EVENT']['TIMES']['value'][1]
    contexts = trial['parameters']['EVENT']['CONTEXTS']['value']
    labels = trial['parameters']['EVENT']['LABELS']['value']
    analog_rate = trial['header']['analogs']['frame_rate']
    point_rate = trial['header']['points']['frame_rate']

    start_analog =trial['header']['analogs']['first_frame']
    start_point = trial['header']['points']['first_frame']

    event = []
    for i in range(len(times)):
        event.append([times[i], (int(times[i]*analog_rate)-start_analog), (int(times[i]*point_rate)-start_point), contexts[i], labels[i]])

    events = sorted(event, key=lambda x: x[0])
    return events

def get_cycles(events):
    """
    This function returns the frames for the left and right cycles.
        Arguments:
            events(Dictionary): Event information
        Returns:
            right(List-tuple): [[point start, analog start], [point end, analog end]] 
            left(List-tuple): [[point start, analog start], [point end, analog end]] 
    """

    right = []
    left = []

    for event in events:
        if event[3] =="Right":
            right.append(event)
        if event[3] =="Left":
            left.append(event)

    # if there are 4 events the first is the foot off (not part of cycle)
    if len(right) == 4:
        right = right[1:]
    else:
        left = left[1:]

    return right, left
    
def get_events(trial):
    """
    This function returns a dictionary with event data stored.
        Arguments:
            trial(C3D Object): The gait trial object
        Returns:
            eventsdata(Dictionary): Event data from the trial 
    """

    eventsdata = {}
    eventsdata['Subject_Name'] = trial['parameters']['SUBJECTS']['NAMES']['value']

    eventsdata['No_events'] = int(trial['parameters']['EVENT']['USED']['value'])
    eventsdata["Events"] = pull_events(trial)
    eventsdata["Left_cycle"], eventsdata["Right_cycle"] = get_cycles(eventsdata["Events"])

    eventsdata['analog_start_frame'] = eventsdata['Events'][0][1]
    eventsdata['points_start_frame'] = eventsdata['Events'][0][2]
    eventsdata['analog_end_frame'] = eventsdata['Events'][-1][1]
    eventsdata['points_end_frame'] = eventsdata['Events'][-1][2]

    return eventsdata

def analog_metadata(trial):
    """
    This function collects the metadata for the analog channels stored within the C3D file.
        Arguments:
            trial(C3D Object): The gait trial object
        Returns:
            analogs_meta(Dictionary): channel label, description, units, scale, gain, offset
            labels(List): Channel labels
    """
    labels = trial['parameters']['ANALOG']['LABELS']['value']
    description = trial['parameters']['ANALOG']['DESCRIPTIONS']['value']
    units = trial['parameters']['ANALOG']['UNITS']['value']
    scale = trial['parameters']['ANALOG']['SCALE']['value']
    gain = trial['parameters']['ANALOG']['GAIN']['value']
    offset = trial['parameters']['ANALOG']['OFFSET']['value']

    analogs_meta = []
    for i in range(len(labels)):
        analogs_meta.append([labels[i], description[i],units[i], 
        scale[i], gain[i], offset[i]])

    return analogs_meta, labels

def analog_channel_groups(labels):
    """
    Groups channel labels for the different analog measurements.
        Arguments:
            labels(List): List  of the analog channel labels
        Returns:
            forceplate(List): List  of the forceplate channel labels
            emg(List): List  of the emg channel labels
            myometer(List): List  of the myometer channel labels
    """

    forceplate, emg, myometer = [], [], []

    for label in labels:
        if "myometer" in label:
            myometer.append(label)
        elif ("Force") in label:
            forceplate.append(label)
        elif ("Moment") in label:
            forceplate.append(label)
        else:
            emg.append(label)
    return forceplate, emg, myometer

def get_analogs(trial):
    """
    This function returns a dictionary with analog data stored.
        Arguments:
            trial(C3D Object): The gait trial object
        Returns:
            analogsdata(Dictionary): Analog data from the trial 
    """

    analogsdata = {}
    analogsdata['Subject_Name'] = trial['parameters']['SUBJECTS']['NAMES']['value']

    analogsdata['analogs_metadata'], labels = analog_metadata(trial)
    analogsdata['analog_frequency'] = trial['header']['analogs']['frame_rate']

    analogsdata['Forceplate_channels'], analogsdata['EMG_channels'], analogsdata['Myometer_channels'] = analog_channel_groups(labels)
    
    raw_analogs = np.array(trial['data']['analogs'][0])

    for i, label in enumerate(labels):
        analogsdata[label] = list(raw_analogs[i])
    
        
    return analogsdata

def points_metadata(trial):
    """
    This function collects the metadata for the points channels stored within the C3D file.
        Arguments:
            trial(C3D Object): The gait trial object
        Returns:
            points_meta(Dictionary): [] - # may get more data
            labels(List): Channel labels
    """
    labels = trial['parameters']['POINT']['LABELS']['value'] 

    points_meta = []

    return points_meta, labels

def points_channel_groups(labels):
    """
    This function returns groups labels for kinematics and kinetics.
        Arguments:
            labels(List): List of all points channel labels
        Returns:
            angles(List): List of the Angle channel labels 
            powers(List): List of the power channel labels 
            forces(List): List of the force channel labels 
            moments(List): List of the moment channel labels 
            markers(List): List of the marker channel labels 
            others(List): List of the other channel labels
    """

    angles, powers, forces, moments = [], [], [], []
    markers, others = [], []

    for label in labels:
        if "Angle" in label:
            angles.append(label)
        elif "Power" in label:
            powers.append(label)
        elif "Force" in label:
            forces.append(label)
        elif "Moment" in label:
            moments.append(label)
        elif "*" in label:
            others.append(label)
        else:
            markers.append(label)

    return angles, powers, forces, moments, markers, others

def get_points(trial):
    """
    This function returns a dictionary with point data stored.
        Arguments:
            trial(C3D Object): The gait trial object
        Returns:
            pointsdata(Dictionary): Point data from the trial 
    """
    pointsdata = {}
    pointsdata['Subject_Name'] = trial['parameters']['SUBJECTS']['NAMES']['value']

    pointsdata['points_metadata'], labels = points_metadata(trial)
    pointsdata['points_frequency'] = trial['header']['points']['frame_rate']

    pointsdata['Joint_angles'], pointsdata['Joint_powers'], pointsdata['Joint_forces'], pointsdata['Joint_moments'], pointsdata['Marker_channels'], pointsdata['Other_channels'] = points_channel_groups(labels)

    #data ={}
    for i, label in enumerate(labels):
        pointsdata[label] = list(trial['data']['points'][:,i,:])
    
    return pointsdata

def KINETICS_DATA(pointsdata, start, end):
    """
    This function returns a sliced set of kinematic variables
        Arguments:
            pointsdata(Dictionary): Point data from the trial
            start(int): The points start frame
            end(int): The points end frame 
        Returns:
            KINEMATICS(Dictionary): Contains kinematic variable data
    """

    KINETICS = {}

    plane = ['X', 'Y', 'Z']

    for channel in pointsdata['Joint_powers']:
        for i, lab in enumerate(plane):
            KINETICS["{}_{}".format(channel,plane[i])] = pointsdata[channel][i][start:end]

    for channel in pointsdata['Joint_moments']:
        for i, lab in enumerate(plane):
            KINETICS["{}_{}".format(channel,plane[i])] = pointsdata[channel][i][start:end]

    for channel in pointsdata['Joint_forces']:
        for i, lab in enumerate(plane):
            KINETICS["{}_{}".format(channel,plane[i])] = pointsdata[channel][i][start:end]

    return KINETICS

def KINEMATICS_DATA(pointsdata, start, end):
    """
    This function returns a sliced set of kinetic variables
        Arguments:
            pointsdata(Dictionary): Point data from the trial
            start(int): The points start frame
            end(int): The points end frame 
        Returns:
            KINETICS(Dictionary): Contains kinetic variable data
    """

    KINEMATICS = {}
    kins = {}
    for channel in pointsdata['Joint_angles']:
        kins[channel] = pointsdata[channel]
    
    convert = [
        ['Pelvic Tilt Left', 'LPelvisAngles', 0], 
        ['Pelvic Tilt Right','RPelvisAngles',0], 
        ['Hip Flexion Left','LHipAngles',0], 
        ['Hip Flexion Right','RHipAngles',0], 
        ['Knee Flexion Left','LKneeAngles',0], 
        ['Knee Flexion Right','RKneeAngles',0], 
        ['Ankle Dorsiflexion Left','LAnkleAngles',0], 
        ['Ankle Dorsiflexion Right','RAnkleAngles',0], 
        ['Pelvic Obliquity Left','LPelvisAngles',1], 
        ['Pelvic Obliquity Right','RPelvisAngles',1], 
        ['Hip Abduction Left','LHipAngles',1], 
        ['Hip Abduction Right','RHipAngles',1], 
        ['Pelvic Rotation Left','LPelvisAngles',2], 
        ['Pelvic Rotation Right','RPelvisAngles',2], 
        ['Hip Rotation Left','LHipAngles',1], 
        ['Hip Rotation Right','RHipAngles',1], 
        ['Foot Progression Left','LFootProgressAngles',2], 
        ['Foot Progression Right','RFootProgressAngles',2]
    ]

    for i, conv in enumerate(convert):
        KINEMATICS[conv[0]] = kins[conv[1]][conv[2]][start:end]
        #print(conv[0])
    return KINEMATICS

def EMG_DATA(analogsdata, start, end):
    """
    This function returns a sliced set of EMG variables
        Arguments:
            analogsdata(Dictionary): Analog data from the trial
            start(int): The analogs start frame
            end(int): The analogs end frame 
        Returns:
            EMG(Dictionary): Contains EMG variable data
    """

    EMG = {}
    for channel in analogsdata['EMG_channels']:
        EMG[channel] = analogsdata[channel][start:end]
    return EMG

###################################################

class c3dExtract:
    """
    This class extracts the useful data from a C3D file.
    """
    def __init__(self, filepath):
        trial = c3d(filepath)

        self.eventsdata = get_events(trial)

        self.analogsdata = get_analogs(trial)

        self.pointsdata = get_points(trial)

        self.full_dataset()

        self.left_dataset()

        self.right_dataset()

        self.GPS_dataset()

    def full_dataset(self):

        self.KINEMATICS_full = KINEMATICS_DATA(self.pointsdata, self.eventsdata['Events'][0][2], self.eventsdata['Events'][-1][2])

        self.KINETICS_full = KINETICS_DATA(self.pointsdata, self.eventsdata['Events'][0][2], self.eventsdata['Events'][-1][2])

        self.EMG_full = EMG_DATA(self.analogsdata, self.eventsdata['Events'][0][1], self.eventsdata['Events'][-1][1])

    def left_dataset(self):
        
        self.KINEMATICS_left = KINEMATICS_DATA(self.pointsdata, self.eventsdata['Left_cycle'][0][2], self.eventsdata['Left_cycle'][2][2])

        self.KINETICS_left = KINETICS_DATA(self.pointsdata, self.eventsdata['Left_cycle'][0][2], self.eventsdata['Left_cycle'][2][2])

        self.EMG_left = EMG_DATA(self.analogsdata, self.eventsdata['Left_cycle'][0][1], self.eventsdata['Left_cycle'][2][1])

    def right_dataset(self):
        
        self.KINEMATICS_right = KINEMATICS_DATA(self.pointsdata, self.eventsdata['Right_cycle'][0][2], self.eventsdata['Right_cycle'][2][2])

        self.KINETICS_right = KINETICS_DATA(self.pointsdata, self.eventsdata['Right_cycle'][0][2], self.eventsdata['Right_cycle'][2][2])

        self.EMG_right = EMG_DATA(self.analogsdata, self.eventsdata['Right_cycle'][0][1], self.eventsdata['Right_cycle'][2][1])

    def GPS_dataset(self):

        self.GPSdataset = {}

        for key, value in self.KINEMATICS_left.items():
            if "Left" in key:
                self.GPSdataset[key] = signal.resample(value, 100)
        
        for key, value in self.KINEMATICS_right.items():
            if "Right" in key:
                self.GPSdataset[key] = signal.resample(value, 100)


def export_gait_data(filepath, outputdirectory, subjectname, trial=None):

    if trial != None:
        fpath = "{}\\{}_{}.gait"
    else:
        fpath = "{}\\{}.gait"

    gait_data = c3dExtract(filepath)

    with open(fpath, 'wb') as f:
        pickle.dump(gait_data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print("Data extraction started\n")
    print("Data from {}\n".format(filepath))
    print("Saved to {}\n".format(fpath))
    print("Extraction finished\n")
    return