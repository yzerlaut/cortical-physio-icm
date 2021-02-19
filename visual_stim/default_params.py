import numpy as np

PRESENTATIONS = ['Single-Stimulus', 'Stimuli-Sequence', 'Randomized-Sequence']

BLANK_SCREENS = ['Black Screen' ,'Grey Screen', 'White Screen']
NAME_TO_COLOR = {'Black Screen':-1, 'Grey Screen':0, 'White Screen':1}
SETUP = ['demo-mode', 'Bacci-2P-setup']

PRESENTATION = {
    # duration
    'presentation-duration':5.,
    'presentation-prestim-period':2,
    'presentation-interstim-period':2,
    'presentation-poststim-period':2,
    # blank screen
    'presentation-prestim-screen':-1,
    'presentation-interstim-screen':-1,
    'presentation-poststim-screen':-1,
    # repetition
    'N-repeat':2,
    'shuffling-seed':1,
    'starting-index':0,
}

STIMULI = {
    
    # simple screen at constant light level
    'light-level':{
        'light-level (lum.)':0.5,
        # range
        'light-level-1':-1., 'light-level-2':1., 'N-light-level':3},
    
    # full-field static grating
    'full-field-grating':{
        'angle (deg)':60,
        'spatial-freq (cycle/deg)':0.05,
        'contrast (norm.)':1.,
        # range
        'spatial-freq-1':0.001, 'spatial-freq-2':2., 'N-spatial-freq':2,
        'angle-1':0., 'angle-2':180, 'N-angle':0,
        'contrast-1':0.2, 'contrast-2':1., 'N-contrast':0},
    
    # center grating
    'center-grating':{
        'angle (deg)':60, 'spatial-freq (cycle/deg)':0.05,
        'radius (deg)':5, 'x-center (deg)':0, 'y-center (deg)':0,
        'contrast (norm.)':1.,
        'bg-color (lum.)':0., # not thought to be varied
        # range
        'angle-1':0, 'angle-2':150., 'N-angle':0,
        'spatial-freq-1':0.001, 'spatial-freq-2':2., 'N-spatial-freq':2,
        'radius-1':0, 'radius-2':150., 'N-radius':0,
        'x-center-1':-50, 'x-center-2':50, 'N-x-center':0,
        'y-center-1':-40., 'y-center-2':40., 'N-y-center':0,
        'contrast-1':0.2, 'contrast-2':1., 'N-contrast':0,
        'bg-color-1':-1., 'bg-color-2':1., 'N-bg-color':0},

    # off-center grating
    'off-center-grating':{
        'angle (deg)':60, 'spatial-freq (cycle/deg)':0.05,
        'radius (deg)':5, 'x-center (deg)':0, 'y-center (deg)':0,
        'contrast (norm.)':1.,
        'bg-color (lum.)':0., # not thought to be varied
        # range
        'angle-1':0, 'angle-2':150., 'N-angle':0,
        'spatial-freq-1':0.001, 'spatial-freq-2':2., 'N-spatial-freq':2,
        'radius-1':0, 'radius-2':150., 'N-radius':0,
        'x-center-1':-50, 'x-center-2':50, 'N-x-center':0,
        'y-center-1':-40., 'y-center-2':40., 'N-y-center':0,
        'contrast-1':0.2, 'contrast-2':1., 'N-contrast':0,
        'bg-color-1':-1., 'bg-color-2':1., 'N-bg-color':0},

    # surround grating
    'surround-grating':{
        'angle (deg)':60, 'spatial-freq (cycle/deg)':0.05,
        'radius-start (deg)':4, 'radius-end (deg)':8,
        'x-center (deg)':0, 'y-center (deg)':0,
        'contrast (norm.)':1.,
        'bg-color (lum.)':0., # not thought to be varied
        # range
        'angle-1':0, 'angle-2':150., 'N-angle':0,
        'spatial-freq-1':0.001, 'spatial-freq-2':2., 'N-spatial-freq':2,
        'radius-start-1':2., 'radius-start-2':120, 'N-radius-start':0,
        'radius-end-1':0., 'radius-end-2':20., 'N-radius-end':0,
        'x-center-1':-50, 'x-center-2':50, 'N-x-center':0,
        'y-center-1':-40., 'y-center-2':40., 'N-y-center':0,
        'contrast-1':0.2, 'contrast-2':1., 'N-contrast':0,
        'bg-color-1':-1., 'bg-color-2':1., 'N-bg-color':0},
    
    # full-field drifting grating
    'drifting-full-field-grating':{
        'angle (deg)':60,
        'spatial-freq (cycle/deg)':0.05,
        'speed (cycle/s)':2.,
        'contrast (norm.)':1.,
        # range
        'spatial-freq-1':0.001, 'spatial-freq-2':2., 'N-spatial-freq':2,
        'angle-1':0., 'angle-2':180, 'N-angle':0,
        'speed-1':0.1, 'speed-2':50, 'N-speed':5,
        'contrast-1':0.2, 'contrast-2':1., 'N-contrast':0},
    
    # center drifting grating
    'drifting-center-grating':{
        'angle (deg)':60, 'spatial-freq (cycle/deg)':0.05,
        'radius (deg)':5, 'x-center (deg)':0, 'y-center (deg)':0,
        'speed (cycle/s)':2.,
        'contrast (norm.)':1.,
        'bg-color (lum.)':0., # not thought to be varied
        # range
        'angle-1':0, 'angle-2':150., 'N-angle':0,
        'spatial-freq-1':0.001, 'spatial-freq-2':2., 'N-spatial-freq':2,
        'speed-1':0.1, 'speed-2':50, 'N-speed':5,
        'radius-1':0, 'radius-2':150., 'N-radius':0,
        'x-center-1':-50, 'x-center-2':50, 'N-x-center':0,
        'y-center-1':-40., 'y-center-2':40., 'N-y-center':0,
        'contrast-1':0.2, 'contrast-2':1., 'N-contrast':0,
        'bg-color-1':-1., 'bg-color-2':1., 'N-bg-color':0},
    
    # off-center grating
    'drifting-off-center-grating':{
        'angle (deg)':60, 'spatial-freq (cycle/deg)':0.05,
        'radius (deg)':5, 'x-center (deg)':0, 'y-center (deg)':0,
        'speed (cycle/s)':2.,
        'contrast (norm.)':1.,
        'bg-color (lum.)':0., # not thought to be varied
        # range
        'angle-1':0, 'angle-2':150., 'N-angle':0,
        'spatial-freq-1':0.001, 'spatial-freq-2':2., 'N-spatial-freq':2,
        'radius-1':0, 'radius-2':150., 'N-radius':0,
        'speed-1':0.1, 'speed-2':50, 'N-speed':5,
        'x-center-1':-50, 'x-center-2':50, 'N-x-center':0,
        'y-center-1':-40., 'y-center-2':40., 'N-y-center':0,
        'contrast-1':0.2, 'contrast-2':1., 'N-contrast':0,
        'bg-color-1':-1., 'bg-color-2':1., 'N-bg-color':0},

    # surround drifting grating
    'drifting-surround-grating':{
        'angle (deg)':60, 'spatial-freq (cycle/deg)':0.05,
        'radius-start (deg)':4, 'radius-end (deg)':8,
        'x-center (deg)':0, 'y-center (deg)':0,
        'speed (cycle/s)':2.,
        'contrast (norm.)':1.,
        'bg-color (lum.)':0., # not thought to be varied
        # range
        'angle-1':0, 'angle-2':150., 'N-angle':0,
        'spatial-freq-1':0.001, 'spatial-freq-2':2., 'N-spatial-freq':2,
        'radius-start-1':2., 'radius-start-2':120, 'N-radius-start':0,
        'radius-end-1':0., 'radius-end-2':20., 'N-radius-end':0,
        'speed-1':0.1, 'speed-2':50, 'N-speed':5,
        'x-center-1':-50, 'x-center-2':50, 'N-x-center':0,
        'y-center-1':-40., 'y-center-2':40., 'N-y-center':0,
        'contrast-1':0.2, 'contrast-2':1., 'N-contrast':0,
        'bg-color-1':-1., 'bg-color-2':1., 'N-bg-color':0},
    
    'center-surround-grating':{},
    
    # gaussian blobs
    'gaussian-blobs':{
        'radius (deg)':5, 'x-center (deg)':0, 'y-center (deg)':0,
        'center-time (s)': 2.,
        'extent-time (s)': 1.,
        'contrast (norm.)':1.,
        'bg-color (lum.)':-1., # not thought to be varied
        # range
        'center-time-1':0., 'center-time-2':15., 'N-center-time':0,
        'extent-time-1':0., 'extent-time-2':15., 'N-extent-time':0,
        'radius-1':0, 'radius-2':150., 'N-radius':0,
        'x-center-1':-50, 'x-center-2':50, 'N-x-center':0,
        'y-center-1':-40., 'y-center-2':40., 'N-y-center':0,
        'contrast-1':0.2, 'contrast-2':1., 'N-contrast':0,
        'bg-color-1':-1., 'bg-color-2':1., 'N-bg-color':0},

    # NI
    'Natural-Image':{
        'Image-ID (#)':1,
        'Image-ID-1':1,'Image-ID-2':5,'N-Image-ID':5},

    'Natural-Image+VSE':{
        'Image-ID (#)':1,
        'VSE-seed (#)':1,
        'saccade-amplitude (deg)':1.,
        'mean-saccade-duration (s)':3.,
        'std-saccade-duration (s)':0.5,
        'vary-VSE-with-Image (0/1)':1,
        'saccade-amplitude-1':0.001, 'saccade-amplitude-2':10., 'N-saccade-amplitude':0,
        'vary-VSE-with-Image-1':0,'vary-VSE-with-Image-2':1,'N-vary-VSE-with-Image':0,
        'mean-saccade-duration-1':0.01,'mean-saccade-duration-2':100.,'N-mean-saccade-duration':0,
        'std-saccade-duration-1':0.01,'std-saccade-duration-2':100.,'N-std-saccade-duration':0,
        'Image-ID-1':1,'Image-ID-2':5,'N-Image-ID':5,
        'VSE-seed-1':1,'VSE-seed-2':5,'N-VSE-seed':1},
    
    'sparse-noise':{
        'square-size (deg)':2., # in degrees
        'sparseness (%)':10,
        'mean-refresh-time (s)':2.,
        'jitter-refresh-time (s)':0.5,
        'noise-seed (#)':1,
        'contrast (norm.)':1.,
        'bg-color (lum.)':0., # not thought to be varied
        'square-size-1':0.2,'square-size-2':9,'N-square-size':3,
        'sparseness-1':1,'sparseness-2':50,'N-sparseness':0,
        'mean-refresh-time-1':0.01,'mean-refresh-time-2':10.,'N-mean-refresh-time':0,
        'jitter-refresh-time-1':0.01,'jitter-refresh-time-2':5.,'N-jitter-refresh-time':0,
        'noise-seed-1':1, 'noise-seed-2':1000, 'N-noise-seed':10,
        'contrast-1':0., 'contrast-2':1., 'N-contrast':0,
        'bg-color-1':-1., 'bg-color-2':1., 'N-bg-color':0,
    },
    
    'dense-noise':{
        'square-size (deg)':2., # in degrees
        'mean-refresh-time (s)':2.,
        'jitter-refresh-time (s)':0.5,
        'noise-seed (#)':1,
        'contrast (norm.)':1.,
        'square-size-1':0.2,'square-size-2':9,'N-square-size':3,
        'mean-refresh-time-1':0.01,'mean-refresh-time-2':10.,'N-mean-refresh-time':0,
        'jitter-refresh-time-1':0.01,'jitter-refresh-time-2':5.,'N-jitter-refresh-time':0,
        'noise-seed-1':1, 'noise-seed-2':1000, 'N-noise-seed':10,
        'contrast-1':0., 'contrast-2':1., 'N-contrast':0,
    },
    # 'full-field-grating+VSE':{},
}
