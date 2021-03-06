import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui, QtCore
import os, sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from pupil import roi, process
from Ca_imaging.tools import compute_CaImaging_trace
from dataviz.tools import *


t = np.linspace(0, 2*np.pi)

def raw_data_plot(self, tzoom,
                  plot_update=True,
                  with_images=False,
                  with_roi=False,
                  with_scatter=False):

    iplot = 0
    scatter = []
    self.plot.clear()
    
    ## -------- Screen --------- ##

    if 'Photodiode-Signal' in self.nwbfile.acquisition:
        
        i1, i2 = convert_times_to_indices(*tzoom, self.nwbfile.acquisition['Photodiode-Signal'])
        if self.no_subsampling:
            isampling = np.arange(i1,i2)
        else:
            isampling = np.unique(np.linspace(i1, i2, self.settings['Npoints'], dtype=int))
        y = scale_and_position(self,self.nwbfile.acquisition['Photodiode-Signal'].data[list(isampling)], i=iplot)
        iplot+=1
        self.plot.plot(convert_index_to_time(isampling, self.nwbfile.acquisition['Photodiode-Signal']), y,
                       pen=pg.mkPen(color=self.settings['colors']['Screen']))

    ## -------- Locomotion --------- ##
    
    if 'Running-Speed' in self.nwbfile.acquisition:
        
        i1, i2 = convert_times_to_indices(*tzoom, self.nwbfile.acquisition['Running-Speed'])
        if self.no_subsampling:
            isampling = np.arange(i1+1, i2-1)
        else:
            isampling = np.unique(np.linspace(i1+1, i2-1, self.settings['Npoints'], dtype=int))
        y = scale_and_position(self,self.nwbfile.acquisition['Running-Speed'].data[list(isampling)], i=iplot)
        iplot+=1
        self.plot.plot(convert_index_to_time(isampling, self.nwbfile.acquisition['Running-Speed']), y,
                       pen=pg.mkPen(color=self.settings['colors']['Locomotion']))
            

    ## -------- FaceCamera, Face motion and Pupil-Size --------- ##
    
    if 'FaceCamera' in self.nwbfile.acquisition:
        
        i0 = convert_time_to_index(self.time, self.nwbfile.acquisition['FaceCamera'])
        self.pFaceimg.setImage(self.nwbfile.acquisition['FaceCamera'].data[i0])
        
        if hasattr(self, 'FaceCameraFrameLevel'):
            self.plot.removeItem(self.FaceCameraFrameLevel)
        self.FaceCameraFrameLevel = self.plot.plot(self.nwbfile.acquisition['FaceCamera'].timestamps[i0]*np.ones(2),
                                                   [0, y.max()], pen=pg.mkPen(color=self.settings['colors']['FaceMotion']), linewidth=0.5)

    if 'FaceMotion' in self.nwbfile.acquisition:
        
        i0 = convert_time_to_index(self.time, self.nwbfile.acquisition['FaceMotion'])
        self.pFacemotionimg.setImage(self.nwbfile.acquisition['FaceMotion'].data[i0])
        if hasattr(self, 'FacemotionFrameLevel'):
            self.plot.removeItem(self.FacemotionFrameLevel)
        self.FacemotionFrameLevel = self.plot.plot(self.nwbfile.acquisition['FaceMotion'].timestamps[i0]*np.ones(2),
                                                   [0, y.max()], pen=pg.mkPen(color=self.settings['colors']['FaceMotion']), linewidth=0.5)
        t_facemotion_frame = self.nwbfile.acquisition['FaceMotion'].timestamps[i0]
        
    else:
        t_facemotion_frame = None
        
    if 'FaceMotion' in self.nwbfile.processing:

        i1, i2 = convert_times_to_indices(*self.tzoom, self.nwbfile.processing['FaceMotion'].data_interfaces['face-motion'])

        t = self.nwbfile.processing['FaceMotion'].data_interfaces['face-motion'].timestamps[i1:i2]
        
        y = scale_and_position(self, self.nwbfile.processing['FaceMotion'].data_interfaces['face-motion'].data[i1:i2],
                               i=iplot)
        self.plot.plot(t, y, pen=pg.mkPen(color=self.settings['colors']['FaceMotion']))
            
        iplot+=1

        # self.facemotionROI        
        
    if 'Pupil' in self.nwbfile.acquisition:
        
        i0 = convert_time_to_index(self.time, self.nwbfile.acquisition['Pupil'])
        img = self.nwbfile.acquisition['Pupil'].data[i0]
        img = (img-img.min())/(img.max()-img.min())
        self.pPupilimg.setImage(255*(1-np.exp(-img/0.2)))
        if hasattr(self, 'PupilFrameLevel'):
            self.plot.removeItem(self.PupilFrameLevel)
        self.PupilFrameLevel = self.plot.plot(self.nwbfile.acquisition['Pupil'].timestamps[i0]*np.ones(2),
                                              [0, y.max()], pen=pg.mkPen(color=self.settings['colors']['Pupil']), linewidth=0.5)
        t_pupil_frame = self.nwbfile.acquisition['Pupil'].timestamps[i0]
    else:
        t_pupil_frame = None
        
    if 'Pupil' in self.nwbfile.processing:

        i1, i2 = convert_times_to_indices(*self.tzoom, self.nwbfile.processing['Pupil'].data_interfaces['cx'])

        t = self.nwbfile.processing['Pupil'].data_interfaces['sx'].timestamps[i1:i2]
        
        y = scale_and_position(self,
                               np.max([self.nwbfile.processing['Pupil'].data_interfaces['sx'].data[i1:i2],
                                       self.nwbfile.processing['Pupil'].data_interfaces['sy'].data[i1:i2]], axis=0),
                               i=iplot)

        self.plot.plot(t, y, pen=pg.mkPen(color=self.settings['colors']['Pupil']))

        # adding blinking flag (a thick line at the bottom)
        if 'blinking' in self.nwbfile.processing['Pupil'].data_interfaces:
            cond = (self.nwbfile.processing['Pupil'].data_interfaces['blinking'].data[i1:i2]==1) & np.isfinite(y)
            if np.sum(cond):
                self.plot.plot(t[cond],y[cond].min()+0*t[cond], pen=None, symbol='o',
                               symbolPen=pg.mkPen(color=self.settings['colors']['Pupil'], width=0),                                      
                               symbolBrush=pg.mkBrush(0, 0, 255, 255), symbolSize=7)
                
        iplot+=1

        # plotting a circle for the pupil fit
        coords = []
        if t_pupil_frame is not None:
            i0 = convert_time_to_index(t_pupil_frame, self.nwbfile.processing['Pupil'].data_interfaces['sx'])
            for key in ['cx', 'cy', 'sx', 'sy']:
                coords.append(self.nwbfile.processing['Pupil'].data_interfaces[key].data[i0]*self.FaceCamera_mm_to_pix)
            if 'angle' in self.nwbfile.processing['Pupil'].data_interfaces:
                coords.append(self.nwbfile.processing['Pupil'].data_interfaces['angle'].data[i0])
            else:
                coords.append(0)

            self.pupilContour.setData(*process.ellipse_coords(*coords, transpose=True), size=3, brush=pg.mkBrush(255,0,0))
            

    # ## -------- Electrophy --------- ##
    
    if ('Electrophysiological-Signal' in self.nwbfile.acquisition):
        # deprecated
        
        i1 = convert_time_to_index(tzoom[0], self.nwbfile.acquisition['Electrophysiological-Signal'])+1
        i2 = convert_time_to_index(tzoom[1], self.nwbfile.acquisition['Electrophysiological-Signal'])-1
        if self.no_subsampling:
            isampling = np.arange(i1,i2)
        else:
            isampling = np.unique(np.linspace(i1, i2, self.settings['Npoints'], dtype=int))
        y = scale_and_position(self,self.nwbfile.acquisition['Electrophysiological-Signal'].data[list(isampling)], i=iplot)
        iplot+=1
        self.plot.plot(convert_index_to_time(isampling, self.nwbfile.acquisition['Electrophysiological-Signal']), y,
                       pen=pg.mkPen(color=self.settings['colors']['Electrophy']))

    if ('LFP' in self.nwbfile.acquisition):
        
        i1 = convert_time_to_index(tzoom[0], self.nwbfile.acquisition['LFP'])+1
        i2 = convert_time_to_index(tzoom[1], self.nwbfile.acquisition['LFP'])-1
        if self.no_subsampling:
            isampling = np.arange(i1,i2)
        else:
            isampling = np.unique(np.linspace(i1, i2, self.settings['Npoints'], dtype=int))
        y = scale_and_position(self,self.nwbfile.acquisition['LFP'].data[list(isampling)], i=iplot)
        iplot+=1
        self.plot.plot(convert_index_to_time(isampling, self.nwbfile.acquisition['LFP']), y,
                       pen=pg.mkPen(color=self.settings['colors']['LFP']))


    if ('Vm' in self.nwbfile.acquisition):
        
        i1 = convert_time_to_index(tzoom[0], self.nwbfile.acquisition['Vm'])+1
        i2 = convert_time_to_index(tzoom[1], self.nwbfile.acquisition['Vm'])-1
        if self.no_subsampling:
            isampling = np.arange(i1,i2)
        else:
            isampling = np.unique(np.linspace(i1, i2, self.settings['Npoints'], dtype=int))
        y = scale_and_position(self,self.nwbfile.acquisition['Vm'].data[list(isampling)], i=iplot)
        iplot+=1
        self.plot.plot(convert_index_to_time(isampling, self.nwbfile.acquisition['Vm']), y,
                       pen=pg.mkPen(color=self.settings['colors']['Vm']))

        
    # ## -------- Calcium --------- ##
    
    # if (self.time==0) and ('ophys' in self.nwbfile.processing):
    if ('ophys' in self.nwbfile.processing):
        self.pCaimg.setImage(self.nwbfile.processing['ophys'].data_interfaces['Backgrounds_0'].images[self.CaImaging_bg_key][:]) # plotting the mean image
        
    if 'CaImaging-TimeSeries' in self.nwbfile.acquisition:
        i0 = convert_time_to_index(self.time, self.nwbfile.acquisition['CaImaging-TimeSeries'])
        # self.pCaimg.setImage(self.nwbfile.acquisition['CaImaging-TimeSeries'].data[i0,:,:]) # REMOVE NOW, MAYBE REINTRODUCE
        if hasattr(self, 'CaFrameLevel'):
            self.plot.removeItem(self.CaFrameLevel)
        self.CaFrameLevel = self.plot.plot(self.nwbfile.acquisition['CaImaging-TimeSeries'].timestamps[i0]*np.ones(2), [0, y.max()],
                                           pen=pg.mkPen(color=self.settings['colors']['CaImaging']), linewidth=0.5)
        
    if ('ophys' in self.nwbfile.processing) and with_roi:
        if hasattr(self, 'ROIscatter'):
            self.pCa.removeItem(self.ROIscatter)
        self.ROIscatter = pg.ScatterPlotItem()
        X, Y = [], []
        for ir in self.validROI_indices[self.roiIndices]:
            indices = np.arange((self.pixel_masks_index[ir-1] if ir>0 else 0),
                                (self.pixel_masks_index[ir] if ir<len(self.validROI_indices) else len(self.pixel_masks_index)))
            x = [self.pixel_masks[ii][1] for ii in indices]
            y = [self.pixel_masks[ii][0] for ii in indices]
            X += list(np.mean(x)+3*np.std(x)*np.cos(t)) # TO PLOT CIRCLES
            Y += list(np.mean(y)+3*np.std(y)*np.sin(t))
            # X += x # TO PLOT THE REAL ROIS
            # Y += y
        self.ROIscatter.setData(X, Y, size=1, brush=pg.mkBrush(0,255,0))
        self.pCa.addItem(self.ROIscatter)

    if ('ophys' in self.nwbfile.processing) and (self.roiIndices is not None):
        i1 = convert_time_to_index(self.tzoom[0], self.Neuropil, axis=1)
        i2 = convert_time_to_index(self.tzoom[1], self.Neuropil, axis=1)
        if self.no_subsampling:
            isampling = np.arange(i1,i2)
        else:
            isampling = np.unique(np.linspace(i1, i2, self.settings['Npoints'], dtype=int))
        tt = np.array(self.Neuropil.timestamps[:])[isampling]

        if self.roiPick.text()=='sum' or (len(self.roiIndices)==1):
            y = scale_and_position(self, compute_CaImaging_trace(self, self.CaImaging_key, self.roiIndices).sum(axis=0)[isampling], i=iplot) # valid ROIs inside
            self.plot.plot(tt, y, pen=pg.mkPen(color=(0,250,0), linewidth=1))
            # if self.CaImaging_key=='Fluorescence':
            #     nrnp = scale_and_position(self, y, value=self.Neuropil.data[:,isampling][self.validROI_indices[self.roiIndices],:].sum(axis=0), i=iplot)
            #     self.plot.plot(tt, nrnp, pen=pg.mkPen(color=(255,255,255), linewidth=0.2))
        else:
            for n, ir in enumerate(self.roiIndices):
                y = scale_and_position(self, compute_CaImaging_trace(self, self.CaImaging_key, [ir]).sum(axis=0)[isampling], i=iplot)+n/2.
                self.plot.plot(tt, y, pen=pg.mkPen(color=np.random.randint(255, size=3), linewidth=1))
                # if self.CaImaging_key=='Fluorescence':
                #     nrnp = scale_and_position(self, y, value=self.Neuropil.data[:,isampling][self.validROI_indices[ir],:], i=iplot)+n/2.
                #     self.plot.plot(tt, nrnp, pen=pg.mkPen(color=(255,255,255), linewidth=0.2))
        iplot += 1

    # ## -------- Visual Stimulation --------- ##

    if self.visual_stim is not None:
        
        icond = np.argwhere((self.nwbfile.stimulus['time_start_realigned'].data[:]<=self.time) & \
                            (self.nwbfile.stimulus['time_stop_realigned'].data[:]>=self.time)).flatten()
        if len(icond)>0:
            self.pScreenimg.setImage(255*self.visual_stim.get_image(icond[0],
                                     self.time-self.nwbfile.stimulus['time_start_realigned'].data[icond[0]]))
        elif self.time<=self.nwbfile.stimulus['time_start_realigned'].data[0]: # PRE-STIM
            self.pScreenimg.setImage(255*self.visual_stim.get_prestim_image())
        elif self.time>=self.nwbfile.stimulus['time_stop_realigned'].data[-1]: # POST-STIM
            self.pScreenimg.setImage(255*self.visual_stim.get_poststim_image())
        else: # INTER-STIM
            self.pScreenimg.setImage(255*self.visual_stim.get_interstim_image())
            
        self.pScreenimg.setLevels([0,255])

    if (self.visual_stim is not None) and ('time_start_realigned' in self.nwbfile.stimulus) and ('time_stop_realigned' in self.nwbfile.stimulus):
        # if visual-stim we highlight the stim periods
        icond = np.argwhere((self.nwbfile.stimulus['time_start_realigned'].data[:]>tzoom[0]-10) & \
                            (self.nwbfile.stimulus['time_stop_realigned'].data[:]<tzoom[1]+10)).flatten()

        if hasattr(self, 'StimFill') and self.StimFill is not None:
            for x in self.StimFill:
                self.plot.removeItem(x)

        X, Y = [], []
        if len(icond)>0:
            self.StimFill = []
            # for i in icond:
            for i in range(max([0,icond[0]-1]),
                           min([icond[-1]+1,self.nwbfile.stimulus['time_stop_realigned'].data.shape[0]-1])):
                t0 = self.nwbfile.stimulus['time_start_realigned'].data[i]
                t1 = self.nwbfile.stimulus['time_stop_realigned'].data[i]
                self.StimFill.append(self.plot.plot([t0, t1], [0, 0],
                                fillLevel=y.max(), brush=(150,150,150,80)))

    # if with_scatter and hasattr(self, 'scatter'):
    #     self.plot.removeItem(self.scatter)
    #     self.scatter.setData([s[0] for s in scatter],
    #                          [s[1] for s in scatter],
    #                          size=10, brush=pg.mkBrush(255,255,255))
    #     self.plot.addItem(self.scatter)

    self.plot.setRange(xRange=tzoom, yRange=[0,y.max()], padding=0.0)
    self.frameSlider.setValue(int(self.settings['Npoints']*(self.time-tzoom[0])/(tzoom[1]-tzoom[0])))
    
    self.plot.show()
