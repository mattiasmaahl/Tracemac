"""
Created 2013-08-27\n
@author Mattias Måhl\n
Class Tracefunctions\n
Functions to administrate search for MAC-adress\n
"""

import subprocess
import sys
import getopt  

class Tracefunctions:
    def get_system_args(argv):
        """
        function get_system_args
        function to parse system arguments in cli-envioronment.
        Args:
            -h, --help=           Display helptext for cli-command.

            -i, --ipaddress=      Target ip-address to find in the network.
                                  *note* this implies access to both mgmnt- and target network (if separate)

            -s, --startingip=     IP-address of the first switch in the cascade.

            -o, --out=            Output logging top specified file.

            -m, --macaddress=     Target MAC-address to find in the network.

            -v, --verbose=        Enebles verbose output to standard output and logging file if '-o/-out= is used.

            -f, --in-file         Enables function to loop through a list of targets in a text file.
                                  *note* One target per line.
        """
        global dump_trace_to_file
        
        targs = self.Trace_arguments()
        if(len(argv) == 1):
            printhelp()
            sys.exit(1)
        try:
            opts, args = getopt.getopt(
                argv[1:],
                "hi:s:o:m:vf:",
                ["ipaddress=", "help", "startingip=", "out=", "macaddress=", "verbose", "in-file="])
        except getopt.GetoptError:
            print("Options error: check your supplied options!")
            printhelp()
            sys.exit(1)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                printhelp()
            if opt in ("-i", "--ipaddress"):
                targs.target_ip_address = arg
            if opt in ("-s", "--startingip"):
                targs.start_ip_address = arg
            if opt in ("-o", "--out"):
                targs.dump_file = arg
                dump_trace_to_file = True
            if opt in ("-m", "--macaddress"):
                targs.target_mac_address = self.fix_macaddress(arg)
            if opt in ("-v", "--verbose"):
                targs.verbose = True
            if opt in ("-f", "--in-file"):
                targs.in_file = arg
        if (chk_system_args(targs)):
            return targs
        else:
            return False

    def chk_system_args(argv):
        """
        function chk_system_args
        function to check if argumest supplied are correct and that mandatory argurments are supplied.
        """
        if (not argv.start_ip_address):
            print("Syntax error Required option --startingip(-s) not specified\n")
            printhelp()
            return False
        if (not argv.target_mac_address and not argv.target_ip_address):
            if not argv.in_file:
                print("Syntax error: -i or -m not set\n")
                printhelp()
                return False
        if (argv.target_mac_address and argv.target_ip_address):
            print("Syntax error: -i and -m set can only use one or the other.\n")
            printhelp()
            return False
        return True

    def fix_macaddress(MAC):
        """
        function fix_macaddres
        this function fixes the mac-address to be exactly the same even if the user supplies it in different formats.
        i.e 121212-121212 will become 121212121212 and likewise 12:12:12:12:12:12 will become 121212121212.
        """
        return (MAC.replace("-", "")).replace(":", "")
        
    ## Print the help text:
    def printhelp():
        """
        function printhelp
        duh!
        """
        print ("""
        Tracemac 1.7.1 Usage:
        ---------------------------------------------------------------------------------------------------------------
        ./tracemac.py [-h] -s {IP-ADDRESS} [{-m [MAC-ADDRES]} OR {-i [IP-ADDRESS]} [-o {PATH/TO/OUTPUT.FILE]} 
        
        OPTIONS:
            -h, --help	    Displays this help.

        REQUIRED OPTION:    
            -s, --starting-ip   defines witch ip-address to start the search
                                This is Required!
                                example: ./tracemac.py -i 192.168.1.1
                                    
        ONE OF THE FOLLOWING HAS TO BE SET:
            -m, --macaddress    Whitch Mac-Address to trace.
                                Accepted strings:
                                    0000aa-9973ab
                                    00:00:aa:99:73:ab
                                note: this option requires an up-to-date arp-table
                                
            -i, --ipaddress     Whitch Ip-address to trace.

        OPTIONAL ARGS:
            -o, --out           Dump the trace to a file.
            -v, --verbose       Print all information
            -f, --in-file       Specify a file witch contains a list of IP-addresses
                                This option cannot be used with -m or -i

    ---------------------------------------------------------------------------------------------------------------
     Auther: Mattias Måhl 2012
    """)
        sys.exit(0)

    def get_mac_address_from_ip(ipaddress):
        """
        function get_mac_address_from_ip
        function to arping an ip address to get the Mac-address assosiated woth it.
        It's important that the target ip address is on the same network as the machine running the program and NOT routed!
        If it's routed the routers mac address will be the one reported by the arping!
        """
        ip_alive = False
        p=subprocess.Popen('ping -c 1 ' + ipaddress, shell=True, stdout=subprocess.PIPE)
        output, errors = p.communicate()
        if output is not None:
            for i in output.split('\n'):
                if "1 received" in i:
                    ip_alive = True

        if not ip_alive:
            p=subprocess.Popen('ping -c 1 ' + ipaddress, shell=True, stdout=subprocess.PIPE)
            output, errors = p.communicate()
            if output is not None:
                for i in output.split('\n'):
                    if "1 received" in i:
                        ip_alive = True
            if not ip_alive:
                return False

        p=subprocess.Popen('arp -a ' + ipaddress, shell=True, stdout=subprocess.PIPE)
        output, errors = p.communicate()
        if output is not None :
            for i in output.split("\n"):
                if ipaddress in i:
                    for j in i.split():
                        if ":" in j:
                            return j.replace(":","")
        return False

    def ping_my_address(ipaddress, cnt):
        """
        function ping_my_address
        simple function to ping the target IP-address to keep the Mac-address table up-to-date.
        """
        p=subprocess.Popen('ping -c %s %s' % (cnt, ipaddress), shell=True, stdout=subprocess.PIPE)
        output, errors = p.communicate()

    class Trace_arguments:
        """
        Class Trace_arguments
        Object to store the supplied arguments.
        """
        start_ip_address = ""
        target_mac_address = ""
        dump_file = ""
        target_ip_address = ""
        verbose = False
        in_file = ""

    class Trace_result:
        """
        Class Trace_result
        Object to store a single result from the search.
        This stores the path the program took to find the port witch has the mac-adress.
        """
        SW_O = list()
        trace_end = ""
        search_ip = ""
        search_mac = ""
        failed = False
