"""Software to save beamline positions for a specific energy with EPICS

   Classes
   -------
   Energy
     Base class for energy save with EPICS.
"""
import time
import threading
import subprocess

from epics import PV

from energy import log


class Energy():

    def __init__(self, pv_files, macros):

        # init pvs
        self.config_pvs = {}
        self.control_pvs = {}
        self.pv_prefixes = {}

        if not isinstance(pv_files, list):
            pv_files = [pv_files]
        for pv_file in pv_files:
            self.read_pv_file(pv_file, macros)
        self.show_pvs()

        self.epics_pvs = {**self.config_pvs, **self.control_pvs}

        # Wait 1 second for all PVs to connect
        time.sleep(1)

        for epics_pv in ('EnergyMove', 'EnergyMoveSet', 'EnergyArbitrary'):
            self.epics_pvs[epics_pv].add_callback(self.pv_callback)
        for epics_pv in ('EnergyMove', 'EnergyMoveSet', 'EnergyBusy'):
            self.epics_pvs[epics_pv].put(0)

        # Start the watchdog timer thread
        thread = threading.Thread(target=self.reset_watchdog, args=(), daemon=True)
        thread.start()

        self.epics_pvs['EnergyStatus'].put('Done')

        log.setup_custom_logger("./energy.log")
        print("./energy.log")


    def pv_callback(self, pvname=None, value=None, char_value=None, **kw):
        """Callback function that is called by pyEpics when certain EPICS PVs are changed
        """

        print('pv_callback pvName=%s, value=%s, char_value=%s' % (pvname, value, char_value))
        if (pvname.find('EnergyMove') != -1) and (value == 1):
            thread = threading.Thread(target=self.energy_change, args=())
            thread.start()       
        elif (pvname.find('EnergyMoveSet') != -1) and (value == 1):
            thread = threading.Thread(target=self.energy_move_set, args=())
            thread.start()       
        elif (pvname.find('EnergyArbitrary') != -1):
            thread = threading.Thread(target=self.energy_in_range, args=())
            thread.start()

    def energy_change(self):

        if self.epics_pvs['EnergyStatus'].get(as_string=True) != 'Done' or self.epics_pvs['EnergyBusy'].get() == 1:
            return
            
        if (self.epics_pvs["EnergyTesting"].get()):
            self.epics_pvs['EnergyStatus'].put('Changing energy testing')
        else:
            self.epics_pvs['EnergyStatus'].put('Changing energy')

        self.epics_pvs['EnergyBusy'].put(1)

        energy_choice_min = float(PV(self.epics_pvs["EnergyChoice"].pvname + '.ONST').get().split(' ')[1])
        energy_choice_max = float(PV(self.epics_pvs["EnergyChoice"].pvname + '.NIST').get().split(' ')[1])

        if self.epics_pvs["EnergyCalibrationUse"].get(as_string=True) == "Pre-set":
            self.epics_pvs['EnergyStatus'].put('Changing energy: using presets')

            energy_choice_index = str(self.epics_pvs["EnergyChoice"].get())
            energy_choice       = self.epics_pvs["EnergyChoice"].get(as_string=True)
            energy_choice_list  = energy_choice.split(' ')
            log.info("Energy: energy choice = %s" % energy_choice)
            if energy_choice_list[0] == 'Pink':
                command = 'energy pink --force'
            else: # Mono
                command = 'energy set --energy ' + energy_choice_list[1] + ' --force'
        else:
            energy_arbitrary = self.epics_pvs['EnergyArbitrary'].get()
            if  (energy_arbitrary >= energy_choice_min) & (energy_arbitrary < energy_choice_max):
                command = 'energy set --energy ' + str(self.epics_pvs['EnergyArbitrary'].get()) + ' --force'
                self.epics_pvs['EnergyInRange'].put(1)
            else:
                self.epics_pvs['EnergyStatus'].put('Error: energy out of range')
                self.epics_pvs['EnergyInRange'].put(0)
                time.sleep(2) # for testing
                self.epics_pvs['EnergyStatus'].put('Done')
                self.epics_pvs['EnergyBusy'].put(0)   
                self.epics_pvs['EnergyMove'].put(0)
                return
        if (self.epics_pvs["EnergyTesting"].get()):
            command =  command + ' --testing' 
        
        log.error(command)
        subprocess.Popen(command, shell=True)        

        time.sleep(10)
        log.info('Energy: waiting on motion to complete')
        while True:
            time.sleep(.3)
            if PV('2bma:alldone').get() and PV('2bmb:alldone').get():
                break
        log.info('motion completed')

        time.sleep(2) # for testing
        self.epics_pvs['EnergyStatus'].put('Done')
        self.epics_pvs['EnergyBusy'].put(0)   
        self.epics_pvs['EnergyMove'].put(0)   

    def energy_move_set(self):

        if self.epics_pvs['EnergyStatus'].get(as_string=True) != 'Done':
            return
            
        self.epics_pvs['EnergyStatus'].put('Changing energy move setting update')
        self.epics_pvs['EnergyBusy'].put(1)
        command = 'energy status'
        log.error(command)
        subprocess.Popen(command, shell=True)     
        time.sleep(2) # for testing
        self.epics_pvs['EnergyStatus'].put('Done')
        self.epics_pvs['EnergyMoveSet'].put(0)   
        self.epics_pvs['EnergyBusy'].put(0)

    def energy_in_range(self):

        if self.epics_pvs['EnergyStatus'].get(as_string=True) != 'Done' or self.epics_pvs['EnergyBusy'].get() == 1:
            return

        energy_choice_min = float(PV(self.epics_pvs["EnergyChoice"].pvname + '.ONST').get().split(' ')[1])
        energy_choice_max = float(PV(self.epics_pvs["EnergyChoice"].pvname + '.NIST').get().split(' ')[1])

        energy_arbitrary = self.epics_pvs['EnergyArbitrary'].get()
        if  (energy_arbitrary >= energy_choice_min) & (energy_arbitrary < energy_choice_max):
            command = 'energy set --energy ' + str(self.epics_pvs['EnergyArbitrary'].get()) + ' --force'
            self.epics_pvs['EnergyInRange'].put(1)
        else:
            self.epics_pvs['EnergyStatus'].put('Error: energy out of range')
            self.epics_pvs['EnergyInRange'].put(0)
 
        time.sleep(2) # for testing
        self.epics_pvs['EnergyStatus'].put('Done')
        self.epics_pvs['EnergyBusy'].put(0)   
        self.epics_pvs['EnergyMove'].put(0)   

    def reset_watchdog(self):
        """Sets the watchdog timer to 5 every 3 seconds"""
        while True:
            self.epics_pvs['Watchdog'].put(5)
            time.sleep(3)

        # log.setup_custom_logger("./energy.log")

    def read_pv_file(self, pv_file_name, macros):
        """Reads a file containing a list of EPICS PVs to be used by MCTOptics.


        Parameters
        ----------
        pv_file_name : str
          Name of the file to read
        macros: dict
          Dictionary of macro substitution to perform when reading the file
        """

        pv_file = open(pv_file_name)
        lines = pv_file.read()
        pv_file.close()
        lines = lines.splitlines()
        for line in lines:
            is_config_pv = True
            if line.find('#controlPV') != -1:
                line = line.replace('#controlPV', '')
                is_config_pv = False
            line = line.lstrip()
            # Skip lines starting with #
            if line.startswith('#'):
                continue
            # Skip blank lines
            if line == '':
                continue
            pvname = line
            # Do macro substitution on the pvName
            for key in macros:
                pvname = pvname.replace(key, macros[key])
            # Replace macros in dictionary key with nothing
            dictentry = line
            for key in macros:
                dictentry = dictentry.replace(key, '')

            epics_pv = PV(pvname)

            if is_config_pv:
                self.config_pvs[dictentry] = epics_pv
            else:
                self.control_pvs[dictentry] = epics_pv
            # if dictentry.find('PVAPName') != -1:
            #     pvname = epics_pv.value
            #     key = dictentry.replace('PVAPName', '')
            #     self.control_pvs[key] = PV(pvname)
            if dictentry.find('PVName') != -1:
                pvname = epics_pv.value
                key = dictentry.replace('PVName', '')
                if (pvname != ''): 
                    print(pvname, key)
                    self.control_pvs[key] = PV(pvname)
            if dictentry.find('PVPrefix') != -1:
                pvprefix = epics_pv.value
                key = dictentry.replace('PVPrefix', '')
                self.pv_prefixes[key] = pvprefix

    def show_pvs(self):
        """Prints the current values of all EPICS PVs in use.

        The values are printed in three sections:

        - config_pvs : The PVs that are part of the scan configuration and
          are saved by save_configuration()

        - control_pvs : The PVs that are used for EPICS control and status,
          but are not saved by save_configuration()

        - pv_prefixes : The prefixes for PVs that are used for the areaDetector camera,
          file plugin, etc.
        """

        print('configPVS:')
        for config_pv in self.config_pvs:
            print(config_pv, ':', self.config_pvs[config_pv].get(as_string=True))

        print('')
        print('controlPVS:')
        for control_pv in self.control_pvs:
            print(control_pv, ':', self.control_pvs[control_pv].get(as_string=True))

        print('')
        print('pv_prefixes:')
        for pv_prefix in self.pv_prefixes:
            print(pv_prefix, ':', self.pv_prefixes[pv_prefix])
