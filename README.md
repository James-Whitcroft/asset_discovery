# asset_discovery
#### The Dnstool.py is a python code which takes in a list of hostnames and returns the coresponding ip address on another fil location 
*2 files are given 
*hostnamelist.txt shows an eample of how the hostnams should b formated 
*hostnameoutputfile.txt is th file in which th hostanem and addresseer are wrighten under 
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


### The RoutingTables.py script allows a user to remotely gather all the routing tables from a lists of hosts
### Call python3 RoutingTables.py rttest.json output.txt
* The json file is read and creates hosts based off of the file
* Connections are attempted to each host
* Runs route -n on each host and prints it to the output file
