from ezc3d import c3d
import numpy as np
import json
from scipy import signal
import os

######### need to check and improve eventing

class Events:
    def __init__(self, eventdata, pointfreq, analogfreq, firstPointsFrame, firstAnalogsFrame):

        #check if file has been evented
        try:
            eventdata[0][0]
        except:
            msg = "File has not been evented"
            print(msg)
            raise Exception(msg)
    
        self.firstPointsFrame = firstPointsFrame
        self.firstAnalogsFrame = firstAnalogsFrame

        self.no_events = len(eventdata)

        self.select_events(eventdata, pointfreq, analogfreq)

        self.get_cycle()
        return

    def select_events(self, eventdata, pointfreq, analogfreq):

        # Frame numbers of the first event
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
        self.full_cycle_analog = slice((full[0][2]-self.firstAnalogsFrame), (full[1][2]-self.firstAnalogsFrame))
        
        self.l_cycle_point = slice(left[0][1],left[1][1])
        self.r_cycle_point = slice(right[0][1], right[1][1])
        # Starting count for first frame recorded
        self.full_cycle_point = slice((full[0][1]-self.firstPointsFrame),(full[1][1]-self.firstPointsFrame))

        self.left_events = left
        self.right_events = right
        self.full_cycle = full
        return

class Kinematics:
    def __init__(self, labels, data, full_cycle_point):

        pointsdata = self.getRawPointsData(labels, data, full_cycle_point)

        self.conversionDict()
        self.convertLabels(pointsdata)

        return 

    def getRawPointsData(self, labels, data, full_cycle_point):

        pointsdata = {}

        for i, label in enumerate(labels):
            for j in range(3):
                key = f'{label}_{j}'
                try:
                    value = data[j,i,full_cycle_point]
                except:
                    raise Exception("Not able to slice points data, check eventing")

                pointsdata[key] = value
        return pointsdata

    def conversionDict(self):
        self.convertKinematicsChannels = {'LPelvisAngles_0':'Pelvic Tilt Left', 
        'RPelvisAngles_0':'Pelvic Tilt Right', 
        'LHipAngles_0':'Hip Flexion Left', 
        'RHipAngles_0':'Hip Flexion Right', 
        'LKneeAngles_0':'Knee Flexion Left', 
        'RKneeAngles_0':'Knee Flexion Right', 
        'LAnkleAngles_0':'Ankle Dorsiflexion Left', 
        'RAnkleAngles_0':'Ankle Dorsiflexion Right', 
        'LPelvisAngles_1':'Pelvic Obliquity Left', 
        'RPelvisAngles_1':'Pelvic Obliquity Right', 
        'LHipAngles_1':'Hip Abduction Left', 
        'RHipAngles_1':'Hip Abduction Right', 
        'LPelvisAngles_2':'Pelvic Rotation Left', 
        'RPelvisAngles_2':'Pelvic Rotation Right',
        'LHipAngles_1':'Hip Rotation Left',
        'RHipAngles_1':'Hip Rotation Right', 
        'LFootProgressAngles_2':'Foot Progression Left', 
        'RFootProgressAngles_2':'Foot Progression Right'}
        return

    def convertLabels(self, pointsdata):
        self.kinematics = {}
        for key, value in self.convertKinematicsChannels.items():
            self.kinematics[value] = pointsdata[key]
        return

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
    def __init__(self, channels, data, full_cycle_analog, l_cycle_analog, r_cycle_analog, channelsUsed=None):
        
        self.ChannelsUsed = channelsUsed

        # get dict of analogs
        analogdata = self.organiseAnalogdata(channels[:,0], data, full_cycle_analog)
        
        # set emg data
        self.getEMGData(channels, analogdata)

        # Check channels used
        self.checkChannelsUsed()

        # Separate Sides
        self.getSideEMG(l_cycle_analog, r_cycle_analog)

    def organiseAnalogdata(self, channels, data, full_cycle_analog):
        analogs = {}
        try:
            for i, channel in enumerate(channels):
                analogs[channel] = data[i, full_cycle_analog]
        except: 
            raise Exception("Unable to slice analogdata, check eventing")
        return analogs

    def getEMGData(self, channels, analogdata):

        self.emg = {}

        emgLabels = []
        # Check if EMG is in the label
        for i, label in enumerate(channels[:,0]):
            if "EMG" in label:
                emgLabels.append(label)

        if len(emgLabels) == 12:
            # Convert from emg to muscles and get data
            self.convertEMG()
            self.selectEMG(self, analogdata)

        elif len(emgLabels) > 12:
            # Convert from emg to muscles and get data
            print('BEMG with 16 channels, dont have BEMG15 or BEMG16\n')
            print('Check which set to use\n')
            self.convertBEMG()
            self.selectEMG(analogdata)
            self.bemg = self.emg

            # Save EMG channels aswell
            self.convertEMG()
            self.selectEMG(analogdata)

        elif (len(emgLabels)<1) and ("LRF" in channels[:,0]):
            self.convertMuscles()
            self.selectEMG(analogdata)
        elif (len(emgLabels)<1) and ("L Rectus Femoris" in channels[:,0]):
            self.convertLongMuslces()
            self.selectEMG(analogdata)
        else:
            print("Havent found emg channels")
        return
    
    def convertEMG(self):
        self.convertEMGChannels = {'EMG1':'LRF', 'EMG2':'LVM', 'EMG3':'LMH', 
        'EMG4':'LTA','EMG5':'LMG', 'EMG6':'LSOL','EMG7':'RRF', 'EMG8':'RVM', 
        'EMG9':'RMH','EMG10':'RTA','EMG11':'RMG', 'EMG12':'RSOL'}
        return

    def convertBEMG(self):
        self.convertEMGChannels = {'BEMG1':'LRF', 'BEMG2':'LVM', 'BEMG3':'LMH', 
        'BEMG4':'LTA','BEMG5':'LMG', 'BEMG6':'LSOL','BEMG7':'RRF', 'BEMG8':'RVM', 
        'BEMG9':'RMH','BEMG10':'RTA','BEMG11':'RMG', 'BEMG12':'RSOL'}
        return
    
    def convertMuscles(self):
        self.convertEMGChannels = {'LRF':'LRF', 'LVM':'LVM', 'LMH':'LMH', 'LTA':'LTA', 'LMG':'LMG', 
        'LSOL':'LSOL','RRF':'RRF', 'RVM':'RVM', 'RMH':'RMH', 'RTA':'RTA', 'RMG':'RMG', 'RSOL':'RSOL'}
        return

    def convertLongMuslces(self):
        self.convertEMGChannels = {'L Rectus Femoris':'LRF', 'L Vastus Mediali':'LVM', 'L Medial Hamstri':'LMH', 'L Tibialis Anter':'LTA', 'L Medial Gastroc':'LMG', 
        'L Soleus':'LSOL','R Rectus Femoris':'RRF', 'R Vastus Mediali':'RVM', 'R Medial Hamstri':'RMH', 'R Tibialis Anter':'RTA', 
        'R Medial Gastroc':'RMG', 'R Soleus':'RSOL'}
        return

    def selectEMG(self, analogdata):
        self.emg = {}
        for key, value in self.convertEMGChannels.items():
            try:
                self.emg[value] = analogdata[key]
            except:
                Exception(f"Unable to select {key} from emg datausing ")
        return 

    def checkChannelsUsed(self):
        if self.ChannelsUsed != None:
            newEMG = {}
            for chn in self.ChannelsUsed:
                newEMG[chn] = self.emg[chn]
            self.emg = newEMG
        else:
            pass
        return

    def getSideEMG(self, l_cycle_analog, r_cycle_analog):
        self.emgLeft = {}
        self.emgRight = {}

        self.emgRightChannels = ['RRF', 'RVM', 'RMH', 'RMH', 'RTA', 'RMG', 'RSOL']
        self.emgLeftChannels = ['LRF', 'LVM', 'LMH', 'LMH', 'LTA', 'LMG', 'LSOL']

        try:
            for key, value in self.emg.items():
                self.emgRight[key] = value[r_cycle_analog]
                self.emgLeft[key] = value[l_cycle_analog]
        except:
            raise Exception('Unable to separate emg cycles, check left/right cycles')
        return
        
class GPSKinematics:

    def __init__(self, kinematicdata, l_cycle_point, r_cycle_point, noSamples=51):

        self.select_cycles(kinematicdata, l_cycle_point, r_cycle_point, noSamples)

        return
    
    def select_cycles(self, kinematicdata, l_cycle_point, r_cycle_point, noSamples):

        self.GPSkinematics = {}

        for key, value in kinematicdata.items():
            if "Left" in key:
                cycle = l_cycle_point
            else:
                cycle = r_cycle_point

            self.GPSkinematics[key] = list(signal.resample(value[cycle], noSamples))
        return
    
################################
class TrialData(Events, Kinematics, Kinetics, EMG, GPSKinematics):

    def __init__(self, trialc3d, gpsNoSamples=51, emgChannelsUsed=None):

        self.pointfrequency = trialc3d['header']['points']['frame_rate']
        self.analogfrequnecy = trialc3d['header']['analogs']['frame_rate']

        # Get events data
        eventdata = [
            list(trialc3d['parameters']['EVENT']['TIMES']['value'][1]),
            list(trialc3d['parameters']['EVENT']['CONTEXTS']['value']),
            list(trialc3d['parameters']['EVENT']['LABELS']['value'])
        ]
        eventdata = np.transpose(np.array(eventdata))
        eventdata = sorted(eventdata, key=lambda x: float(x[0]))

        Events.__init__(self, eventdata, self.pointfrequency, self.analogfrequnecy, trialc3d['header']['points']['first_frame'], trialc3d['header']['analogs']['first_frame'])

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
        EMG.__init__(self,analogchannels, analogdata, self.full_cycle_analog, self.l_cycle_analog, self.r_cycle_analog, channelsUsed=emgChannelsUsed)

        # Slice kinematics from GPS
        GPSKinematics.__init__(self, self.kinematics, self.l_cycle_point, self.r_cycle_point, gpsNoSamples)
        return


    def saveEMGside(self, side, directory=None, reference="subject"):

        if side =='Left':
            sideslice = self.l_cycle_analog
        else:
            sideslice = self.r_cycle_analog

        sideEMG = {}
        for key, value in self.emg.items():
            sideEMG[key] = value[sideslice]

        if directory==None:
            path = f"{reference}_EMG_{side}.json"
        else:
            path = os.path.join(directory, f"{reference}_EMG_{side}.json")
        
        with open(path, 'w') as f:
            json.dump(sideEMG,f)
        return

####################

# # pth = "F:/msc_data/C3D_FILES_REF/SUB251_2_5.c3d"
# pth = "F:/msc_data/C3D_FILES_REF/SUB259_2_1.c3d"

# # pth="F:/msc_data/C3D_FILES_REF/SUB356_3_2.c3d"


# trialc3d = c3d(pth)
# tr = TrialData(trialc3d)
