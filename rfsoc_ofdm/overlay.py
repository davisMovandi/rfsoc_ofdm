from pynq import Overlay
import ipywidgets as ipw
import signal
import os
import xrfdc
import xrfclk

# Import overlay specific drivers
from rfsoc_ofdm import inspector
from rfsoc_ofdm import ofdm
from rfsoc_ofdm import clocks

class Overlay(Overlay):
    """
    """
    
    def __init__(self, bitfile_name=None, clks=None, init_rf_clks=True, **kwargs):
        """
        """

        # Generate default bitfile name
        if bitfile_name is None:
            this_dir = os.path.dirname(__file__)
            print("i got to here...")
            bitfile_name = os.path.join(this_dir, 'rfsoc_ofdm', 'bitstream', 'rfsoc_ofdm.bit')
            hwhfile_name  = os.path.join(this_dir, 'rfsoc_ofdm', 'bitstream', 'rfsoc_ofdm.hwh')
        print(bitfile_name)
        # Create Overlay
        super().__init__(bitfile_name,  ignore_version=True, **kwargs)

        # Determine board and set PLL appropriately
        board = os.environ['BOARD']

        # Extract friendly dataconverter names
        if board == 'RFSoC4x2':
            self.dac_tile = self.rfdc.dac_tiles[2]
            self.dac_block = self.dac_tile.blocks[0]
            self.adc_tile = self.rfdc.adc_tiles[2]
            self.adc_block = self.adc_tile.blocks[1]
        elif board in ['ZCU208', 'ZCU216']:
            self.dac_tile = self.rfdc.dac_tiles[2]
            self.dac_block = self.dac_tile.blocks[0]
            self.adc_tile = self.rfdc.adc_tiles[1]
            self.adc_block = self.adc_tile.blocks[0]
        elif board == 'RFSoC2x2':
            self.dac_tile = self.rfdc.dac_tiles[1]
            self.dac_block = self.dac_tile.blocks[0]
            self.adc_tile = self.rfdc.adc_tiles[2]
            self.adc_block = self.adc_tile.blocks[0]
        elif board == 'ZCU111':
            self.dac_tile = self.rfdc.dac_tiles[1]
            self.dac_block = self.dac_tile.blocks[2]
            self.adc_tile = self.rfdc.adc_tiles[0]
            self.adc_block = self.adc_tile.blocks[0]
        else:
            raise RuntimeError('Unknown error occurred.') # shouldn't get here
        
        # Start up LMX clock
        if init_rf_clks:
            clocks.set_custom_lmclks(clks)
        if board == 'ZCU216':
            fs = 1920.00
        else:
            fs =  3840.00 #
        if ((clks == None) or (clks == 384)):
            print("Configuring adc and dac to: pll_freq=384")
            self.configure_adcs()
            print("configure_adcs done")
            self.configure_dacs()
            print("configure_dacs done")
        elif clks == 491:
            print("Configuring adc and dac to: pll_freq=491.52")
            self.configure_adcs(pll_freq=245.76, sample_freq=4915.2, nyquist_zone=2, centre_freq=-4500)
            print("configure_adcs done")
            self.configure_dacs(pll_freq=245.76, sample_freq=5898.24, nyquist_zone=2, centre_freq=4500)
            print("configure_dacs done")
        elif clks == 409:
            print("Configuring adc and dac to: pll_freq=409.6")
            self.configure_adcs(pll_freq=409.6, sample_freq=4915.2, nyquist_zone=1, centre_freq=-800)
            print("configure_adcs done")
            self.configure_dacs(pll_freq=409.6, sample_freq=4915.2, nyquist_zone=1, centre_freq=800)
            print("configure_dacs done")
        print(dir(self))
        self.inspectors = {'transmitter' : self.InspectorTransmitter,
                           'receiver' : self.InspectorReceiver,
                           'constellation' : self.InspectorConstellation,
                           'evm' : self.InspectorEvm}
        # self.inspectors['constellation'].evm = True
        print("inspectors done")
        self.initialise_receiver()
        self.initialise_transmitter()
        self.initialise_evm()

        self.configure_inspectors()    
        self.start_constellation()


    def start_constellation(self):
        """
        """

        self.inspectors['constellation'].get_frame()#constellation=True)
        
        
    def configure_adcs(self, pll_freq=384.00, sample_freq=4800, nyquist_zone=1, centre_freq=-300):
        """
        """
        print("inside adcs")
        # print("pll freq = " + str(pll_freq))
        self.adc_tile.DynamicPLLConfig(1, pll_freq, sample_freq)
        self.adc_block.NyquistZone = nyquist_zone
        self.adc_block.MixerSettings = {
            'CoarseMixFreq'  : xrfdc.COARSE_MIX_BYPASS,
            'EventSource'    : xrfdc.EVNT_SRC_TILE,
            'FineMixerScale' : xrfdc.MIXER_SCALE_1P0,
            'Freq'           : centre_freq,
            'MixerMode'      : xrfdc.MIXER_MODE_R2C,
            'MixerType'      : xrfdc.MIXER_TYPE_FINE,
            'PhaseOffset'    : 0.0
        }
        self.adc_block.UpdateEvent(xrfdc.EVENT_MIXER)
        self.adc_tile.SetupFIFO(True)
        

    def configure_dacs(self, pll_freq=384.00, sample_freq=4800, nyquist_zone=2, centre_freq=4500):
        """
        """
        print("inside dacs")
        # print("pll freq = " + str(pll_freq))
        self.dac_tile.DynamicPLLConfig(1, pll_freq, sample_freq)
        # print("finsihed dynamicPLLConfig")
        self.dac_block.NyquistZone = nyquist_zone
        self.dac_block.InvSincFIR = 2
        print("InvSincFIR = ", str(self.dac_block.InvSincFIR))
        print("mixer mode c2r = ", str(xrfdc.MIXER_MODE_C2R))
        # print("finsihed nyquist zone")
        mix = self.dac_block.MixerSettings
        self.dac_block.MixerSettings = {
            'CoarseMixFreq'  : xrfdc.COARSE_MIX_BYPASS,
            'EventSource'    : xrfdc.EVNT_SRC_IMMEDIATE,
            'FineMixerScale' : xrfdc.MIXER_SCALE_1P0,
            'Freq'           : centre_freq,
            'MixerMode'      : xrfdc.MIXER_MODE_C2R,
            'MixerType'      : xrfdc.MIXER_TYPE_FINE,
            'PhaseOffset'    : 0.0
        }
        self.dac_block.UpdateEvent(1)
        self.dac_tile.SetupFIFO(True)
        
        
    def configure_inspectors(self, shape=(1024,)):
        """
        """
        
        for inspector in self.inspectors.values():
            inspector.set_shape(shape=shape)
        
        
    def initialise_transmitter(self, enable=1, gain=1):
        """
        """
        
        self.ofdm_transmitter.reset = 1
        self.ofdm_transmitter.gain = 2
        self.ofdm_transmitter.transmit_enable = enable
        
    
    def initialise_receiver(self, enable=1, modulation='QPSK'):
        """
        """
        
        self.ofdm_receiver.reset = 1
        self.ofdm_receiver.receive_enable = enable
        self.ofdm_transmitter.modulation = modulation
        
    def initialise_evm(self, modulation='QPSK', threshold=0.03, rms_n=2048, rms_enable=1):
        """
        """
        self.evm_calc_ip_0.modulation = modulation
        self.evm_calc_ip_0.threshold = threshold
        self.evm_calc_ip_0.rms_n = rms_n
        self.evm_calc_ip_0.rms_enable = rms_enable
        
    def ofdm_loopback_application(self):
        """
        """
        
        # Prepare children widgets for tab containers
        transmit_chtime = ipw.VBox([self.inspectors['transmitter'].time_plot(),
                                    ipw.HBox([self.ofdm_transmitter.tone1_freq_ui.get_widget(),
                                              self.ofdm_transmitter.tone1_gain_ui.get_widget(),
                                              self.ofdm_transmitter.tone1_enable_dropdown.get_widget()]),
                                    ipw.HBox([self.ofdm_transmitter.tone2_freq_ui.get_widget(),
                                              self.ofdm_transmitter.tone2_gain_ui.get_widget(),
                                              self.ofdm_transmitter.tone2_enable_dropdown.get_widget()]),
                                    ipw.HBox([self.inspectors['transmitter'].channel_widget.get_widget(),
                                              self.inspectors['transmitter'].plot_control()])])
        transmit_chfreq = ipw.VBox([self.inspectors['transmitter'].spectrum_plot(),
                                    ipw.HBox([self.inspectors['transmitter'].channel_widget.get_widget(),
                                              self.inspectors['transmitter'].plot_control()])])
        receive_chtime = ipw.VBox([self.inspectors['receiver'].time_plot(),
                                   ipw.HBox([self.inspectors['receiver'].channel_widget.get_widget(),
                                             self.inspectors['receiver'].plot_control()])])
        receive_chfreq = ipw.VBox([self.inspectors['receiver'].spectrum_plot(),
                                   ipw.HBox([self.ofdm_transmitter.tone1_freq_ui.get_widget(),
                                             self.ofdm_transmitter.tone1_gain_ui.get_widget(),
                                             self.ofdm_transmitter.tone1_enable_dropdown.get_widget()]),
                                   ipw.HBox([self.ofdm_transmitter.tone2_freq_ui.get_widget(),
                                             self.ofdm_transmitter.tone2_gain_ui.get_widget(),
                                             self.ofdm_transmitter.tone2_enable_dropdown.get_widget()]),
                                   ipw.HBox([self.inspectors['receiver'].channel_widget.get_widget(),
                                             self.inspectors['receiver'].plot_control()])])
        constellation_ch = ipw.VBox([self.inspectors['constellation'].constellation_plot(),
                                     ipw.HBox([self.ofdm_transmitter.modulation_dropdown.get_widget(),
                                            #    self.inspectors['constellation'].channel_widget.get_widget(),
                                               self.inspectors['constellation'].plot_control()])])
        evm_plot = ipw.VBox([self.inspectors['evm'].evm_plot(),
                                     ipw.HBox([self.inspectors['evm'].channel_widget.get_widget(),
                                               self.inspectors['evm'].plot_control()]),
                                     ipw.HBox([self.evm_calc_ip_0.rms_n_ui.get_widget(),
                                               self.evm_calc_ip_0.modulation_dropdown.get_widget()])])

        peak_data_display = ipw.VBox([self.inspectors['receiver'].peak_plot(),
                                     ipw.HBox([self.inspectors['receiver'].channel_widget.get_widget()]),
                                     ipw.HBox([self.inspectors['receiver']._p_plot.num_peaks_ui.get_widget()])])

        # Create tab for inspection plots
        tx_tab_ch = [transmit_chfreq, transmit_chtime]
        tx_insp_tab = ipw.Tab()
        tx_insp_tab.children = tx_tab_ch
        titles = ['Transmit Spectrum', 'Transmit Time']
        [tx_insp_tab.set_title(i, title) for i, title in enumerate(titles)]
        tx_insp_tab.selected_index = 0

        rx_tab_ch = [receive_chfreq, receive_chtime]
        rx_insp_tab = ipw.Tab()
        rx_insp_tab.children = rx_tab_ch
        titles = ['Receive Spectrum', 'Receive Time']
        [rx_insp_tab.set_title(i, title) for i, title in enumerate(titles)]
        rx_insp_tab.selected_index = 0

        # Create tab for demodulation inspection (constellation plot)
        iq_tab_ch = [constellation_ch, evm_plot]
        iq_tab = ipw.Tab()
        iq_tab.children = iq_tab_ch
        titles = ['Constellation', 'EVM']
        [iq_tab.set_title(i, title) for i, title in enumerate(titles)]

        # Create tab for peak inspection (peak table)
        data_tab_ch = [peak_data_display]
        data_tab = ipw.Tab()
        data_tab.children = data_tab_ch
        titles = ['Peak Data']
        [data_tab.set_title(i, title) for i, title in enumerate(titles)]


        # Configure application to launch with the following defaults
        self.inspectors['transmitter'].channel_widget.description = 'Observation Point: '
        self.inspectors['transmitter'].channel_widget.options = [('Symbols', 0), ('Interpolated', 1)]
        self.inspectors['transmitter'].channel_widget.value = 0
        self.inspectors['receiver'].channel_widget.description = 'Observation Point: '
        self.inspectors['receiver'].channel_widget.options = [('Symbols', 0), ('Decimated', 1)]
        self.inspectors['receiver'].channel_widget.value = 0
        self.inspectors['evm'].channel_widget.value = 0
        self.ofdm_transmitter.modulation_dropdown.value = '64-QAM'
        self.evm_calc_ip_0.modulation_dropdown.value = '64-QAM'
        self.evm_calc_ip_0.rms_n_ui.value = 2048
        
        # Attempt to start the OFDM constellation receiver
        def timeout_handler(signum, frame):
           raise Exception("Function timeout.")
            
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)
        try:
            self.inspectors['constellation'].get_frame()
        except Exception: 
            print(Exception)
            print("Inspection failed as synchronisation could not be performed. Please ensure that a loopback cable is connected and then restart the notebook.")
        signal.alarm(0)
        
        # Start the application and return to notebook
        # self.inspectors['receiver']._plot_controller.start()
        # self.inspectors['transmitter']._plot_controller.start()
        self.inspectors['constellation']._plot_controller.start()
        self.inspectors['evm']._plot_controller.start()
        return ipw.HBox([ipw.VBox([tx_insp_tab, rx_insp_tab]), 
                        ipw.VBox([iq_tab, data_tab])])
