import os, sys, itertools, pathlib
import numpy as np
from scipy import stats

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from analysis.read_NWB import read as read_NWB, Data
from analysis.trial_averaging import build_episodes

class CellResponse:
    
    def __init__(self, data,
                 protocol_id=0,
                 quantity='CaImaging', 
                 subquantity='dF/F', 
                 roiIndex = 0,
                 prestim_duration=None,
                 verbose=False):
        
        """ build the episodes corresponding to a specific protocol and a ROIR"""
        for key in data.__dict__.keys():
            setattr(self, key, getattr(data, key))
        if verbose:
            print('Building episodes for "%s"' % self.protocols[protocol_id])
            
        data.CaImaging_key, data.roiIndices = subquantity, [roiIndex]
        self.EPISODES = build_episodes(data, protocol_id=protocol_id, quantity=quantity,
                                       prestim_duration=prestim_duration, verbose=verbose)
        self.varied_parameters = data.varied_parameters
        self.metadata = data.metadata

    def find_cond(self, key, index):
        if (type(key) in [list, np.ndarray]) and (type(index) in [list, np.ndarray]) :
            cond = (self.EPISODES[key[0]]==self.varied_parameters[key[0]][index[0]])
            for n in range(1, len(key)):
                cond = cond & (self.EPISODES[key[n]]==self.varied_parameters[key[n]][index[n]])
        else:
            cond = (self.EPISODES[key]==self.varied_parameters[key][index])
        return cond


    def compute_responsiveness(self,
                               threshold=1e-3,
                               interval_pre=[-2,0],
                               interval_post=[1,3]):

        KEYS = [key for key in self.varied_parameters if key!='repeat']
        OUTPUT = {'responsive':[], 'mean_pre':[], 'mean_post':[]}
        for k in KEYS:
            OUTPUT[k] = []

        for V in itertools.product(*[range(len(vals)) for (k,vals) in self.varied_parameters.items() if k!='repeat']):
            cond = np.ones(self.EPISODES['resp'].shape[0], dtype=bool)
            for key, iv in zip(KEYS, V):
                cond = cond & self.find_cond(key, iv)
                OUTPUT[key].append(self.varied_parameters[key][iv])
                
            test = stat_test_for_evoked_responses(self.EPISODES, cond,
                                                  interval_pre=interval_pre,
                                                  interval_post=interval_post,
                                                  test='wilcoxon')

            if test.pvalue<=threshold:
                OUTPUT['responsive'].append(True)
            else:
                OUTPUT['responsive'].append(False)

            pre_cond = (self.EPISODES['t']>=interval_pre[0]) & (self.EPISODES['t']<=interval_pre[1])
            post_cond = (self.EPISODES['t']>=interval_post[0]) & (self.EPISODES['t']<=interval_post[1])

            OUTPUT['mean_pre'].append(self.EPISODES['resp'][cond,:][:,pre_cond].mean())
            OUTPUT['mean_post'].append(self.EPISODES['resp'][cond,:][:,post_cond].mean())

        return OUTPUT


    def get_average(self, condition=None):

        if condition is None:
            return self.EPISODES['resp'].mean(axis=1)
        else:
            return self.EPISODES['resp'][condition,:].mean(axis=0)

    
    
    
def stat_test_for_evoked_responses(EPISODES, episode_cond,
                                   interval_pre=[-2,0],
                                   interval_post=[1,3],
                                   test='wilcoxon'):


    pre_cond = (EPISODES['t']>=interval_pre[0]) & (EPISODES['t']<=interval_pre[1])
    post_cond = (EPISODES['t']>=interval_post[0]) & (EPISODES['t']<=interval_post[1])
    
    if test=='wilcoxon':
        return stats.wilcoxon(EPISODES['resp'][episode_cond,:][:,pre_cond].mean(axis=1),
                              EPISODES['resp'][episode_cond,:][:,post_cond].mean(axis=1))
    else:
        print(' "%s" test not implemented ! ' % test)

    return test

def pval_to_star(test, pvalue=1e-5, size=5):

    
    if test.pvalue<1e-3:
        return '***', size+1
    elif test.pvalue<1e-2:
        return '**', size+1
    elif test.pvalue<0.05:
        return '*', size+1
    else:
        return 'n.s.', size

        
if __name__=='__main__':


    # filename = os.path.join(os.path.expanduser('~'), 'DATA', 'CaImaging', 'Wild_Type_GCamp6f', '2021_03_23-11-26-36.nwb')
    filename = sys.argv[-1]
    
    FullData= Data(filename)
    
    print(FullData.protocols)
    print('the datafile has %i validated ROIs (over %i from the full suite2p output) ' % (np.sum(FullData.iscell),
                                                                                          len(FullData.iscell)))
    
    for ip, protocol in enumerate(FullData.protocols):
        for roi in range(4):
            cell = CellResponse(FullData,
                                protocol_id=ip,
                                quantity='CaImaging', 
                                subquantity='dF/F', 
                                roiIndex = roi,
                                verbose=False)
            print(cell.compute_responsiveness())
                
            # OUTPUT = {}
            # for key, val in zip(KEYS, VALUES):
            #     OUTPUT[key] = val.flatten()
            # OUTPUT['responsive'] = np.zeros(len(val.flatten()), dtype=bool)
            # print(OUTPUT)
            

    # # # for i in [2, 6, 9, 10, 13, 15, 16, 17, 21, 38, 41, 136]: # for 2021_03_11-17-13-03.nwb
    # for i in range(np.sum(FullData.iscell))[:1]:
    #     fig, responsive = orientation_size_selectivity_analysis(FullData, roiIndex=i)
    #     if responsive:
    #         print('cell %i -> responsive !' % (i+1))
    #     plt.show()








    
