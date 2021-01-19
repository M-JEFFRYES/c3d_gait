from ezc3d import c3d
import numpy as np
import json
from scipy import signal
import os

class Metadata:
    def __init__(self):


        return

class Events:
    def __init__(self, eventdata, pointfreq, analogfreq):

        self.no_events = len(eventdata)

        self.select_events(eventdata, pointfreq, analogfreq)

        self.get_cycle()
        return

    def select_events(self, eventdata, pointfreq, analogfreq):

        self.first_eve = [int(float(eventdata[0][0])*pointfreq), int(float(eventdata[0][0])*analogfreq)] 
        
        eves = []
        for i, val in enumerate(eventdata):
            point = (int(float(val[0])*pointfreq)) - self.first_eve[0]
            analog =(int(float(val[0])*analogfreq)) - self.first_eve[1]
            eves.append([val[0], val[1], val[2], point, analog])
        
        self.eventdata = eves
        return
    
    def get_cycle(self):
        
        if self.no_events <7:
            print("Not enough events present ({})".format(self.no_events))
        elif self.no_events>7:
            print("Extra events present ({})".format(self.no_events))
        else:
            pass

        full, left, right, = [],[], [],


        for event in self.eventdata:
            if "Strike" in event[2]:
                full.append([event[0], (self.first_eve[0]+event[3]), (self.first_eve[1]+event[4])])
                if 'Left' in event[1]:
                    left.append([event[0], event[3], event[4]])
                else:
                    right.append([event[0], event[3], event[4]])
            else:
                pass
        full = full[0], full[-1]

        self.l_cycle_analog = slice(left[0][2], left[1][2])
        self.r_cycle_analog = slice(right[0][2],right[1][2])
        self.full_cycle_analog = slice(full[0][2], full[1][2])
        
        self.l_cycle_point = slice(left[0][1],left[1][1])
        self.r_cycle_point = slice(right[0][1], right[1][1])
        self.full_cycle_point = slice(full[0][1],full[1][1])

        self.left_events = left
        self.right_events = right
        self.full_cycle = full
        return

class Kinematics:
    def __init__(self, labels, data, full_cycle_point):

        self.kinematics = {}
        
        self.select_kinematics(labels, data, full_cycle_point)

        return 

    def select_kinematics(self, labels, data, full_cycle_point):

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

        for i, row in enumerate(convert):
            try:
                labind = labels.index(row[1])
            except:
                # Exception used to find altered label
                for i, lab in enumerate(labels):
                    if row[1] in lab:
                        labind = i
                    else:
                        pass

            axsind = row[2]
            var_data = data[axsind,labind,full_cycle_point]
            self.kinematics[row[0]] = var_data

class Kinetics:
    def __init__(self, labels, data, full_cycle_point):


        # Slice the kinetic vars
        self.grf ={}
        self.moment = {}
        self.power = {}
        self.force = {}
        self.select_all_kinetics(labels, data, full_cycle_point)

        # Select desired kinetic vars
        self.kinetics = {}

        self.select_kinetics()

        return
    
    def select_all_kinetics(self, labels, data, full_cycle_point):

        for i, label in enumerate(labels):

            if "Power" in label:
                self.power[label] = data[:,i,full_cycle_point]
            elif "Moment" in label:
                self.moment[label] = data[:,i,full_cycle_point]
            elif "Force" in label:
                self.force[label] = data[:,i,full_cycle_point]
            elif "Ground" in label:
                self.grf[label] = data[:,i,full_cycle_point]
            else:
                pass
        return

    def select_kinetics(self):
        return

class EMG:
    def __init__(self, channels, data, full_cycle_analog):

        self.emg = {}
        emgdata = data[:,full_cycle_analog]

        self.select_emg(channels, emgdata)

        return

    def select_emg(self, labels, data):

        for i, row in enumerate(labels):
            if (("Analog Device" in row[1]) or ('EMG' in row[1])) and ('FSL' not in row[0]) and ('FSR' not in row[0]):
                
                if "EMG" in row[0]:
                    key = self.relabel_old_system(row[0])
                else:
                    key = row[0]
                self.emg[key] = list(data[i])
        return
    
    def relabel_old_system(self, oldLabel):
        convert = np.array([
            ['LRF', 'EMG1'], ['LVM', 'EMG2'], ['LMH', 'EMG3'], ['LTA', 'EMG4'], ['LMG', 'EMG5'], ['LSOL', 'EMG6'],
            ['RRF', 'EMG7'], ['RVM', 'EMG8'], ['RMH', 'EMG9'], ['RTA', 'EMG10'], ['RMG', 'EMG11'], ['RSOL', 'EMG12']
        ])

        label = str(convert[np.where(convert==oldLabel)[0],0][0])

        return label

    def saveEMG(self, directory=None, reference="subject"):

        if directory==None:
            path = f"{reference}_EMG.json"
        else:
            path = os.path.join(directory, f"{reference}_EMG.json")
        
        with open(path, 'w') as f:
            json.dump(self.emg,f)
        return


class GPSKinematics:

    def __init__(self, kinematicdata, l_cycle_point, r_cycle_point):

        self.select_cycles(kinematicdata, l_cycle_point, r_cycle_point)

        return
    
    def select_cycles(self, kinematicdata, l_cycle_point, r_cycle_point):

        self.GPSkinematics = {}

        for key, value in kinematicdata.items():
            if "Left" in key:
                cycle = l_cycle_point
            else:
                cycle = r_cycle_point

            self.GPSkinematics[key] = list(signal.resample(value[cycle], 51))
        return
    
    def saveGPSkinematics(self, directory=None, reference="subject"):

        if directory==None:
            path = f"{reference}_GPS_KINS.json"
        else:
            path = os.path.join(directory, f"{reference}_GPS_KINS.json")
        
        with open(path, 'w') as f:
            json.dump(self.GPSkinematics,f)
        return


################################
class TrialData(Events, Kinematics, Kinetics, EMG, GPSKinematics):

    def __init__(self, trialc3d):

        self.pointfrequency = trialc3d['header']['points']['frame_rate']
        self.analogfrequnecy = trialc3d['header']['analogs']['frame_rate']

        # Get events data
        eventdata = [
            list(trialc3d['parameters']['EVENT']['TIMES']['value'][1]),
            list(trialc3d['parameters']['EVENT']['CONTEXTS']['value']),
            list(trialc3d['parameters']['EVENT']['LABELS']['value'])
        ]
        eventdata = np.transpose(np.array(eventdata))
        eventdata = sorted(eventdata, key=lambda x: x[0])

        Events.__init__(self, eventdata, self.pointfrequency, self.analogfrequnecy)

        # Trial data
        pointlabels = trialc3d['parameters']['POINT']['LABELS']['value'] 
        pointdata = trialc3d['data']['points']
        analogchannels = np.transpose(np.array([trialc3d['parameters']['ANALOG']['LABELS']['value'], trialc3d['parameters']['ANALOG']['DESCRIPTIONS']['value']]))
        analogdata = trialc3d['data']['analogs'][0]
        
        # Add kinematic data
        Kinematics.__init__(self, pointlabels, pointdata, self.full_cycle_point)

        # Add kinetics data
        Kinetics.__init__(self, pointlabels, pointdata, self.full_cycle_point)

        # Add emg data
        EMG.__init__(self,analogchannels, analogdata, self.full_cycle_analog)

        # Slice kinematics from GPS
        GPSKinematics.__init__(self, self.kinematics, self.l_cycle_point, self.r_cycle_point)
        return



""" 
c3dpath = "../tests/exampledata/ANON_t.c3d"
c3dobj = c3d(c3dpath)

trial = TrialData(c3dobj)

#########

trialc3d = c3d(c3dpath)

pointfrequency = trialc3d['header']['points']['frame_rate']
analogfrequnecy = trialc3d['header']['analogs']['frame_rate']

# Get events data
eventdata = [
    list(trialc3d['parameters']['EVENT']['TIMES']['value'][1]),
    list(trialc3d['parameters']['EVENT']['CONTEXTS']['value']),
    list(trialc3d['parameters']['EVENT']['LABELS']['value'])
]
eventdata = np.transpose(np.array(eventdata))
eventdata = sorted(eventdata, key=lambda x: x[0])

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
