import time
import os
import subprocess
import yaml
import logging
import sys
import requests
import pandas as pd
import os.path
from datetime import datetime
from subprocess import PIPE
from concurrent import futures

logger = logging.getLogger(__name__)


class DeviceChecker(object):
    """
    devices health check

    Attributes
    ----------
    interval_sec : int
        check interval 
    count_max : int
        how many times check devices
    threads_max : int
        threads max number
    device_count : int
        Number of device 
    device_list : str
        device id list
    device_list_path : str
        path of device list(csv file)
    report_path : str
        path of output report
    """
    def __init__(self):

        # load yaml file
        with open('setting.yaml') as file:
            setting = yaml.safe_load(file)

        # record log 
        if not os.path.exists(setting['LogPath']):
            error_log_path = "[ERROR](LogPath)Cannot find the folder specified"
            print(error_log_path)
            sys.exit()
        logging.basicConfig(filename=setting['LogPath'] + '/logger.log', level=logging.DEBUG)

        # variable setting        
        self._device_list_path = setting['DeviceListPath']
        self._report_path      = setting['OutputReportPath']

        self._init_path_error_check()

        self._report_result    = ['| Device | Connected to IoT | Last Connectivity Event | Checking device Datetime|']
        device_df = pd.read_csv(self._device_list_path, dtype=str, header=None)
        
        self._device_list      = list(device_df.values.flatten())
        self._device_count     = len(self._device_list)
        self._interval_sec     = setting['Interval']
        self._threads_max      = setting['Threads']
        self._count_max        = setting['Count']
        self._contine_mode     = setting['ContinueMode']
        self._slack_token      = setting['SlackToken']
        self._slack_channel    = setting['SlackChannel']

        self._init_value_error_check()


    def __call__(self):
        print("---run DeviceChecker-----")
        _start_time = 0
        if self._contine_mode == False:
            # count mode
            for i in range(self._count_max):
                self._check_multi_device(_start_time)
        else:
            # coutinue mode
            while True:
                self._check_multi_device(_start_time)

    def _is_non_zero_file(self, fpath): 
        return True if os.path.isfile(fpath) and os.path.getsize(fpath) > 0 else False 

    def _init_path_error_check(self):
        """Function of verify the folder and files entered.

        Args:
        
        Note:
            (The target path)
            device_list_path(file), report_path(folder)
        """
        if not os.path.isfile(self._device_list_path):
            error_device_list_path = "[ERROR](DeviceListPath)Cannot find the file specified"
            logger.error(error_device_list_path)
            print(error_device_list_path)
            sys.exit()
        if not self._is_non_zero_file(self._device_list_path):
            error_device_list_file = "[ERROR](DeviceListPath)The file specified is empty"
            logger.error(error_device_list_file)
            print(error_device_list_file)
            sys.exit()          
        if not os.path.exists(self._report_path):
            error_report_path = "[ERROR](OutputReportPath)Cannot find the folder specified"
            logger.error(error_report_path)
            print(error_report_path)
            sys.exit()

    def _init_value_error_check(self):
        """Function of verify the value entered.

        Args:
        
        Note:
            (The target variable)
            interval, count, threads, countine_mode device_count
        """  
        if not isinstance(self._interval_sec, int):
            error_interval = "[ERROR]Interval is not int. please set int value"
            logger.error(error_interval)
            print(error_interval)
            sys.exit()
        if not isinstance(self._count_max, int):
            error_count = "[ERROR]Count is not int. please set int value"
            logger.error(error_count)
            print(error_count)
            sys.exit()
        if not isinstance(self._threads_max, int):
            error_threads = "[ERROR]Threads is not int. please set int value"
            logger.error(error_threads)
            print(error_threads)
            sys.exit()
        if self._contine_mode is None: 
            error_contine_mode = "[ERROR]ContinueMode is not setting. please set True/False" 
            logger.error(error_contine_mode)
            print(error_contine_mode)
            sys.exit()          
        if self._device_count == 0:
            error_device_count = "[ERROR]device ID doesn't exist."
            logger.error(error_device_count)
            print(error_device_count)
            sys.exit()

        # output setting
        print(self._device_list)
        print('interval: {}'.format(self._interval_sec))
        print('count   : {}'.format(self._count_max))
        print('thread  : {}'.format(self._threads_max))
        print('device  : {}'.format(self._device_count))
        print('mode    : {}'.format(self._contine_mode))


    def _output_report(self, timestamp):
        """Function of output device health check report

        Args:
            timestamp : check start time
        
        Note:
        """
        print('output report')
        print(timestamp)
        f_name = self._report_path + "file_" + str(timestamp) + ".txt"
        with open(f_name, 'w') as f:
            for d in self._report_result:
                f.write("%s\n" % d)

        del self._report_result[1:]

    def _store_result(self, device_result):
        """Function of store the each device result

        Args:
            device_result(str) : result from each device
        
        Note:
        """        
        self._report_result.append(device_result)

    def _check_multi_device(self,_start_time):
        """Function of multi device health check and report

        Args:
            _start_time : for calculate interval

        Note:
        """
        _start_date_str = str(datetime.now())
        _start_time = int(datetime.now().strftime('%s'))
        
        while int(datetime.now().strftime('%s')) - _start_time < self._interval_sec:
            time.sleep(0.1)

        threads = []
        with futures.ThreadPoolExecutor(max_workers=self._threads_max) as executor:
            for j in range(self._device_count):
                future = executor.submit(fn=self._check_device(self._device_list[j]))
                threads.append(future)
                print(future)
            _ = futures.as_completed(fs=threads)
        print(_start_date_str)
        # report output
        self._output_report(_start_date_str)


    def _check_device(self, device_id):
        """Function of each device health check

        Args:
            device_id(str): device_id
        Note:
        """
        # call tellus API for checking device
        # ex) "tellus check -d 000022"
        date_str = str(datetime.now())
        command_text = "tellus check -d " + str(device_id)
        print(command_text)
        proc = subprocess.run(command_text, shell=True, stdout=PIPE, stderr=PIPE)
        output_status = proc.stdout.decode("utf8")
        lines = output_status.splitlines()

        #error check
        if 'error occurred' in lines[-1]:
            logger.error("[ERROR]device_id:{} is not avalable".format(device_id))
        elif 'false' in lines[-1]:
            print("chatbot")
            # if the status of device is false, share the message using slack bot
            output_message = lines[-1] + date_str + " |" 
            url = "https://slack.com/api/chat.postMessage"
            data = {
            "token": self._slack_token,
            "channel": self._slack_channel,
            "text": output_message
            }
            requests.post(url, data=data)
        else:      
            extract_status = lines[-1] + date_str + " |" 
            print(extract_status)
            self._store_result(extract_status)

        
if __name__ == '__main__':

    # run device checker
    device_checker = DeviceChecker()
    device_checker()