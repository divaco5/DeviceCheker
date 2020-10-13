# DeviceCheker
A device health check program. You can specify the interval (in seconds) and number of times to check.
It is possible to monitor from one to multiple devices.
The settings can be made in YAML file.

# Tree

```
.
├── device_list.csv
├── device_list_zero.csv
├── log
│   └── logger.log
├── report
│   └── file_2020-10-06\ 01:35:44.842671.txt
└── src
    ├── check_device.py
    └── setting.yaml
```

- device_list.csv
  -please add the device ids which you would like to do health check on this list.

- log
  -log folder save log files

- report
  -report folder save report files

- src
  -src folder have setting file and sorce code


# setting

- DeviceListPath
  - set the file path "device_list.csv"
- OutputReportPath
  - set the output folder for report
- LogPath
  - set the log folder for logging

- Interval
  - Interval is in seconds
- Threads
  - Threads is execution unit of a program's operations
- Count
  - Count is number of times to check

- ContinueMode
  - ContinueMode is continualy execute. 
  - set the True or False
  - If it is False, then the Count takes precedence

# Output Report
The output report is generated at the interval of the device check.

```
| Device | Connected to IoT | Last Connectivity Event | Checking device Datetime|
| 000022 | false            | Unknown                 | 2020-10-06 01:56:39.070435 |
| 000027 | true             | 2020-10-02 14:47:18 +0900 JST (3 days ago) | 2020-10-06 01:56:40.645041 |
| 000035 | true             | 2020-10-05 22:18:41 +0900 JST (3 hours ago) | 2020-10-06 01:56:41.865955 |
| 000036 | true             | 2020-10-02 15:08:14 +0900 JST (3 days ago) | 2020-10-06 01:56:42.985894 |
| 000070 | true             | 2020-10-05 17:00:28 +0900 JST (8 hours ago) | 2020-10-06 01:56:43.884830 |
| 000071 | true             | 2020-10-05 17:00:27 +0900 JST (8 hours ago) | 2020-10-06 01:56:44.765666 |
```
- Device
  - Device id
- Connected to IoT
  - true is working and false is not working
- Last Connectivity Event
  - Datetime for last connectivity event
- Checking device Datetime
  - Datetime for checking device
  
# log

- An error message appears if the input data is unexpected.
- An error message appears if a device ID in the device list is not available for handling.
