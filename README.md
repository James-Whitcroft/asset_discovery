# asset_discovery

#### The ping_sweep powershell script allows for host detection and OS detection

##### Run with `.\ping_sweep.ps1`
###### Ping sweep provides an interactive command line interface
* Enter 1 to read ip addresses from a file
  * See os_detection_sample.txt for sample input
* Enter 2 to manually enter a range
  * Range formats are:
    * RANGE - 10.10.1.1-10.10.2.50
    * CIDR - 192.168.1.0/24
* UP hosts and their OS will be reported on completion
