"""
Created 2013-08-27\n
@author Mattias Måhl\n
Class Switch_Object\n
This is an object to store Switchdata in.\n
"""

import sys
import os
sys.path.append(os.path.dirname(__file__) + "\\pysnmp.egg")
sys.path.append(os.path.dirname(__file__))

from pysnmp.entity.rfc3413.oneliner import cmdgen
import subprocess
from Trace_Functions import *

#error handling:
class sw_error(Exception):
    #: specific function to handle exceptions in the class.
    
    def __init__(self, error_msg):
        self.msg = "Tracemac error: %s" % (error_msg)
    def __str__(self):
        return repr(self.msg)



class Sw_Object:
    """
        Initilization of the Switch Object setting up the switch and
        getting the information from the switch through SNMP.\n
        Defining the tuples and variables to store the switch data. 
    """
    #: Class Sw_Object of Module Switch_Object
    
    def __init__(self, *ipaddress):
        """
        __init__:
        @param: self(auto) ipaddress(required)
        @usage: a = Sw_Object("x.x.x.x")
        """
        
        ipadd = '0.0.0.0'
        #Contructing the switch-objects data-components.
        if ipaddress:
            try:
                self.check_ip_address(ipaddress[0])
                self.check_if_alive(ipaddress[0])
            except sw_error as e:
                print (e)
                sys.exit(1)
            ipadd = ipaddress[0]
        
        self.switch_ip_address = ipadd          # Setting Switch IP-Address
        self.switch_mac_address = ""            # The Switch own Mac-address
        self.switch_neighbors = list()          # switch_neigboures - list of the switches neigbours and their ip-addreses.
        self.interface_list = list()            # interface_list - list of interfaces and their mac-addresses.
        self.mac_found_at_interface = 0         # Variable to store where the mac_address is found. Default = 0. this is set by find_my_mac_address.
        self.system_name = ""
        if (ipaddress):
            #self.switch_mac_address = get_mac_address_from_ip(self.switch_ip_address)
            self.get_mac_address_list()         # Gather the switches mac-address table.
            self.find_switch_mac_address()      # store the switches own macaddress to the object.
            self.get_neighbors()
            self.get_switch_data()

    class cl_switch_interface:
        """
        class cl_switch_interface\n
        Switch_objects interface object to store mac-adresses assosiated with the interface.\n
        """
        def __init__(self, interface, mac_address):
            self.interface = interface
            self.mac_address = list()
            self.mac_address.append(mac_address)
            
    class cl_switch_neighbors:
        """
        class cl_switch_neighbores\n
        Switch_Objects neighbors object to store the switches neighbors and witch interface their on.\n
        """
        interface = 0
        ip_address = ''
        name = ''
        remote_interface = 0
        def __init__(self, interface):
            self.interface = interface

    def get_switch_data(self):
        """Do snmp-recuest to get the system name of the target switch."""
        errorIndication, errorStatus, errorIndex, SystemName = self._do_snmp_request('system-name')
        self.system_name = SystemName[0][1]
        

    def find_switch_mac_address(self):
        """
        function find_switch_mac_address()\n
        Do snmp request för oid: 1.3.6.1.4.1.11.2.14.11.5.1.1.6.0 (BaseMacAddress)\n
        """
        errorIndication, errorStatus, errorIndex, MacAddr = self._do_snmp_request('base_mac_address')
        try:
            self.switch_mac_address = str(MacAddr[0][1]).encode('hex')
        except IndexError as e:
            print(MacAddr)
            sys.exit(1)

    def check_if_alive(self, ipaddress):
        """
        function check_if_alive\n
        function to ping host to see if it's alive.\n
        raises error if it's a fail.\n
        """
        p=subprocess.Popen('ping -c 1 ' + ipaddress, shell=True, stdout=subprocess.PIPE)
        output, errors = p.communicate()
        if output is not None :
            for i in output.split("\n"):
                if "1 received" in i:
                    return True
        raise sw_error('Ping to host failed!')
            
    def check_ip_address(self, ipaddress):
        """
        function check_ip_address\n
        function to check if the ip-address provided is acceptable.\n
        i.e. number(dot)number(dot)number(dot)number\n
        return False if not and returns the same string if True\n
        """
        if (ipaddress.count(".") == 3):
            return ipaddress
        else:
            raise sw_error('Ip-address: %s is in the wrong format. Correct format is xxx.yyy.zzz.aaa' % (ipaddress))


    def find_my_mac_address(self, mac_address):
        """function to search the Mac-table of the switch to find a specific MAC-adress."""
        if (mac_address == self.switch_mac_address):
            return self.cl_switch_interface(-1, mac_address)
        
        for iface in self.interface_list:
            for _mac in iface.mac_address:
                if (_mac == mac_address):
                    self.mac_found_at_interface = iface.interface

    def append_mac_to_interface(self, interface, macaddress):
        """
        function append_mac_to_interface\n
        a function to add mac-address to a specific interface. if interface not found add new interface and add the mac_address to it.\n
        """
        if_found = False #control over if the interface is found.
        for intf in self.interface_list: # loop through the inteface list to find the specific interface.
            if (intf.interface == interface): #check if interface number matches, if so add the mac-address.
                intf.mac_address.append(macaddress)
                if_found = True
        if (if_found == False): # if interface not found add the new interface and the mac-address to the interface.
            self.interface_list.append(self.cl_switch_interface(interface, macaddress))

    def append_neighbor(self, interface, *args):
        """
        function append_neighbor\n
        function to append Neighbor to the switchobjects array och neighbors.\n
        """
        
        exists = False
        for a in self.switch_neighbors:
            if (a.interface == interface):
                exists = True
        if not exists:
            self.switch_neighbors.append(self.cl_switch_neighbors(interface))
        
        for a in self.switch_neighbors:
                if (a.interface == interface):
                    if (args[0] == "name"):
                        a.name = args[1]
                    elif (args[0] == "remote_interface"):
                        a.remote_inteface = args[1]
                    elif (args[0] == "ip_address"):
                        a.ip_address = args[1]
        
        
        
    def get_mac_address_list(self):
        """
        function get_mac_address_list\n
        Does a SNMP-request to gather the mac-address-table from this switch-object.\n
        """
        errorIndication, errorStatus, errorIndex, varBindTable = self._do_snmp_request('mac_interface')
        if (not errorStatus):
            exit                    ## This should be a Raise statement.
        for row in varBindTable:
            hx = row[0][1]
            val = row[1][1]
            mys=str(hx).encode('hex')
            if (len(mys) > 5 and val != 0):
                self.append_mac_to_interface(int(val), mys)

    def is_interface_a_neighbor(self, interface):
        """
        function is_interface_a_neighbor\n
        Check to see if the interface has neighbors registered.\n
        Returns True or False
        """
        for a in self.switch_neighbors:
            if (int(a.interface) == int(interface)):
                return True
        return False

    def get_neighbor_at_interface(self, interface):
        """
        function get_neighbor_at_interface\n
        function to get the neighbor at a specific interface.\n
        searches registered neighbors and returns a hit.\n
        """
        for a in self.switch_neighbors:
            if (int(a.interface) == int(interface)):
                return a

    def get_interface(self, interface):
        """
        function get_interface\n
        searches registered interfaces and returns the interface_object\n
        """
        for a in self.interface_list:
            if (int(a.interface) == int(interface)):
                return a

    def get_neighbors(self):
        """
        function get_neighbores\n
        gets the list of neighbors and stores them in the list 'switch_neighbors'\n
        """
        errorIndication, errorStatus, errorIndex, ResultTable = self._do_snmp_request('neighbors')
        errorIndication2, errorStatus2, errorIndex2, ResultTable2 = self._do_snmp_request('neighbors_ip')

        if (not errorStatus):
            exit
        name = ""
        for row in ResultTable:
                oid = (str(row[0][0]).strip('()')).split(', ')
                res = str(row[0][1])
                if (len(oid)>10):
                    if (int(oid[10]) == 8):
                        self.append_neighbor(oid[12], 'remote_interface', res)
                    if (int(oid[10]) == 9):
                        self.append_neighbor(oid[12], 'name', res)
        for row in ResultTable2:
                oid = (str(row[0][0]).strip('()')).split(', ')
                res = str(row[0][1])
                if (len(oid)>10):
                    if (int(oid[10]) == 3):
                        ip_add = "%s.%s.%s.%s" % (oid[-4], oid[-3], oid[-2], oid[-1])
                        iface = oid[12]
                        self.append_neighbor(iface, "ip_address", ip_add)
   
    def _do_snmp_request(self, request):
        """
        private function _do_snmp_request\n
        @param request\n
        request can be one of the following\n
             \tneighbors\n
             \tneighbors_ip\n
             \tbase_mac_adress\n
             \tmac_interface\n
             \tsystem-name\n
        """
        
        if (request == 'neighbors'):
            return cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('public', 'public', 0),
            cmdgen.UdpTransportTarget((self.switch_ip_address, 161)),
            (1,0,8802,1,1,2,1,4,1)
            )
        elif (request == 'neighbors_ip'):
            return cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('public', 'public', 0),
            cmdgen.UdpTransportTarget((self.switch_ip_address, 161)),
            (1,0,8802,1,1,2,1,4,2,1,3)
            )
        elif (request == 'base_mac_address'):
            return cmdgen.CommandGenerator().getCmd(
            cmdgen.CommunityData('public', 'public', 0),
            cmdgen.UdpTransportTarget((self.switch_ip_address, 161)),
            (1,3,6,1,4,1,11,2,14,11,5,1,1,6,0)
            ) #1.3.6.1.4.1.11.2.14.11.5.1.1.6.0
        elif (request == 'mac_interface'):
            return cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('public', 'public', 0),
            cmdgen.UdpTransportTarget((self.switch_ip_address, 161)),
            (1,3,6,1,2,1,17,4,3,1,1),
	    (1,3,6,1,2,1,17,4,3,1,2)
            )
        elif (request == 'system-name'):
            return cmdgen.CommandGenerator().getCmd(
            cmdgen.CommunityData('public', 'public', 1),
            cmdgen.UdpTransportTarget((self.switch_ip_address, 161)),
            (1,3,6,1,2,1,1,5,0)
            )
        else:
            return "", "", "", ""
