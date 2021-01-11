from trial import Metadata, Events, Kinematics, Kinetics, EMG, GPSKinematics
from trial import TrialData

import unittest
from ezc3d import c3d
import numpy as np
import os

testc3dpath = "tests/exampledata/ANON_t.c3d"



class MetadataTest(unittest.TestCase):

    def setUp(self):
        self.__c3dpath = testc3dpath
        self.__c3d = c3d(self.__c3dpath)
        return
    
    def test_Metadata(self):
        #self.__Metadata = Metadata()
        print("Metadata class test passed\n")

class EventsTest(unittest.TestCase):

    def setUp(self):
        self.__c3dpath = testc3dpath
        self.__c3d = c3d(self.__c3dpath)


        self.pointfrequency = self.__c3d['header']['points']['frame_rate']
        self.analogfrequnecy = self.__c3d['header']['analogs']['frame_rate']

        # Get events data
        self.eventdata = [
            list(self.__c3d['parameters']['EVENT']['TIMES']['value'][1]),
            list(self.__c3d['parameters']['EVENT']['CONTEXTS']['value']),
            list(self.__c3d['parameters']['EVENT']['LABELS']['value'])
        ]
        self.eventdata = np.transpose(np.array(self.eventdata))
        self.eventdata = sorted(self.eventdata, key=lambda x: x[0])
        return
    
    def test_Events(self):
        self.__Events = Events(self.eventdata, self.pointfrequency, self.analogfrequnecy)
        print("Event class test passed\n")
        
        return 

class KinematicsTest(unittest.TestCase):

    def setUp(self):
        self.__c3dpath = testc3dpath
        self.__c3d = c3d(self.__c3dpath)

        self.pointlabels = self.__c3d['parameters']['POINT']['LABELS']['value'] 
        self.pointdata = self.__c3d['data']['points']

        # Get event info
        self.pointfrequency = self.__c3d['header']['points']['frame_rate']
        self.analogfrequnecy = self.__c3d['header']['analogs']['frame_rate']

        self.eventdata = [
            list(self.__c3d['parameters']['EVENT']['TIMES']['value'][1]),
            list(self.__c3d['parameters']['EVENT']['CONTEXTS']['value']),
            list(self.__c3d['parameters']['EVENT']['LABELS']['value'])
        ]
        self.eventdata = np.transpose(np.array(self.eventdata))
        self.eventdata = sorted(self.eventdata, key=lambda x: x[0])
        self.__Events = Events(self.eventdata, self.pointfrequency, self.analogfrequnecy)
        return


    def test_Kinematics(self):

        self.__Kinematics = Kinematics(self.pointlabels, self.pointdata, self.__Events.full_cycle_point)
        print("Kinematics class test passed\n")
        return 

class KineticsTest(unittest.TestCase):

    def setUp(self):
        self.__c3dpath = testc3dpath
        self.__c3d = c3d(self.__c3dpath)

        self.pointlabels = self.__c3d['parameters']['POINT']['LABELS']['value'] 

        self.pointdata = self.__c3d['data']['points']

        # Get event info
        self.pointfrequency = self.__c3d['header']['points']['frame_rate']
        self.analogfrequnecy = self.__c3d['header']['analogs']['frame_rate']

        self.eventdata = [
            list(self.__c3d['parameters']['EVENT']['TIMES']['value'][1]),
            list(self.__c3d['parameters']['EVENT']['CONTEXTS']['value']),
            list(self.__c3d['parameters']['EVENT']['LABELS']['value'])
        ]
        self.eventdata = np.transpose(np.array(self.eventdata))
        self.eventdata = sorted(self.eventdata, key=lambda x: x[0])
        self.__Events = Events(self.eventdata, self.pointfrequency, self.analogfrequnecy)

        return
    
    def test_Kinetics(self):
        
        self.__Kinetics = Kinetics(self.pointlabels, self.pointdata, self.__Events.full_cycle_point)
        print("Kinetics class test passed\n")
        return

class EMGTest(unittest.TestCase):

    def setUp(self):
        self.__c3dpath = testc3dpath
        self.__c3d = c3d(self.__c3dpath)

        self.analogchannels = np.transpose(np.array([self.__c3d['parameters']['ANALOG']['LABELS']['value'], self.__c3d['parameters']['ANALOG']['DESCRIPTIONS']['value']]))
        self.analogdata = self.__c3d['data']['analogs'][0]
        return
    
    def test_EMG(self):

        self.__EMG = EMG(self.analogchannels, self.analogdata)
        print("EMG class test passed\n")
        return

class GPSKinematicsTest(unittest.TestCase):

    def setUp(self):
        self.__c3dpath = testc3dpath
        self.__c3d = c3d(self.__c3dpath)

        self.pointlabels = self.__c3d['parameters']['POINT']['LABELS']['value'] 
        self.pointdata = self.__c3d['data']['points']
    
        # get event data
        self.pointfrequency = self.__c3d['header']['points']['frame_rate']
        self.analogfrequnecy = self.__c3d['header']['analogs']['frame_rate']

        # Get events data
        self.eventdata = [
            list(self.__c3d['parameters']['EVENT']['TIMES']['value'][1]),
            list(self.__c3d['parameters']['EVENT']['CONTEXTS']['value']),
            list(self.__c3d['parameters']['EVENT']['LABELS']['value'])
        ]
        self.eventdata = np.transpose(np.array(self.eventdata))
        self.eventdata = sorted(self.eventdata, key=lambda x: x[0])
        self.__Events = Events(self.eventdata, self.pointfrequency, self.analogfrequnecy)
        
        self.__Kinematics = Kinematics(self.pointlabels, self.pointdata, self.__Events.full_cycle_point)
        return
    
    def test_GPSKinematics(self):
        
        self.__GPSKintematics =  GPSKinematics(self.__Kinematics.kinematics, self.__Events.l_cycle_point, self.__Events.r_cycle_point)
        print("GPSKinematics class test passed\n")
        return

class TrialDataTest(unittest.TestCase):

    def setUp(self):
        self.__c3dpath = testc3dpath
        self.__c3d = c3d(self.__c3dpath)
        return
    
    def test_Trial(self):

        self.__Trial = TrialData(self.__c3d)

        print("Trial class test passed\n")
        return


if __name__=="__main__":
    unittest.main()   