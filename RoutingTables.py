import subprocess
import sys
import paramiko
import threading


# Host class
# Each host has an ip address, username, and password
class Host():
    ip = ''
    user = ''
    pw = ''


# Called by read_file
# Makes a host with an ip address, username, and password
# Removes newlines from each string
# returns a host
def make_host(ip, user, pw):
    host = Host()
    host.ip = str(ip.strip())
    host.user = str(user.strip())
    host.pw = str(pw.strip())
    return host


# Called by main
# Reads a .json file
# Removes extra characters from each line
# First, obtains default values if available
# At closed brackets, uses information obtained from each line to send to make_host
#       skips closed brackets when all non-default values are ''
# Informs user of unrecognized lines in the file and their line number
# Creates a list of hosts and returns that list
def read_file(json):
    host_list = []
    with open(json, 'r') as j:
        lines = j.readlines()
        linenumber = 0
        default_ip = default_user = default_password = ip = user = pw = ''
        addresses = []
        for line in lines:
            linenumber += 1
            line = line.replace(' ','')
            line = line.replace('\t','')
            line = line.replace('"','')
            line = line.replace(',','')
            if '{' in line:
                pass
            elif 'default ip' in line:
                default_ip = line.split(':')[-1]
            elif 'default user' in line:
                default_user = line.split(':')[-1]
            elif 'default password' in line:
                default_password = line.split(':')[-1]
            elif 'ip' in line:
                ip = line.split(':')[-1]
            elif 'user' in line:
                user = line.split(':')[-1]
            elif 'password' in line:
                pw = line.split(':')[-1]
            elif '}' in line:
                if ip == user == pw == '':
                    pass
                else:
                    if ip == '':
                        ip = default_ip
                    if user == '':
                        user = default_user
                    if pw == '':
                        pw = default_password
                    addresses = get_ips(ip)
                    if addresses is not None:
                        for address in addresses:
                            host = make_host(address, user, pw)
                            host_list.append(host)
                        ip = user = pw  = ''
            else:
                print('Unrecognized line at '+str(linenumber))
    return host_list


# Called by Formatting
# Checks if the value is an integer
# returns True if it is an int, False if it is not
def is_Int(s):
    try:
        int(s)
        return True
    except Exception as e:
        return False


# Called by get_ips
# Determines if the lower and higher bounds of the IP range must be switched
# If the first different value between the two values is higher in the lower bound
#   returns False so they will be switched
# If the values are the same or the higher bound is higher, 
#   returns True so they will not be switched
def switch(bound, curr):
    x = 0
    while x < len(bound):
        if bound[x] > curr[x]:
            break
        elif bound[x] < curr[x]:
            return False
        x += 1
    return True


# Called by get_ips
# Checks if the IP addresses are formatted correctly
# First, checks that there are four octets in each address      ex 10.1.2.3.4.5.6.7.8
# Then, calls is_Int to determine if the values are all ints    ex 10.a.2.3
# Then, checks if the values are within 255 and 0 inclusive     ex: 10.1.999.3 or 10.1.-8.3
# Last, checks if the octets has more than 3 characters in it   ex: 10.1.2.4444444
def Formating(bound, curr):
    x = 0
    if len(bound) != 4 or len(curr) != 4:
        print ('IP address error. There must be four octets in an address')
        return
    while x < len(bound):
        if is_Int(bound[x]) is False or is_Int(curr[x]) is False:
            print ('IP address error. Octets must be integers.')
            return
        if int(bound[x]) > 255 or int(curr[x]) > 255:
            print ('IP address error. Octets must be less than or equal to 255.')
            return
        if int(bound[x]) < 0 or int(curr[x]) < 0:
            print ('IP address error. Octets must be non-negative.')
            return
        if len(bound[x]) > 4 or len(curr[x]) > 4:
            print ('IP address error. Octets can be at most three digits long.')
            return
        x +=1
    return 0


# Called by read_file
# Takes in an ip or ip range as an argument ex: 10.1.2.3 or 10.1.2.3-10.1.5.6
# Splits this arg and places the first value in curr_addr
# switch and Formatting are called to determine if the values are in the correct order
#   and if the formatting is correct
# If switch returns false, curr_addr and addr_bound are switched
# Creates a list of ip addresses based on the range
# returns the list of ip addresses
def get_ips(addr):
    addr_bound = addr.split('-')
    addr_list = []
    curr_split = []
    curr_addr = addr_bound[0]
    addr_bound_check = addr_bound[-1].split('.')
    curr_addr_check = addr_bound[0].split('.')
    if Formating(addr_bound_check, curr_addr_check) is None:
        return
    if switch(addr_bound_check, curr_addr_check) is False:
        hold = addr_bound[-1]
        addr_bound[-1] = curr_addr
        curr_addr = hold
    while curr_addr not in addr_bound[-1]:
        addr_list.append(curr_addr)
        curr_split = curr_addr.split('.')
        if curr_split[3] == '255':
            if curr_split[2] == '255':
                if curr_split[1] == '255':
                    if curr_split[0] == '255':
                        print ('IP Address out of poccible IP range!')
                        break
                    else:
                        curr_split[0] = str(int(curr_split[0]) + 1)
                        curr_split[1] = '0'
                else:
                    curr_split[1] = str(int(curr_split[1]) + 1)
                    curr_split[2] = '0'
            else:
                curr_split[2] = str(int(curr_split[2]) + 1)
                curr_split[3] = '0'
        else:
            curr_split[3] = str(int(curr_split[3]) + 1)
        curr_addr = curr_split[0] + '.' + curr_split[1] + '.' + curr_split[2] + '.' + curr_split [3]
    addr_list.append(curr_addr)
    return addr_list


# Called by make_threads
# Creates a SSH Client
# Attempts to establish a connection using the host ip, username, and password
# Runs the route -n command once connection is established
# Placed the output into printout at x location
# Closes the connection
# Exceptions occur when:
#   a connection cannot be made
#   an authentication failure occues
#   an unexpected error
def run_route(addr, printout, x):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname = str(addr.ip), username = str(addr.user), password = str(addr.pw))
        stdin, stdout, stderr = client.exec_command('route -n')
        printout[x] = str(addr.ip) + ' Routing Table.\n'
        for line in stdout:
            printout[x] = printout[x] + line
        printout[x] = printout[x] + '\n'
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        printout[x] = str(addr.ip) + ' failed to establish a connection.\n'
    except paramiko.ssh_exception.AuthenticationException as e:
        printout[x] = str(addr.ip) + ' failed to authenticate.\n'
    except Exception as e:
        printout[x] = str(addr.ip) + ' encountered an error.\n'
    client.close()


# Called by main
# Creates threads to run run_route with a host
# Prinout keeps the outputs from the threads organized
# Threads join and wirte their outputs one at a time to the file
def make_threads(fname, host_list):
    threads = []
    printout = []
    x = 0
    while x < len(host_list):
        printout.append('')
        t = threading.Thread(target = run_route, args = (host_list[x], printout, x))
        threads.append(t)
        t.daemon = True
        t.start()
        x += 1
    x = 0
    f = open(fname, 'w')
    while x < len(threads):
        threads[x].join()
        f.write(printout[x])
        x += 1
    f.close()


# Takes in an input and output file
# Calls read_file to obtain a list of hosts
# If the list is empty, return None
# Calls make_threads
# Exception when the arguments are too few or too many
def main():
    try:
        fname = sys.argv[2]
        json = sys.argv[1]
        host_list = read_file(json)
        if host_list is None:
            return
        make_threads(fname, host_list)
    except Exception as e:
        print("""Not enough arguments. The proper formats are:\n
        python3 RoutingTables.py [input json path] [output file path]\n
        python3 RoutingTables.py [input json path] [output file path]""")


main()

