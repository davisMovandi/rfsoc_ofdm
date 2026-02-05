from pynq import DefaultIP
import numpy as np
from .quick_widgets import DropDown, UserInput

switcher = {'BPSK'     : 0,
            'QPSK'     : 1,
            '8-PSK'    : 2,
            '16-QAM'   : 3,
            '32-QAM'   : 4,
            '64-QAM'   : 5,
            '128-QAM'  : 6,
            '256-QAM'  : 7,
            '512-QAM'  : 8,
            '1024-QAM' : 9}

evm_switcher = {'QPSK'    : 0,
                '64-QAM'  : 1}

enabler = {'Disable' : 0,
           'Enable'  : 1}

class EVMCore(DefaultIP):
    """Driver for EVM calculation core logic IP
    """
    
    def __init__(self,description):

        def _callback_modulation(value):
            self.modulation = value

        def _callback_rms_n(value):
            self.rms_n = value

        super().__init__(description=description)

        self.modulation_dropdown = DropDown(callback=_callback_modulation,
                                            options=list(evm_switcher.keys()),
                                            value='QPSK',
                                            description='Modulation Scheme: ')
        
        self.rms_n_ui = UserInput(callback=_callback_rms_n,
                                      value=2048,
                                      min=128,
                                      max=4096,
                                      step=128,
                                      description='RMS N: ')
        
    bindto = ["xilinx.com:ip:evm_calc_ip:1.9"]
    
    @property
    def reset(self):
        return self.read(0x0)
        
    @reset.setter
    def reset(self, reset):
        self.write(0x0, reset)
        
    @property
    def enable(self):
        return self.read(0x104)
        
    @enable.setter
    def enable(self, enable):
        self.write(0x104, enable)
        
    @property
    def modulation(self):
        global evm_switcher
        scheme = self.read(0x104)
        return list(evm_switcher.keys())[scheme]
        
    @modulation.setter
    def modulation(self, modulation):
        global evm_switcher
        scheme = evm_switcher.get(modulation)
        self.write(0x104, scheme)
    
    @property
    def threshold(self):
        return self.read(0x100)
        
    @threshold.setter
    def threshold(self, threshold):
        thresh = (int(threshold*2**15))
        self.write(0x100, thresh)

    @property
    def rms_n(self):
        return self.read(0x108)
        
    @rms_n.setter
    def rms_n(self, rms_n):
        n = (int(rms_n))
        self.write(0x108, n)

    @property
    def rms_enable(self):
        return self.read(0x10C)
        
    @rms_enable.setter
    def rms_enable(self, enable):
        self.write(0x10C, enable)

class OFDMTxCore(DefaultIP):
    """Driver for Transmitter core logic IP
    """
    
    def __init__(self,description):
        
        def _callback_modulation(value):
            self.modulation = value

        def _callback_tone1_freq_MHz(value):
            self.tone1_freq_mHz = value

        def _callback_tone1_gain(value):
            self.tone1_gain = value

        def _callback_tone1_enable(value):
            self.tone1_enable = value

        def _callback_tone2_freq_MHz(value):
            self.tone2_freq_mHz = value

        def _callback_tone2_gain(value):
            self.tone2_gain = value

        def _callback_tone2_enable(value):
            self.tone2_enable = value

        super().__init__(description=description)
        
        self.modulation_dropdown = DropDown(callback=_callback_modulation,
                                            options=list(switcher.keys()),
                                            value='BPSK',
                                            description='Modulation Scheme: ')

        self.tone1_freq_ui = UserInput(callback=_callback_tone1_freq_MHz,
                                      value=10,
                                      description='Freq (MHz): ')
        
        self.tone1_gain_ui = UserInput(callback=_callback_tone1_gain,
                                      value=-10,
                                      min=-60,
                                      max=0,
                                      step=0.5,
                                      description='Backoff (dB): ')

        self.tone1_enable_dropdown = DropDown(callback=_callback_tone1_enable,
                                            options=list(enabler.keys()),
                                            value='Disable',
                                            description='Tone 1 Enable: ')

        self.tone2_freq_ui = UserInput(callback=_callback_tone2_freq_MHz,
                                      value=5,
                                      description='Freq (MHz): ')

        self.tone2_gain_ui = UserInput(callback=_callback_tone2_gain,
                                      value=0,
                                      min=-60,
                                      max=0,
                                      step=0.5,
                                      description='Backoff (dB): ')

        self.tone2_enable_dropdown = DropDown(callback=_callback_tone2_enable,
                                            options=list(enabler.keys()),
                                            value='Disable',
                                            description='Tone 2 Enable: ')

    bindto = ["xilinx.com:ip:ofdm_tx:0.4"]
    
    @property
    def reset(self):
        return self.read(0x0)
        
    @reset.setter
    def reset(self, reset):
        self.write(0x0, reset)
        
    @property
    def modulation(self):
        global switcher
        scheme = self.read(0x100)
        return list(switcher.keys())[scheme]
        
    @modulation.setter
    def modulation(self, modulation):
        global switcher
        scheme = switcher.get(modulation)
        self.write(0x100, scheme)

    @property
    def tone1_freq_mHz(self):
        return self.read(0x10C)

    @tone1_freq_mHz.setter
    def tone1_freq_mHz(self, tone1_freq_mHz):
        self.write(0x10C, int(tone1_freq_mHz*2**8))

    @property
    def tone2_freq_mHz(self):
        return self.read(0x110)

    @tone2_freq_mHz.setter
    def tone2_freq_mHz(self, tone2_freq_mHz):
        self.write(0x110, int(tone2_freq_mHz*2**8))

    @property
    def tone1_enable(self):
        global enabler
        scheme = self.read(0x114)
        return list(enabler.keys())[scheme]
        
    @tone1_enable.setter
    def tone1_enable(self, tone1_enable):
        global enabler
        scheme = enabler.get(tone1_enable)
        self.write(0x114, scheme)

    @property
    def tone2_enable(self):
        global enabler
        scheme = self.read(0x118)
        return list(enabler.keys())[scheme]
        
    @tone2_enable.setter
    def tone2_enable(self, tone2_enable):
        global enabler
        scheme = enabler.get(tone2_enable)
        self.write(0x118, scheme)

    @property
    def tone1_gain(self):
        scaled_gain = self.read(0x11C)
        gain = 20*np.log10(scaled_gain/(2**14))
        return gain
        
    @tone1_gain.setter
    def tone1_gain(self, tone1_gain):
        tone1_gain = float(tone1_gain)
        tone1_gain = min(max(tone1_gain, -60), 0)
        scaled_gain = int((round(10**(tone1_gain/20) * (2**14))))
        self.write(0x11C, scaled_gain)

    @property
    def tone2_gain(self):
        scaled_gain = self.read(0x120)
        gain = 20*np.log10(scaled_gain/(2**14))
        return gain
        
    @tone2_gain.setter
    def tone2_gain(self, tone2_gain):
        tone2_gain = float(tone2_gain)
        tone2_gain = min(max(tone2_gain, -60), 0)
        scaled_gain = int((round(10**(tone2_gain/20) * (2**14))))
        self.write(0x120, scaled_gain)

    @property
    def transmit_enable(self):
        return self.read(0x104)
        
    @transmit_enable.setter
    def transmit_enable(self, transmit_enable):
        self.write(0x104, transmit_enable)
        
    @property
    def gain(self):
        scaled_gain = self.read(0x108)
        gain = scaled_gain/(2**30)
        return gain
        
    @gain.setter
    def gain(self, gain):
        scaled_gain = int(gain*2**30)
        self.write(0x108, scaled_gain)

class OFDMRxCore(DefaultIP):
    """Driver for Receiver core logic IP
    """
    
    def __init__(self,description):
        super().__init__(description=description)
        
    bindto = ["xilinx.com:ip:ofdm_rx:0.4"]
    
    @property
    def reset(self):
        return self.read(0x0)
        
    @reset.setter
    def reset(self, reset):
        self.write(0x0, reset)
        
    @property
    def receive_enable(self):
        return self.read(0x0)
        
    @receive_enable.setter
    def receive_enable(self, enable):
        self.write(0x0, enable)
