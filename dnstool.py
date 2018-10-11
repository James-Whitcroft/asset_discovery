"""
Software:DNS Enumerating tool
Author: Eliezer Garcia
10/7/2018
about:
this project is a tool used to obtain the ip address of a hostname
requirements: this tool takes in 2 file locations
        1)the DNS hostname fil location
             *the file must be formatted with the hostname on each line
             *alterations can be done to the code to condense file usage such as separating hostname by comma using the split function
        2)the location file which is where the results will be writen on
             *result will be separated into 2 rows hostname & ip address
"""
import socket
"""
the DnsTool function implements majority of the code such as asking for the file names and opening and obtaining the ip 
address for the hostname
if the hostname is not resolved a message will be indicated 
hostnames should be in the format such as bob.company.net and such
hostnames with subdirectory are not tolerated bob.company.net/jobs/tell-com
       ********************************************************************
        minor changes can be done to the code to help enforce other options such a printing the type of service offered
            
"""
def DnsTool():
      #user input is needed as far as file location
      filename = input("Enter the DNS file location:\n"
                       "(this is the file location of host names):\n")
      outfile = input("Enter DNS(ip address to domain name) destination file location:\n")

      file=open(filename,"r")
      output=open(outfile,"w")

      output.write("Opening file"+filename+"........\n")
      output.write("Hostname:"+" "*31+"Ip Address:\n")

      for line in file:
            try:
                  output.write("Hostname: "+" "*10+line.strip()
                               +"\n"+"Ip Address:"+" "*9+socket.gethostbyname(line.strip())+"\n"
                               +"-"*100+"\n")
            except socket.gaierror:\
                  output.write("Hostname: "+" "*10+line.strip()
                               +"\n"+"Ip Address:"+" "*9+"cannot resolve hostname:\n"
                               + "-" * 100 + "\n")
      output.write("Finished......\n")
      file.close()
      output.close()

"""
the main function only calls DnsTool which is where majority of the code is implemented 
"""
def main():
      DnsTool()


if __name__ == '__main__':
    main()
