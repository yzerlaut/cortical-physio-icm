import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
from scipy.interpolate import interp1d

def resample_signal(original_signal,
                    original_freq=1e4,
                    t_sample=None,
                    new_freq=1e3,
                    pre_smoothing=0,
                    post_smoothing=0,
                    tlim=None,
                    verbose=False):

    if verbose:
        print('resampling signal [...]')
        

    if (pre_smoothing*original_freq)>1:
        if verbose:
            print(' - gaussian smoothing - pre')
        signal = gaussian_filter1d(original_signal, int(pre_smoothing*original_freq), mode='nearest')
    else:
        signal = original_signal
        
    if t_sample is None:
       t_sample = np.arange(len(signal))/original_freq
       
    if verbose:
        print(' - signal interpolation')

    func = interp1d(t_sample[np.isfinite(signal)], signal[np.isfinite(signal)],
                    fill_value='extrapolate')
    if tlim is None:
        tlim = [t_sample[0], t_sample[-1]]
    new_t = np.arange(int((tlim[1]-tlim[0])*new_freq))/new_freq+tlim[0]
    new_signal = func(new_t)

    if (post_smoothing*new_freq)>1:
        if verbose:
            print(' - gaussian smoothing - post')
        new_signal = gaussian_filter1d(new_signal, int(post_smoothing*new_freq), mode='nearest')
        
    return new_t, new_signal


def autocorrel(Signal, tmax, dt):
    """
    argument : Signal (np.array), tmax and dt (float)
    tmax, is the maximum length of the autocorrelation that we want to see
    returns : autocorrel (np.array), time_shift (np.array)
    take a Signal of time sampling dt, and returns its autocorrelation
     function between [0,tstop] (normalized) !!
    """
    steps = int(tmax/dt) # number of steps to sum on
    Signal2 = (Signal-Signal.mean())/Signal.std()
    cr = np.correlate(Signal2[steps:],Signal2)/steps
    time_shift = np.arange(len(cr))*dt
    return cr/cr.max(), time_shift

def crosscorrel(Signal1, Signal2, tmax, dt):
    """
    argument : Signal1 (np.array()), Signal2 (np.array())
    returns : np.array()
    take two Signals, and returns their crosscorrelation function 

    CONVENTION:
    --------------------------------------------------------------
    when the peak is in the past (negative t_shift)
    it means that Signal2 is delayed with respect to Signal 1
    --------------------------------------------------------------
    """
    if len(Signal1)!=len(Signal2):
        print('Need two arrays of the same size !!')
        
    steps = int(tmax/dt) # number of steps to sum on
    time_shift = dt*np.concatenate([-np.arange(1, steps)[::-1], np.arange(steps)])
    CCF = np.zeros(len(time_shift))
    for i in np.arange(steps):
        ccf = np.corrcoef(Signal1[:len(Signal1)-i], Signal2[i:])
        CCF[steps-1+i] = ccf[0,1]
    for i in np.arange(steps):
        ccf = np.corrcoef(Signal2[:len(Signal1)-i], Signal1[i:])
        CCF[steps-1-i] = ccf[0,1]
    return CCF, time_shift

def autocorrel_on_NWB_quantity(Q1=None,
                               t_q1=None,
                               q1=None,
                               tmax=1,
                               Npoints=300):
    """
    Q1 can be replaced by an explicit signal with time sampling
    """

    # Q1 signal
    if (t_q1 is not None) and (q1 is not None):
        print(q1[:])
    elif Q1.timestamps is not None:
        t_q1 = Q1.timestamps[:]
        q1 =Q1.data[:]
    elif hasattr(Q1, 'rate'):
        t_q1 = Q1.starting_time+np.arange(Q1.num_samples)/Q1.rate
        q1 =Q1.data[:]
    else:
        print('second signal not recognized')
        q1=None
        

    if (q1 is not None):
        sampling_freq = Npoints/tmax
        tlim = [t_q1[0]-1./sampling_freq,
                t_q1[-1]+1./sampling_freq]

        new_t_q1, new_q1 = resample_signal(q1,
                                           t_sample=t_q1,
                                           new_freq=sampling_freq,
                                           tlim=tlim)

        # import matplotlib.pyplot as plt
        # plt.figure()
        # plt.plot(t_q1[-1000:], q1[-1000:])
        # plt.plot(new_t_q1[-1000:], new_q1[-1000:])
        # plt.show()
        
        return autocorrel(new_q1, tmax, 1./sampling_freq)
    else:
        return [0], [0]


def crosscorrel_on_NWB_quantity(Q1=None, Q2=None, tmax=1,
                                t_q1=None,
                                q1=None,
                                t_q2=None,
                                q2=None,
                                Npoints=300):
    """
    Q1 has to be a NWB signal
    Q2 can be replaced by an explicit signal with time sampling
    """

    # Q1 signal
    if (t_q1 is not None) and (q1 is not None):
        pass
    elif hasattr(Q1, 'timestamps') and (Q1.timestamps is not None):
        t_q1 = Q1.timestamps[:]
        q1 =Q1.data[:]
    elif hasattr(Q1, 'rate'):
        t_q1 = Q1.starting_time+np.arange(Q1.num_samples)/Q1.rate
        q1 =Q1.data[:]
    else:
        print('first signal not recognized')
        q1=None

    # Q2 signal
    if (t_q2 is not None) and (q2 is not None):
        pass
    elif hasattr(Q2, 'timestamps') and (Q2.timestamps is not None):
        t_q2 = Q2.timestamps[:]
        q2 =Q2.data[:]
    elif hasattr(Q2, 'rate'):
        t_q2 = Q2.starting_time+np.arange(Q2.num_samples)/Q2.rate
        q2 =Q2.data[:]
    else:
        print('second signal not recognized')
        q2=None


    if (q2 is not None) and (q1 is not None):
        sampling_freq = Npoints/tmax
        tlim = [np.min([t_q1[0], t_q2[0]])-1./sampling_freq,
                np.max([t_q1[-1], t_q2[-1]])+1./sampling_freq]

        new_t_q1, new_q1 = resample_signal(q1,
                                           t_sample=t_q1,
                                           new_freq=sampling_freq,
                                           tlim=tlim)
        new_t_q2, new_q2 = resample_signal(q2,
                                           t_sample=t_q2,
                                           new_freq=sampling_freq,
                                           tlim=tlim)
        # FOR DEBUGGING
        # import matplotlib.pyplot as plt
        # plt.figure()
        # plt.plot(t_q1[:1000], q1[:1000])
        # plt.plot(new_t_q1[:1000], new_q1[:1000])
        # plt.show()
        # plt.figure()
        # plt.plot(t_q2[:1000], q2[:1000])
        # plt.plot(new_t_q2[:1000], new_q2[:1000])
        # plt.show()
        return crosscorrel(new_q1, new_q2, tmax, 1./sampling_freq)
    else:
        return [0], [0]


def crosshistogram_on_NWB_quantity(Q1=None, Q2=None,
                                   t_q1=None,
                                   q1=None,
                                   t_q2=None,
                                   q2=None,
                                   Npoints=30,
                                   Nmin=20):

    # Q1 signal
    if (t_q1 is not None) and (q1 is not None):
        pass
    elif hasattr(Q1, 'timestamps') and (Q1.timestamps is not None):
        t_q1 = Q1.timestamps[:]
        q1 =Q1.data[:]
    elif hasattr(Q1, 'rate'):
        t_q1 = Q1.starting_time+np.arange(Q1.num_samples)/Q1.rate
        q1 =Q1.data[:]
    else:
        print('first signal not recognized')
        q1=None

    # Q2 signal
    if (t_q2 is not None) and (q2 is not None):
        pass
    elif hasattr(Q2, 'timestamps') and (Q2.timestamps is not None):
        t_q2 = Q2.timestamps[:]
        q2 =Q2.data[:]
    elif hasattr(Q2, 'rate'):
        t_q2 = Q2.starting_time+np.arange(Q2.num_samples)/Q2.rate
        q2 =Q2.data[:]
    else:
        print('second signal not recognized')
        q2=None

    mean_q1, var_q1 = [], []
    mean_q2, var_q2 = [], []
    
    if (q2 is not None) and (q1 is not None):
        func=interp1d(t_q2, q2, fill_value='extrapolate')
        new_q2 = func(t_q1)

        BINS=np.linspace(q1[np.isfinite(q1)].min(),
                         q1[np.isfinite(q1)].max(),
                         Npoints)
        bins = np.digitize(q1, bins=BINS)

        mean_q1, var_q1 = [], []
        mean_q2, var_q2 = [], []
        for i, b in enumerate(np.unique(bins)):
            cond = (bins==b)
            if np.sum(cond)>Nmin:
                mean_q1.append(q1[cond].mean())
                var_q1.append(q1[cond].std())
                mean_q2.append(new_q2[cond].mean())
                var_q2.append(new_q2[cond].std())

    return mean_q1, var_q1, mean_q2, var_q2
    
if __name__=='__main__':


    """
    some common tools for analysis
    """

    import matplotlib.pylab as plt
    import sys, os, pathlib
    sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
    from analysis.read_NWB import Data

    filename = sys.argv[-1]

    data = Data(filename)

    # CCF, tshift = crosscorrel_on_NWB_quantity(data.nwbfile.acquisition['Running-Speed'],
    #                                           data.nwbfile.acquisition['Running-Speed'],
    #                                           # t_q2=data.Fluorescence.timestamps[:],
    #                                           # q2=data.Fluorescence.data[data.iscell[0],:],
    #                                           tmax=100)
    # CCF, tshift = crosscorrel_on_NWB_quantity(t_q1=data.Fluorescence.timestamps[:],
    #                                           q1=data.Fluorescence.data[data.iscell[0],:],
    #                                           t_q2=data.Fluorescence.timestamps[:],
    #                                           q2=data.Fluorescence.data[data.iscell[0],:],
    #                                           tmax=20)
    CCF, tshift = autocorrel_on_NWB_quantity(t_q1=data.Fluorescence.timestamps[:],
                                             q1=data.Fluorescence.data[data.iscell[0],:],
                                             tmax=1000)
    plt.plot(tshift, CCF)
    plt.show()








