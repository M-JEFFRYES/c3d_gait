from ezc3d import c3d 
import numpy as np
from scipy import signal
import os

class Anonymise:
    """This class removes the patient identifiable data from the c3d file."""
    def __init__(self, c3dPath, subjectname="ANON"):
        """
        Loads the c3d file data and removes patient identifable data.

        :param c3dPath(string): Absolute or relative path to the c3d file
        :param subjectname(string)(optional): Reference to replace the patient name
        :return: None
        """

        # Load c3d file
        try:
            trial = c3d(c3dPath)
        except:
            raise Exception("Unable to open {}. Check the filepath is valid and not corrupted".format(c3dPath))
    
        # Remove name from c3d object
        trial['parameters']['SUBJECTS']['NAMES']['value'] = subjectname
        self.trialC3D = trial
        return
    
    def createFilePath(self, outputdir, condition, trialno):
        """
        Returns a file path for the anonymised c3d file to be save to.
        Format "{outputdir}/{subjectname}_{condition}_{trialno}.c3d

        :param outputdir(String): Absolute or relative path to chosen directory
        :param condition(String): Trial condition e.g barefoot
        :param trialno(int): Trial number
        
        :return: fielpath(String): Output file path
        """
        # Create file name
        filename= self.trialC3D['parameters']['SUBJECTS']['NAMES']['value']
        if condition!=None:
            filename = "{}_{}".format(filename, condition)
        else:
            pass

        if trialno!=None:
            filename  = "{}_{}.c3d".format(filename, trialno)
        else:
            filename  = "{}.c3d".format(filename)
        
        if outputdir!=None:
            filepath = os.path.join(outputdir, filename)
        else:
            filepath = filename
        return filepath

    def saveC3D(self, outputdir=None, condition=None, trialno=None):
        """
        Save the anonymised c3d file.

        :param outputdir(String): Absolute or relative path to chosen directory
        :param condition(String): Trial condition e.g barefoot
        :param trialno(int): Trial number
        :return: None
        """
        fpath = self.createFilePath(outputdir, condition, trialno)
        self.trialC3D.write(fpath)
        return

class PointsData:

    def __init__(self, PointsLabels, Groups, PointsData, PointsFrequency=120):
        self.PointsFrequency = PointsFrequency

        self.getLabels(Groups)

        self.pullPointsData(PointsLabels, PointsData)

        return
    
    def getLabels(self, Groups):

        self.KinematicLabels = set(Groups['Angles']) 
        self.PowerLabels = set(Groups['Powers'])
        self.MomentLabels = set(Groups['Moments'])
        self.ForceLabels = set(Groups['Forces'])

        self.convertKinematicsChannels = {
            'LPelvisAngles_0':'Pelvic Tilt Left', 
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
            'LHipAngles_2':'Hip Rotation Left',
            'RHipAngles_2':'Hip Rotation Right', 
            'LFootProgressAngles_2':'Foot Progression Left', 
            'RFootProgressAngles_2':'Foot Progression Right'}
        return

    def pullPointsData(self,  PointsLabels, PointsData):
        
        self.KinematicData = {}
        self.PowerData = {}
        self.MomentData = {}
        self.ForceData = {}

        for labelset, label in enumerate(PointsLabels):

            # Check if in kinematics
            if label in self.KinematicLabels: 
                for ind in range(0,3):
                    chn = f'{label}_{ind}'
                    if chn in self.convertKinematicsChannels:
                        key = self.convertKinematicsChannels[chn]
                        value = PointsData[ind, labelset, :]

                        self.KinematicData[key] = value
                    else:
                        pass
            
            elif label in self.PowerLabels: 
                for ind in range(0,3):
                    chn = f'{label}_{ind}'
                    
                    key = chn
                    value = PointsData[ind, labelset, :]
                    self.PowerData[key] = value
                    
            elif label in self.MomentLabels: 
                for ind in range(0,3):
                    chn = f'{label}_{ind}'
                    
                    key = chn
                    value = PointsData[ind, labelset, :]
                    self.MomentData[key] = value

            elif label in self.ForceLabels: 
                for ind in range(0,3):
                    chn = f'{label}_{ind}'
                    
                    key = chn
                    value = PointsData[ind, labelset, :]
                    self.ForceData[key] = value
            
            # Check if in kinematics         
            else:
                pass
        return

    def SliceKinematics(self, LC_Slice, RC_Slice, Full_Slice, NoPointSamples=51):
        
        self.Kinematics_LC = {}
        self.Kinematics_RC = {}
        self.Kinematics_Full = {}
        self.gpskinematics = {}
        for key, value in self.KinematicData.items():

            self.Kinematics_LC[key] = value[LC_Slice]
            self.Kinematics_RC[key] = value[RC_Slice]
            self.Kinematics_Full[key] = value[Full_Slice]

            if "Left" in key:
                self.gpskinematics[key] = list(signal.resample(value[LC_Slice], NoPointSamples))
            else:
                self.gpskinematics[key] = list(signal.resample(value[RC_Slice], NoPointSamples))
        return 

class AnalogsData:

    def __init__(self, AnalogsLabels, AnalogDescriptions, AnalogUnits, AnalogsData, AnalogsFrequency=1000):

        self.AnalogDescriptions = AnalogDescriptions # dont think it is needed, maybe to confirm EMG

        self.AnalogsFrequency = AnalogsFrequency

        self.getEMGLabels(AnalogUnits, AnalogsLabels)
        
        self.CheckEMGLabelset(AnalogDescriptions, AnalogUnits)

        self.ConvertEMGLabel()

        self.pullAnalogsData(AnalogsLabels, AnalogsData)

        return

    def getEMGLabels(self, AnalogUnits, AnalogsLabels):

        self.EmgLabels = []
        self.ForceplateLabels = []
        self.OtherAnalogLabels = []

        for i, unit in enumerate(AnalogUnits):

            if ("v" in unit.lower()) and ("FSL" not in AnalogsLabels[i].lower()) and ("FSR" not in AnalogsLabels[i].lower()):
                self.EmgLabels.append(AnalogsLabels[i])
            elif "n" in unit.lower():
                self.ForceplateLabels.append(AnalogsLabels[i])
            else:
                self.OtherAnalogLabels.append(AnalogsLabels[i])
        return
        
    def CheckEMGLabelset(self, AnalogDescriptions, AnalogUnits):

        for i, unit in enumerate(AnalogUnits):

            if 'v' in unit.lower():
                if "Delsys IM EMG" in AnalogDescriptions[i]:
                    self.emgset = 'delsys'
                    break

                elif "EMG Channel" in AnalogDescriptions[i]:
                    self.emgset = 'sys1'
                    break

                elif "Analog Device::Voltage" in AnalogDescriptions[i]:
                    self.emgset = 'sys2'
                    break

                elif "Analog EMG::Voltage" in AnalogDescriptions[i]:
                    self.emgset = 'sys3'
                    break

                else:
                    self.emgset = 'unknown'
                    print(AnalogDescriptions[i])
                    pass

                print(self.emgset)
        return

    def ConvertEMGLabel(self):

        conversionLookup = {
            'delsys':{'LRF.IM EMG1': 'LRF',
                'RVM.IM EMG10': 'RVM',
                'RSM.IM EMG11': 'RSM',
                'RST.IM EMG12': 'RST',
                'RTA.IM EMG13': 'RTA',
                'RPR.IM EMG14': 'RPR',
                'RMG.IM EMG15': 'RMG',
                'RSOL.IM EMG16': 'RSOL',
                'LVM.IM EMG2': 'LVM',
                'LSM.IM EMG3': 'LSM',
                'LST.IM EMG4': 'LST',
                'LTA.IM EMG5': 'LTA',
                'LPR.IM EMG6': 'LPR',
                'LMG.IM EMG7': 'LMG',
                'LSOL.IM EMG8': 'LSOL',
                'RRF.IM EMG9': 'RRF'},

            'sys1':{'EMG1': 'EMG1',
                'EMG2': 'EMG2',
                'EMG3': 'EMG3',
                'EMG4': 'EMG4',
                'EMG5': 'EMG5',
                'EMG6': 'EMG6',
                'EMG7': 'EMG7',
                'EMG8': 'EMG8',
                'EMG9': 'EMG9',
                'EMG10': 'EMG10',
                'EMG11': 'EMG11',
                'EMG12': 'EMG12'},

            'sys2':{'Voltage.EMG1': 'Voltage.EMG1',
                'Voltage.EMG2': 'Voltage.EMG2',
                'Voltage.EMG3': 'Voltage.EMG3',
                'Voltage.EMG4': 'Voltage.EMG4',
                'Voltage.EMG5': 'Voltage.EMG5',
                'Voltage.EMG6': 'Voltage.EMG6',
                'Voltage.EMG7': 'Voltage.EMG7',
                'Voltage.EMG8': 'Voltage.EMG8',
                'Voltage.EMG9': 'Voltage.EMG9',
                'Voltage.EMG10': 'Voltage.EMG10',
                'Voltage.EMG11': 'Voltage.EMG11',
                'Voltage.EMG12': 'Voltage.EMG12'},

            'sys3':{'LRF01': 'LRF01',
                'LMH02': 'LMH02',
                'BROKEN03': 'BROKEN03',
                'BROKEN04': 'BROKEN04',
                'BROKEN05': 'BROKEN05',
                'BROKEN06': 'BROKEN06',
                'BROKEN07': 'BROKEN07',
                'BROKEN08': 'BROKEN08',
                'RVM09': 'RVM09',
                'LVM10': 'LVM10',
                'LTA11': 'LTA11',
                'LMG12': 'LMG12',
                'RMG13': 'RMG13',
                'RTA14': 'RTA14',
                'RMH15': 'RMH15',
                'RRF16': 'RRF16'},
        }

        labelConversion = conversionLookup[self.emgset]

        self.newEMGLabels = []
        for i in range(0, len(self.EmgLabels)):
            try:
                newlabel = labelConversion[self.EmgLabels[i]]
            except:
                print(f'emg label not found in lookup hashmap--> {self.EmgLabels[i]}')
                newlabel = self.EmgLabels[i]
            self.newEMGLabels.append(newlabel)            
        return
    
    def pullAnalogsData(self,AnalogsLabels, AnalogsData):

        self.EMGData = {}
        self.ForceplateData = {}
        self.OtherAnalogData = {}

        for labInd, label in enumerate(AnalogsLabels):
            
            key = label
            value = AnalogsData[labInd]

            if label in self.EmgLabels:

                # convert label
                newkey = self.newEMGLabels[self.EmgLabels.index(key)]
                self.EMGData[newkey] = value
            elif label in self.ForceplateLabels:
                self.ForceplateData[key] = value
            elif label in self.OtherAnalogLabels:
                self.OtherAnalogData[key] = value
            else:
                pass

        return
    
    def SliceEMG(self, LC_Slice, RC_Slice, Full_Slice):

        self.EMG_LC = {}
        self.EMG_RC = {}
        self.EMG_Full = {}

        for key, value in self.EMGData.items():
            self.EMG_LC[key] = value[LC_Slice]
            self.EMG_RC[key] = value[RC_Slice]
            self.EMG_Full[key] = value[Full_Slice]
        return

    def MSAInputData(self, MSALabels, cycle='Left', resampleType='frequency', resample=1000):
        
        
        self.MSALabels = MSALabels
        self.MSAData = []
        # Select cycle dataset
        if cycle=='Left':
            emg = self.EMG_LC
        elif cycle=='Right':
            emg = self.EMG_RC
        else:
            emg = self.EMG_Full

        # calculate samples required
        currentSamples = len(emg[self.MSALabels[0]])
        if resampleType=='frequency':
            requiredSamples = int((currentSamples/self.AnalogsFrequency)*resample)
        else:
            requiredSamples = resample

        # Append channel data
        for key in self.MSALabels:
            if key in emg:
                value = emg[key]
                self.MSAData.append(list(signal.resample(value, requiredSamples)))
            else:
                print(f'Missing EMG channel ---> {key}')
            
        self.MSAData = np.array(self.MSAData)
        return

class EventData:

    def __init__(self, EventTimes, EventLabels, EventContexts, PointsFirstFrame=0, PointsFrequency=120, AnalogsFirstFrame=0, AnalogsFrequency=1000):
        
        self.PointsFirstFrame=PointsFirstFrame 
        self.PointsFrequency=PointsFrequency 
        self.AnalogsFirstFrame=AnalogsFirstFrame 
        self.AnalogsFrequency=AnalogsFrequency

        self.organiseEventData(EventTimes, EventLabels, EventContexts)

        self.checkNumberEvents()

        self.getGaitcycles()

        self.GetCycleSlices()
        return

    def CalculatePointFrame(self, time):
        pointFrame = int((time*self.PointsFrequency) - self.PointsFirstFrame)
        return pointFrame
    
    def CalculateAnalogFrame(self, time):
        analogFrame = int((time*self.AnalogsFrequency) - self.AnalogsFirstFrame)
        return analogFrame

    def organiseEventData(self, EventTimes, EventLabels, EventContexts):

        self.eventdata = []
        for i, time in enumerate(EventTimes):
            pframe = self.CalculatePointFrame(time) 
            aframe = self.CalculateAnalogFrame(time) 
            data = [time, EventContexts[i], EventLabels[i], pframe, aframe]
            self.eventdata.append(data)

        self.eventdata = sorted(self.eventdata, key=lambda x: float(x[0]))
        return

    def checkNumberEvents(self):
        try:
            self.eventdata[0][0]
        except:
            msg = "File has not been evented"
            print(msg)
            raise Exception(msg)

        self.no_events = len(self.eventdata)

        if self.no_events <7:
            print("Not enough events present ({})".format(self.no_events))
        elif self.no_events>7:
            print("Extra events present ({})".format(self.no_events))
        else:
            pass
        return

    def getGaitcycles(self):

        lc_track, rc_track = False, False
        lc_current, rc_current = [], []
        self.left_cycles, self.right_cycles = [], []

        firstStrike = None
        # get cycles for individual legs
        for i, event in enumerate(self.eventdata):

            if (event[2]=="Foot Strike"):

                if (firstStrike == None):
                    firstStrike = i
            
                if event[1] == 'Left':
                    if (lc_track==False):
                        lc_current.append([event[0], event[3], event[4]])
                        lc_track=True
                    elif (lc_track==True):
                        lc_current.append([event[0], event[3], event[4]])
                        self.left_cycles.append(lc_current)
                        lc_current = []
                        lc_track=False
                    else:
                        pass
            
                elif event[1] == 'Right':
                    if (rc_track==False):
                        rc_current.append([event[0], event[3], event[4]])
                        rc_track=True
                    elif (rc_track==True):
                        rc_current.append([event[0], event[3], event[4]])
                        self.right_cycles.append(rc_current)
                        rc_current = []
                        rc_track=False
                    else:
                        pass
                else:
                    pass
            else:
                pass
        
        # get whole gait cycle
        order = ['Foot Strike','Foot Off','Foot Strike','Foot Off', 'Foot Strike',
        'Foot Off', 'Foot Strike']

        correctEvents = True
        for i in range(firstStrike, firstStrike+7,1):
            if self.eventdata[i][2] != order[i-firstStrike]:
                correctEvents = False
            else:
                pass
        
        if correctEvents:
            self.full_cycle = [self.eventdata[firstStrike], self.eventdata[firstStrike+6]]
        return
    
    def GetCycleSlices(self):
        self.LC_Slice_Points = slice(self.left_cycles[0][0][1], self.left_cycles[0][1][1]+1, 1)
        self.LC_Slice_Analogs = slice(self.left_cycles[0][0][2], self.left_cycles[0][1][2]+1, 1)

        self.RC_Slice_Points = slice(self.right_cycles[0][0][1], self.right_cycles[0][1][1]+1, 1)
        self.RC_Slice_Analogs = slice(self.right_cycles[0][0][2], self.right_cycles[0][1][2]+1, 1)

        self.Full_Slice_Points = slice(self.full_cycle[0][3], self.full_cycle[1][3]+1, 1)
        self.Full_Slice_Analogs = slice(self.full_cycle[0][4], self.full_cycle[1][4]+1, 1)
        return

class GaitTrial(PointsData, AnalogsData, EventData):

    def __init__(self, c3dobj):

        EventData.__init__(self,
            c3dobj['parameters']['EVENT']['TIMES']['value'][1],
            c3dobj['parameters']['EVENT']['LABELS']['value'],
            c3dobj['parameters']['EVENT']['CONTEXTS']['value'],
            PointsFirstFrame=c3dobj['header']['points']['first_frame'],
            PointsFrequency=c3dobj['header']['points']['frame_rate'],
            AnalogsFirstFrame=c3dobj['header']['analogs']['first_frame'],
            AnalogsFrequency=c3dobj['header']['analogs']['frame_rate'])

        Groups = {'Angles':c3dobj['parameters']['POINT']['ANGLES']['value'],
            'Powers':c3dobj['parameters']['POINT']['POWERS']['value'],
            'Moments':c3dobj['parameters']['POINT']['MOMENTS']['value'],
            'Forces':c3dobj['parameters']['POINT']['FORCES']['value']
        }

        PointsData.__init__(self, 
            c3dobj['parameters']['POINT']['LABELS']['value'], 
            Groups,
            c3dobj['data']['points'], 
            PointsFrequency=c3dobj['header']['points']['frame_rate'])

        AnalogsData.__init__(self,
            c3dobj['parameters']['ANALOG']['LABELS']['value'],
            c3dobj['parameters']['ANALOG']['DESCRIPTIONS']['value'],
            c3dobj['parameters']['ANALOG']['UNITS']['value'],
            c3dobj['data']['analogs'][0],
            AnalogsFrequency=c3dobj['header']['analogs']['frame_rate'])
        
        self.SliceKinematics(self.LC_Slice_Points, self.RC_Slice_Points, self.Full_Slice_Points)

        self.SliceEMG(self.LC_Slice_Analogs, self.RC_Slice_Analogs, self.Full_Slice_Analogs)

        return


########

def ExtractTrialData(path):
    
    c3dobj = c3d(path)

    trial = GaitTrial(c3dobj)

    return trial



# path = "C:\Development_projects\__EXAMPLE_FILES\C3D\gait_2.c3d"

# path = "F:\\testc3d\\new.c3d" # delsys
# path = "F:\\testc3d\\1.c3d" # sys1
# path = "F:\\testc3d\\old (1).c3d" # sys2
# path = "F:\\testc3d\\med.c3d" # sys3

# c3dobj = c3d(path)

# a = c3dobj['parameters']['ANALOG']['LABELS']['value']
# b = c3dobj['parameters']['ANALOG']['DESCRIPTIONS']['value']
# c = c3dobj['parameters']['ANALOG']['UNITS']['value']
# x = {}
# for i in range(len(a)):
#     x[a[i]] = a[i]
#     print()
#     if 'v' in c[i].lower():

# tr = GaitTrial(c3dobj)


