from PyQt5 import QtGui, QtWidgets, QtCore
import sys, time, tempfile, os, pathlib, json, subprocess
import multiprocessing # for the camera streams !!
import numpy as np

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from assembling.saving import *

if not sys.argv[-1]=='no-stim':
    from visual_stim.stimuli import build_stim
    from visual_stim.default_params import SETUP
else:
    SETUP = [None]

from misc.style import set_app_icon, set_dark_style
try:
    from hardware_control.NIdaq.main import Acquisition
    from hardware_control.FLIRcamera.recording import CameraAcquisition
    from hardware_control.LogitechWebcam.preview import launch_RigView
except ModuleNotFoundError:
    # just to be able to work on the UI without the modules
    print('The hardware control modules were not found...')

# os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
## NASTY workaround to the error:
# ** OMP: Error #15: Initializing libiomp5md.dll, but found libiomp5md.dll already initialized. **

base_path = str(pathlib.Path(__file__).resolve().parents[0])
settings_filename = os.path.join(base_path, 'settings.npy')

STEP_FOR_CA_IMAGING = {"channel":0, "onset": 0.1, "duration": .3, "value":5.0}

class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self, app, args=None):
        """
        """
        super(MainWindow, self).__init__()
        
        self.setWindowTitle('Experimental module -- Physiology of Visual Circuits')
        self.setGeometry(50, 50, 550, 370)

        ##########################################################
        ##########################################################
        ##########################################################
        self.quit_event = multiprocessing.Event() # to control the RigView !
        self.run_event = multiprocessing.Event() # to turn on and off recordings execute through multiprocessing.Process
        # self.camready_event = multiprocessing.Event() # to turn on and off recordings execute through multiprocessing.Process
        self.stim, self.acq, self.init, self.setup, self.stop_flag = None, None, False, SETUP[0], False
        self.FaceCamera, self.FaceCamera_process = None, None
        self.RigView_process = None
        self.params_window = None

        ##########################################################
        ##########################################################
        ##########################################################
        rml = QtWidgets.QLabel('   '+'-'*40+" Recording modalities "+'-'*40, self)
        rml.move(30, 5)
        rml.setMinimumWidth(500)
        self.VisualStimButton = QtWidgets.QPushButton("Visual-Stim", self)
        self.VisualStimButton.move(30, 40)
        self.LocomotionButton = QtWidgets.QPushButton("Locomotion", self)
        self.LocomotionButton.move(130, 40)
        self.ElectrophyButton = QtWidgets.QPushButton("Electrophy", self)
        self.ElectrophyButton.move(230, 40)
        self.FaceCameraButton = QtWidgets.QPushButton("FaceCamera", self)
        self.FaceCameraButton.move(330, 40)
        self.FaceCameraButton.activated.connect(self.start_FaceCamera)
        self.CaImagingButton = QtWidgets.QPushButton("CaImaging", self)
        self.CaImagingButton.move(430, 40)
        for button in [self.VisualStimButton, self.LocomotionButton, self.ElectrophyButton,
                       self.FaceCameraButton, self.CaImagingButton]:
            button.setCheckable(True)
        for button in [self.VisualStimButton, self.LocomotionButton]:
            button.setChecked(True)
            
        # config choice
        # QtWidgets.QLabel(" ======= Config : ======", self).move(170, 90)
        QtWidgets.QLabel("  => Config :", self).move(160, 90)
        self.cbc = QtWidgets.QComboBox(self)
        self.cbc.setMinimumWidth(270)
        self.cbc.move(250, 90)
        self.cbc.activated.connect(self.update_config)

        # subject choice
        QtWidgets.QLabel("-> Subject :", self).move(100, 125)
        self.cbs = QtWidgets.QComboBox(self)
        self.cbs.setMinimumWidth(340)
        self.cbs.move(180, 125)
        self.cbs.activated.connect(self.update_subject)
        
        # protocol choice
        QtWidgets.QLabel(" Visual Protocol :", self).move(20, 160)
        self.cbp = QtWidgets.QComboBox(self)
        self.cbp.setMinimumWidth(390)
        self.cbp.move(130, 160)
        self.cbp.activated.connect(self.update_protocol)

        # buttons and functions
        LABELS = ["i) Initialize", "r) Run", "s) Stop", "q) Quit"]
        FUNCTIONS = [self.initialize, self.run, self.stop, self.quit]
        
        mainMenu = self.menuBar()
        self.fileMenu = mainMenu.addMenu('')

        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('ready to select a protocol/config')
        for func, label, shift in zip(FUNCTIONS, LABELS,\
                                      110*np.arange(len(LABELS))):
            btn = QtWidgets.QPushButton(label, self)
            btn.clicked.connect(func)
            btn.setMinimumWidth(110)
            btn.move(50+shift, 220)
            action = QtWidgets.QAction(label, self)
            action.setShortcut(label.split(')')[0])
            action.triggered.connect(func)
            self.fileMenu.addAction(action)
            
        QtWidgets.QLabel("Notes: ", self).move(40, 265)
        self.qmNotes = QtWidgets.QTextEdit('', self)
        self.qmNotes.move(90, 270)
        self.qmNotes.setMinimumWidth(250)
        self.qmNotes.setMinimumHeight(60)
        
        btn = QtWidgets.QPushButton('Save\nSettings', self)
        btn.clicked.connect(self.save_settings)
        btn.setMinimumWidth(70)
        btn.setMinimumHeight(50)
        btn.move(380,275)

        ##########################################################
        ##########################################################
        ##########################################################
        self.config, self.protocol, self.subject = None, None, None
        
        self.get_config_list()
        self.load_settings()
        self.datafolder = None
	    
        self.experiment = {} # storing the specifics of an experiment
        
        self.show()

    ### GUI FUNCTIONS ###
    
    def save_settings(self):
        settings = {'config':self.cbc.currentText(),
                    'protocol':self.cbp.currentText(),
                    'subject':self.cbs.currentText()}
        for label, button in zip(['VisualStimButton', 'LocomotionButton', 'ElectrophyButton',
                                  'FaceCameraButton', 'CaImagingButton'],
                                 [self.VisualStimButton, self.LocomotionButton, self.ElectrophyButton,
                                  self.FaceCameraButton, self.CaImagingButton]):
            settings[label] = button.isChecked()
        np.save(settings_filename, settings)
        self.statusBar.showMessage('settings succesfully saved !')

    def load_settings(self):
        if os.path.isfile(settings_filename):
            settings = np.load(settings_filename, allow_pickle=True).item()
            if settings['config'] in self.config_list:
                self.cbc.setCurrentText(settings['config'])
                self.update_config()
            if settings['protocol'] in self.protocol_list:
                self.cbp.setCurrentText(settings['protocol'])
                self.update_protocol()
            if settings['subject'] in self.subjects:
                self.cbs.setCurrentText(settings['subject'])
                self.update_subject()
            for label, button in zip(['VisualStimButton', 'LocomotionButton', 'ElectrophyButton',
                                      'FaceCameraButton', 'CaImagingButton'],
                                     [self.VisualStimButton, self.LocomotionButton, self.ElectrophyButton,
                                      self.FaceCameraButton, self.CaImagingButton]):
                button.setChecked(settings[label])
        if (self.config is None) or (self.protocol is None) or (self.subject is None):
            self.statusBar.showMessage(' /!\ Problem in loading settings /!\  ')
    
    def get_config_list(self):
        files = os.listdir(os.path.join(base_path, 'configs'))
        self.config_list = [f.replace('.json', '') for f in files if f.endswith('.json')]
        self.cbc.addItems(self.config_list)
        self.update_config()
        
    def update_config(self):
        fn = os.path.join(base_path, 'configs', self.cbc.currentText()+'.json')
        with open(fn) as f:
            self.config = json.load(f)
        self.get_protocol_list()
        self.get_subject_list()
        self.root_datafolder = os.path.join(os.path.expanduser('~'), self.config['root_datafolder'])
        self.Setup = self.config['Setup']

    def get_protocol_list(self):
        if self.config['protocols']=='all':
            files = os.listdir(os.path.join(base_path, 'protocols'))
            self.protocol_list = [f.replace('.json', '') for f in files if f.endswith('.json')]
        else:
            self.protocol_list = self.config['protocols']
        self.cbp.clear()
        self.cbp.addItems(['None']+self.protocol_list)

    def update_protocol(self):
        if self.cbp.currentText()=='None':
            self.protocol = {}
        else:
            fn = os.path.join(base_path, 'protocols', self.cbp.currentText()+'.json')
            with open(fn) as f:
                self.protocol = json.load(f)
            self.protocol['Setup'] = self.config['Setup'] # override params
            self.protocol['data-folder'] = self.root_datafolder
        
    def get_subject_list(self):
        with open(os.path.join(base_path, 'subjects', self.config['subjects_file'])) as f:
            self.subjects = json.load(f)
        self.cbs.clear()
        self.cbs.addItems(self.subjects.keys())
        
    def update_subject(self):
        self.subject = self.subjects[self.cbs.currentText()]

    def start_FaceCamera(self):
        if self.FaceCameraButton.isChecked() and (self.FaceCamera is None):
            self.FaceCamera = CameraAcquisition()
        else:
            self.FaceCamera = None
        
    def init_FaceCamera(self):
        if self.FaceCamera_process is None:
            self.FaceCamera_process = multiprocessing.Process(target=launch_FaceCamera,
                                        args=(self.run_event , self.quit_event,
                                              self.root_datafolder,
                                              {'frame_rate':self.config['FaceCamera-frame-rate']}))
            self.FaceCamera_process.start()
            print('  starting FaceCamera stream [...] ')
            time.sleep(6)
            print('[ok] FaceCamera ready ! ')
        else:
            print('[ok] FaceCamera already initialized ')
            
        return True
            
    def rigview(self):
        if self.RigView_process is not None:
            self.RigView_process.terminate()
        self.statusBar.showMessage('Initializing RigView stream [...]')
        self.RigView_process = multiprocessing.Process(target=launch_RigView,
                          args=(self.run_event , self.quit_event, self.datafolder))
        self.RigView_process.start()
        time.sleep(5)
        self.statusBar.showMessage('Setup ready')
        
    def initialize(self):

        ### set up all metadata
        self.metadata = {'config':self.cbc.currentText(),
                         'protocol':self.cbp.currentText(),
                         'notes':self.qmNotes.toPlainText(),
                         'subject_ID':self.cbs.currentText(),
                         'subject_props':self.subject} # re-initialize metadata

        for d in [self.config, self.protocol]:
            for key in d:
                self.metadata[key] = d[key]
        
        # Setup configuration
        for modality, button in zip(['VisualStim', 'Locomotion', 'Electrophy', 'FaceCamera', 'CaImaging'],
                                    [self.VisualStimButton, self.LocomotionButton, self.ElectrophyButton,
                                     self.FaceCameraButton, self.CaImagingButton]):
            self.metadata[modality] = bool(button.isChecked())

        if self.cbp.currentText()=='None':
            self.statusBar.showMessage('[...] initializing acquisition')
        else:
            self.statusBar.showMessage('[...] initializing acquisition & stimulation')

        self.filename = generate_filename_path(self.root_datafolder,
                                               filename='metadata', extension='.npy',
                                               with_FaceCamera_frames_folder=self.metadata['FaceCamera'],
                                               with_screen_frames_folder=self.metadata['VisualStim'])
        self.datafolder = os.path.dirname(self.filename)
            
        if self.metadata['protocol']!='None':
            with open(os.path.join(base_path, 'protocols', self.metadata['protocol']+'.json'), 'r') as fp:
                self.protocol = json.load(fp)
        else:
                self.protocol = {}

        # init facecamera
        if self.metadata['FaceCamera']:
            self.statusBar.showMessage('Initializing Camera stream [...]')
            self.init_FaceCamera()
                
        # init visual stimulation
        if self.metadata['VisualStim'] and len(self.protocol.keys())>0:
            self.stim = build_stim(self.protocol)
            np.save(os.path.join(self.datafolder, 'visual-stim.npy'), self.stim.experiment)
            print('[ok] Visual-stimulation data saved as "%s"' % os.path.join(self.datafolder, 'visual-stim.npy'))
            if 'time_stop' in self.stim.experiment:
                max_time = self.stim.experiment['time_stop'][-1]+20
            elif 'refresh_times' in self.stim.experiment:
                max_time = self.stim.experiment['refresh_times'][-1]+20
            else:
                max_time = 1*60*60 # 1 hour, should be stopped manually
        else:
            max_time = 1*60*60 # 1 hour, should be stopped manually
            self.stim = None

        output_steps = []
        if self.metadata['CaImaging']:
            output_steps.append(self.metadata['STEP_FOR_CA_IMAGING'])

        # --------------- #
        ### NI daq init ###   ## we override parameters based on the chosen modalities if needed
        # --------------- #
        if self.metadata['VisualStim'] and (self.metadata['NIdaq-analog-input-channels']<1):
            self.metadata['NIdaq-analog-input-channels'] = 1 # at least one
        if self.metadata['Electrophy'] and (self.metadata['NIdaq-analog-input-channels']<2):
            self.metadata['NIdaq-analog-input-channels'] = 2
        if self.metadata['Locomotion'] and (self.metadata['NIdaq-digital-input-channels']<2):
            self.metadata['NIdaq-digital-input-channels'] = 2
        try:
            self.acq = Acquisition(dt=1./self.metadata['NIdaq-acquisition-frequency'],
                                   Nchannel_analog_in=self.metadata['NIdaq-analog-input-channels'],
                                   Nchannel_digital_in=self.metadata['NIdaq-digital-input-channels'],
                                   max_time=max_time,
                                   output_steps=output_steps,
                                   filename= self.filename.replace('metadata', 'NIdaq'))
        except BaseException as e:
            print(e)
            print(' /!\ PB WITH NI-DAQ /!\ ')
            self.acq = None

        self.init = True
        self.save_experiment() # saving all metadata after full initialization
        
        if self.cbp.currentText()=='None':
            self.statusBar.showMessage('Acquisition ready !')
        else:
            self.statusBar.showMessage('Acquisition & Stimulation ready !')


        
    def run(self):
        self.stop_flag=False
        self.run_event.set() # start the run flag for the facecamera
        
        if ((self.acq is None) and (self.stim is None)) or not self.init:
            self.statusBar.showMessage('Need to initialize the stimulation !')
        elif (self.stim is None) and (self.acq is not None) and (self.FaceCamera is not None):
            # FaceCamera
            self.FaceCamera.rec(self.filename.replace('metadata.npy',
                                                      'FaceCamera.nwb'))
            self.acq.launch()
            self.statusBar.showMessage('Acquisition running [...]')
        else:
            self.statusBar.showMessage('Stimulation & Acquisition running [...]')
            # FaceCamera
            if self.FaceCamera is not None:
                self.FaceCamera.rec(self.filename.replace('metadata.npy',
                                                          'FaceCamera.nwb'))
            # Ni-Daq
            if self.acq is not None:
                self.acq.launch()
            # run visual stim
            if self.metadata['VisualStim']:
                self.stim.run(self)
            # ========================
            # ---- HERE IT RUNS [...]
            # ========================
            # stop and clean up things
            if self.metadata['FaceCamera']:
                self.run_event.clear() # this will close the camera process
            # close visual stim
            if self.metadata['VisualStim']:
                self.stim.close() # close the visual stim
            if self.acq is not None:
                self.acq.close()
            if self.metadata['CaImaging'] and not self.stop_flag: # outside the pure acquisition case
                self.send_CaImaging_Stop_signal()
                
        self.init = False
        print(100*'-', '\n', 50*'=')
        
    
    def stop(self):
        self.run_event.clear() # this will close the camera process
        self.stop_flag=True
        if self.acq is not None:
            self.acq.close()
        if self.stim is not None:
            self.stim.close()
            self.init = False
        if self.metadata['CaImaging']:
            self.send_CaImaging_Stop_signal()
        self.statusBar.showMessage('stimulation stopped !')
        print(100*'-', '\n', 50*'=')
        
    def send_CaImaging_Stop_signal(self):
        self.statusBar.showMessage('sending stop signal for 2-Photon acq.')
        acq = Acquisition(dt=1e-3, # 1kHz
                          Nchannel_analog_in=1, Nchannel_digital_in=0,
                          max_time=1.1,
                          buffer_time=0.1,
                          output_steps= [STEP_FOR_CA_IMAGING],
                          filename=None)
        acq.launch()
        time.sleep(1.1)
        acq.close()
    
    def quit(self):
        self.quit_event.set()
        if self.acq is not None:
            self.acq.close()
        if self.stim is not None:
            self.stim.quit()
        QtWidgets.QApplication.quit()

    def save_experiment(self):
        # SAVING THE METADATA FILES
        np.save(os.path.join(self.datafolder, 'metadata.npy'), self.metadata)
        print('[ok] Metadata data saved as: %s ' % os.path.join(self.datafolder, 'metadata.npy'))
        self.statusBar.showMessage('Metadata saved as: "%s" ' % os.path.join(self.datafolder, 'metadata.npy'))

        
def run(app, args=None):
    return MainWindow(app, args)
    
if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = run(app)
    sys.exit(app.exec_())
