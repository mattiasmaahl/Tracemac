"""
** TraceMac
** Traces a mac-address to a specific port in a switch.
** Version: 1.7.2
** License: GPLv2
"""

_VERSION_ = "1.7.2"

#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(__file__) + "\\pysnmp.egg")
sys.path.append(os.path.dirname(__file__))

# Imports:
from pysnmp.entity.rfc3413.oneliner import cmdgen
import getopt
from Switch_Object import Sw_Object  #Class to be imported later!
from Trace_Functions import *

#main variables:
SWO = list()                 #list-object to store switches
Trace_args = Tracefunctions.Trace_arguments()
dump_trace_to_file = False
list_of_targets = list()
multi_trace_file_name = ""
multiple_result = list()



##Trace_args.start_ip_address =  "192.168.1.253"      #target
###Trace_args.target_mac_address = "00089bac92fa")    #macaddress
##Trace_args.dump_file = "dumpfile.route"             #out
##Trace_args.target_ip_address = "192.168.1.99"       #ipaddress


def pr(pr_str):
    """
    function pr
    function to print out messages to stdout using a specified format.
    This is used for verbose output to stdout and logfile.
    """
    print(pr_str.center(100,"*"))
    write_to_file("%s\n" % (pr_str.center(100,"*")))

def vreport(header, *msg):
    """
    function vreport
    creates and outputs verbose output of progress.
    """
    if not msg:
        tmp = " %s" % (header.ljust(95, " "))
        print (tmp.ljust(96, " ")).center(100, "*")
        write_to_file("%s\n" % ((tmp.ljust(96, " ")).center(100, "*")))
    elif (msg == "big"):
        mystr = split_string_into_chunks(header)
        for txt in mystr:
            print (txt.ljust(96, " ")).center(100, "*")
            write_to_file("%s\n" % ((txt.ljust(96, " ")).center(100, "*")))    
    else:
        tmp = " %s -> %s" % (header.ljust(40, " "), msg)
        print (tmp.ljust(96, " ")).center(100, "*")
        write_to_file("%s\n" % ((tmp.ljust(96, " ")).center(100, "*")))

def printout(msg, *w):
    """
    function printout
    stardart output to stdout and logfile.
    """
    if w:
        print(msg,)
        write_to_file(msg)
    else:
        print(msg)
        write_to_file("%s\n" % (msg))

def write_to_file(line):
    """
    function write_to_file
    if there is a file specified in options this will write to it.
    """
    if dump_trace_to_file:
        with open(Trace_args.dump_file, "a") as myfile:
            myfile.write(line)


def split_string_into_chunks(text, length=94):
    """
    function split_string_into_chunks
    this function serves to sprit output into chunks that's under specified length.
    Default value is 94 chars.
    """
    tmp = text.split()
    retstr = []
    tmp2 = ""
    for a in tmp:
        if ((len(tmp2) + len(a)) < length):
            tmp2 = tmp2 + " " + ''.join(a)
        else:
            retstr.append(tmp2)
            tmp2 = ""
    if (len(tmp2) > 1): retstr.append(tmp2)
    return retstr

def read_infile(filename):
    """
    function read_infile
    this function serves to read the input file an store the targets for the search engine.
    """
    rettup = list()
    with open(filename, "r") as myfile:
        content = (myfile.read()).split("\n")
        for line in content:
            if line: rettup.append(line)
    if not myfile.closed: myfile.close()
    if rettup:
        return rettup
    else:
        return []

def _do_search(arg1, *args):
    """
    private function _do_search
    this is where the magic happens.
    starts a search based on the users options.
    """
    TR = Trace_result()
    
    if arg1 == "single":
        S_IP = Trace_args.target_ip_address
        S_MAC = Trace_args.target_mac_address
    elif arg1 == "multiple":
        if args:
            S_IP = args[0]["ipaddress"]
            S_MAC = args[0]["mac"]
    SWO = list()
    SWO.append(Sw_Object(Trace_args.start_ip_address))

    if v:
        vreport("IP-Address:", SWO[-1].switch_ip_address)
        vreport("System-Name:", SWO[-1].system_name)
        vreport("Mac-Address:", SWO[-1].switch_mac_address)

    pingme = False
    if (len(S_MAC) == 0):
        if v: vreport("Arguments:")
        if v: vreport("IP-Address:", S_IP)
        if not v and not _do_multiple_search: printout("Ip-address supplied. Arp-pinging to get the mac-address...")
        if not v and _do_multiple_search: printout("Searching for: %s" % (S_IP), "W")
        S_MAC = get_mac_address_from_ip(S_IP)
        if not S_MAC:
            if _do_multiple_search:
                printout( "Ping failed to host.")
                T = Trace_result()
                T.SW_O = SWO[-1]
                T.search_ip = S_IP
                T.failed = True
                T.msg = "Ping failed to host"
                return False, T
            else:
                printout( " OOOPS!! " )
                printout( " No Answer from ping. Target appears to be offline" )
                sys.exit(1)
        else:
            pingme = True
            if v and not _do_multiple_search: vreport("  Got MAC from ARP:", S_MAC)
            if not v and not _do_multiple_search: printout( "Got MAC: %s" % (S_MAC))
            if _do_multiple_search: printout(" [%s] " % (S_MAC), "W")
    if v: pr("")
    if v: pr("  STARTING TRACE  ")
    
    mac_address_is_at_endpoint = False
    while not mac_address_is_at_endpoint:
        if pingme: ping_my_address(S_IP, "1")
        
        SWO[-1].find_my_mac_address(S_MAC)
        #print "interface %s " % (SWO[-1].mac_found_at_interface)
        
        is_neighbor = SWO[-1].is_interface_a_neighbor(SWO[-1].mac_found_at_interface)
        interface = SWO[-1].get_interface(SWO[-1].mac_found_at_interface)
        has_multiple_mac = False
        if (not interface):
            if pingme: ping_my_address(S_IP)
            SWO[-1].find_my_mac_address(S_MAC)
            #print "interface %s " % (SWO[-1].mac_found_at_interface)
            is_neighbor = SWO[-1].is_interface_a_neighbor(SWO[-1].mac_found_at_interface)
            interface = SWO[-1].get_interface(SWO[-1].mac_found_at_interface)
            has_multiple_mac = False
            if (not interface):
                TR.search_ip = S_IP
                TR.SW_O = SWO[-1]
                TR.trace_end = "%s / %s" % (SWO[-1].switch_ip_address, SWO[-1].mac_found_at_interface)
                TR.failed = True
                TR.msg = "Mac-addres not found at switch last switch."
                return False, TR
        if (interface.interface == -1):
            TR.search_ip = S_IP
            TR.SW_O = SWO[-1]
            TR.trace_end = "%s / %s" % (SWO[-1].switch_ip_address, SWO[-1].mac_found_at_interface)
            TR.failed = True
            TR.msg = "IP/Mac is a switch"
            return False, TR
            
        if (len(interface.mac_address) > 1):
            has_multiple_mac = True

        if (SWO[-1].mac_found_at_interface):
            if v and not _do_multiple_search:
                vreport("Ip-Address:", SWO[-1].switch_ip_address)
                vreport("Interface:", retval)
                vreport("Interface has neighbor:", is_neighbor)
            elif (not _do_multiple_search):
                st = "Mac Found: %s/%s" % (SWO[-1].switch_ip_address, SWO[-1].mac_found_at_interface)
                printout(st, "w")
            if is_neighbor:
                neighbor = SWO[-1].get_neighbor_at_interface(SWO[-1].mac_found_at_interface)
                if v and not _do_multiple_search:
                    vreport("   with IP_address:", neighbor.ip_address)
                elif (not _do_multiple_search):
                    printout( " -> going to neighbor : %s" % (neighbor.ip_address))
            else:
                if not v and not _do_multiple_search: printout( "" )
            if v and not _do_multiple_search: vreport("Interface has multiple Mac:", has_multiple_mac)
           
            if (is_neighbor):
                if v and not _do_multiple_search: pr(" Going to next switch... ")
                SWO.append(Sw_Object(neighbor.ip_address))
                if v and not _do_multiple_search: vreport("IP-Address:", SWO[-1].switch_ip_address)
                if v and not _do_multiple_search: vreport("System-Name:", SWO[-1].system_name)
                if v and not _do_multiple_search: vreport("Mac-Address:", SWO[-1].switch_mac_address)
            elif ( not is_neighbor and has_multiple_mac):
                TR.SW_O = SWO[-1]
                TR.trace_end = "%s / %s" % (SWO[-1].switch_ip_address, SWO[-1].mac_found_at_interface)
                TR.failed = True
                TR.msg = "Interface has multiple mac!"
                return True, TR
            elif ( not is_neighbor and not has_multiple_mac):
                TR.SW_O = SWO[-1]
                TR.trace_end = "%s / %s" % (SWO[-1].switch_ip_address, SWO[-1].mac_found_at_interface)
                TR.search_ip = S_IP
                TR.search_mac = S_MAC
                TR.msg = "Success"
                if _do_multiple_search: printout("-> Success!")
                return False, TR

if __name__ == "__main__":
    ## PROGRAM STARTS HERE:
    ''' TODO: Uncomment later: '''
    Trace_args = get_system_args(sys.argv)
    if (Trace_args.dump_file):
        dump_trace_to_file = True
        fi = open(Trace_args.dump_file, "w")
        fi.close()
        
    if not Trace_args: sys.exit()
    _do_multiple_search = False
    if (Trace_args.in_file):
        multi_trace_file_name = "%s.trace" % (Trace_args.in_file)
        printout("Reading file: %s" % (Trace_args.in_file))
        
        list_of_targets = read_infile(Trace_args.in_file)
        if list_of_targets:
            _do_multiple_search = True
            printout("Found %s targets in this file." % (len(list_of_targets)))
        else:
            printout("error: no targets found")
            sys.exit(1)


    #this is to make things easier.
    v = Trace_args.verbose

    if v:
        pr("")
        pr("  TRACEMAC v%s   " % (_VERSION_))
        pr("")
    else:
        printout("")
        printout( "TRACEMAC v%s   "  % (_VERSION_) )
        printout( "Starting trace  " )
        printout( "" )

    if _do_multiple_search:
        for target in list_of_targets:
            print("pinging %s 4 times" % target)
            ping_my_address(target, "4")
            Search_table = {"ipaddress": target, "mac": ""}
            error, result = _do_search("multiple", Search_table)
            multiple_result.append(result)
            
    else:
        error, result = _do_search("single")

    if error:
        pr(" Ooops! ")
        vreport(" ")
        vreport("This Interface seems to have multiple MAC:s but no Neighbors!! this can happen when there is a non-manageble switch on the interface. Or old Firmwares. Check your dokumentation.", "big")
        vreport(" ")
        pr(" Trace ended at: ")
        vreport("Switch named:", result.SW_O.system_name)
        vreport("IP-Address / port:", result.trace_end)
        pr("")
    else:
        if not _do_multiple_search:
            if not v:
                printout( "End of search. Result: Success!")
                printout( "" )
            if v: pr("")
            pr(" Success! ")
            if (result.search_ip):
                vreport("Requested IP-Address:", result.search_ip)
                vreport("With MAC:", result.search_mac)
            else:
                vreport("Requested MAC:", result.search_mac)

            vreport("Seems to be on switch named:", result.SW_O.system_name)
            vreport("IP-Address / port:", result.trace_end)

        elif _do_multiple_search:
            f = open(multi_trace_file_name, "w")
            print("")
            pr("  Done  ")
            f.write(" Searchresults from %s\n" % (multi_trace_file_name.rstrip(".trace")))
            vreport("Search results:")
            for res in multiple_result:
                if not res.failed:
                    mystr = "%s [%s] " % (res.search_ip, res.search_mac)
                    mystr2 = "%s (%s)" % (res.SW_O.system_name, res.trace_end)
                    fstr = "%s\t%s\t%s\t%s" % (res.search_ip, res.search_mac, res.SW_O.switch_ip_address , res.SW_O.mac_found_at_interface)
                    f.write("%s\n" % (fstr))
                    vreport(mystr, mystr2)
                else:
                    fstr = "%s\t\t\t\t\t%s" % (res.search_ip, res.msg)
                    f.write("%s\n" % (fstr))
                    vreport(res.search_ip, res.msg)
            if not f.closed: f.close()

    pr("")
    if _do_multiple_search:
        printout("Se full report in file: %s" % multi_trace_file_name)
