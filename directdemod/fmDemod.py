'''
FM demodulation
'''

import numpy as np
import scipy.signal as signal

'''
Object for FM demodulation
'''

class fmDemod():

    '''
    Object for FM demodulation
    '''

    def __init__(self, storeState = True):

        '''Initialize the object

        Args:
            storeState (:obj:`bool`): Store state? Helps if signal is chunked
        '''

        self.__storeState = storeState
        self.__last = None

    def demod(self, sig):

        '''FM demod a given complex IQ array

        Args:
            sig (:obj:`numpy array`): numpy array with IQ in complex form

        Returns:
            :obj:`numpy array`: FM demodulated array
        '''

        sig_fmd = sig[1:] * np.conj(sig[:-1])

        if self.__storeState:
            if self.__last is None:
                self.__last = sig[-1]
                return np.angle(sig_fmd)
            else:
                addCorrection = np.array([sig[0] * np.conj(self.__last)])
                self.__last = sig[-1]
                return np.angle(np.concatenate([addCorrection, sig_fmd]))
        else:
            return np.angle(sig_fmd)