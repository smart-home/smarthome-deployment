#!/usr/bin/python -u

"""
hcitool lescan clone on steroids

- apt-get install libbluetooth3

- apt-get install python-bluez
- or -
- pip install PyBluez
"""

# based on BLE scanner https://github.com/adamf/BLE/blob/77e2ac5f7d8d247f71e6293e77c4024ac50e9f44/ble-scanner.py
# based on https://code.google.com/p/pybluez/source/browse/trunk/examples/advanced/inquiry-with-rssi.py
# https://github.com/pauloborges/bluez/blob/master/tools/hcitool.c for lescan
# https://kernel.googlesource.com/pub/scm/bluetooth/bluez/+/5.6/lib/hci.h for opcodes
# https://github.com/pauloborges/bluez/blob/master/lib/hci.c#L2782 for functions used by lescan

DEBUG = False

import struct
import bluetooth._bluetooth as bluez
import subprocess
import datetime
import json

LE_META_EVENT = 0x3e
LE_PUBLIC_ADDRESS=0x00
LE_RANDOM_ADDRESS=0x01
LE_SET_SCAN_PARAMETERS_CP_SIZE=7
OGF_LE_CTL=0x08
OCF_LE_SET_SCAN_PARAMETERS=0x000B
OCF_LE_SET_SCAN_ENABLE=0x000C
OCF_LE_CREATE_CONN=0x000D

LE_ROLE_MASTER = 0x00
LE_ROLE_SLAVE = 0x01

# these are actually subevents of LE_META_EVENT
EVT_LE_CONN_COMPLETE=0x01
EVT_LE_ADVERTISING_REPORT=0x02
EVT_LE_CONN_UPDATE_COMPLETE=0x03
EVT_LE_READ_REMOTE_USED_FEATURES_COMPLETE=0x04

# Advertisment event types
ADV_IND=0x00
ADV_DIRECT_IND=0x01
ADV_SCAN_IND=0x02
ADV_NONCONN_IND=0x03
ADV_SCAN_RSP=0x04

ADV_TYPES = {
    0x00: 'ADV_IND',
    0x01: 'ADV_DIRECT_IND',
    0x02: 'ADV_SCAN_IND',
    0x03: 'ADV_NONCONN_IND',
    0x04: 'ADV_SCAN_RSP',
}

packed_bdaddr_to_string = lambda bdaddr_packed: ':'.join('%02X'%i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))

class LEScan():
    def __init__(self):
        subprocess.call(["/usr/sbin/hciconfig", "hci0", "down"])
        subprocess.check_call(["/usr/sbin/hciconfig", "hci0", "up"])

        dev_id = 0
        self.sock = bluez.hci_open_dev(dev_id)
        self.old_filter = self.sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

        self.hci_disable_le_scan()

    def __del__(self):
        self.hci_disable_le_scan()
        self.sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, self.old_filter )

    cleanup = __del__

    def run(self, callback=None, active=False):
        self.hci_le_set_scan_parameters(active)
        self.hci_enable_le_scan()
        self.handle_events(callback)

    def hci_enable_le_scan(self):
        self.hci_toggle_le_scan(0x01)

    def hci_disable_le_scan(self):
        self.hci_toggle_le_scan(0x00)

    def hci_toggle_le_scan(self, enable):
    #        hci_le_set_scan_enable(dd, 0x01, filter_dup, 1000);
    #        memset(&scan_cp, 0, sizeof(scan_cp));
    #        uint8_t         enable;
    #        uint8_t         filter_dup;
    #        scan_cp.enable = enable;
    #        scan_cp.filter_dup = filter_dup;
    #
    #        memset(&rq, 0, sizeof(rq));
    #        rq.ogf = OGF_LE_CTL;
    #        rq.ocf = OCF_LE_SET_SCAN_ENABLE;
    #        rq.cparam = &scan_cp;
    #        rq.clen = LE_SET_SCAN_ENABLE_CP_SIZE;
    #        rq.rparam = &status;
    #        rq.rlen = 1;

    #        if (hci_send_req(dd, &rq, to) < 0)
    #                return -1;

        """
        < HCI Command: LE Set Scan Enable (0x08|0x000c) plen 2
            value 0x01 (scanning enabled)
            filter duplicates 0x00 (disabled)
        > HCI Event: Command Complete (0x0e) plen 4
            LE Set Scan Enable (0x08|0x000c) ncmd 1
            status 0x00

        < 0000: 01 0c 20 02 01 00                                 .. ...
        > 0000: 04 0e 04 01 0c 20 00                              ..... .
        """

        if DEBUG: print "--- toggle scan: ", enable
        FILTER_DUP = 0x00 # Show duplicates
        cmd_pkt = struct.pack("<BB", enable, FILTER_DUP)
        bluez.hci_send_cmd(self.sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)
        if DEBUG: print "--- sent toggle scan"


    def hci_le_set_scan_parameters(self, active=False):
    #        uint8_t         type;
    #        uint16_t        interval;
    #        uint16_t        window;
    #        uint8_t         own_bdaddr_type;
    #        uint8_t         filter;

    #        memset(&param_cp, 0, sizeof(param_cp));
    #        param_cp.type = type;
    #        param_cp.interval = interval;
    #        param_cp.window = window;
    #        param_cp.own_bdaddr_type = own_type;
    #        param_cp.filter = filter;
    #
    #        memset(&rq, 0, sizeof(rq));

    # #define OGF_LE_CTL              0x08
    #        rq.ogf = OGF_LE_CTL;

    # #define OCF_LE_SET_SCAN_PARAMETERS              0x000B
    #        rq.ocf = OCF_LE_SET_SCAN_PARAMETERS;

    #        rq.cparam = &param_cp;
    # #define LE_SET_SCAN_PARAMETERS_CP_SIZE 7
    #        rq.clen = LE_SET_SCAN_PARAMETERS_CP_SIZE;
    #        rq.rparam = &status;
    #        rq.rlen = 1;
    # if (hci_send_req(dd, &rq, to) < 0)

        """
        < HCI Command: LE Set Scan Parameters (0x08|0x000b) plen 7
            type 0x01 (active)
            interval 10.000ms window 10.000ms
            own address: 0x00 (Public) policy: All
        > HCI Event: Command Complete (0x0e) plen 4
            LE Set Scan Parameters (0x08|0x000b) ncmd 1
            status 0x00

        < 0000: 01 0b 20 07 01 10 00 10  00 00 00                 .. ........
        > 0000: 04 0e 04 01 0b 20 00                              ..... .
        """

        if DEBUG: print "--- setting up scan"

        SCAN_RANDOM = 0x01
        SCAN_PUBLIC = 0x00
        OWN_TYPE = SCAN_PUBLIC

        if active: SCAN_TYPE = 0x01 # Active
        else: SCAN_TYPE = 0x00 # Passive

        INTERVAL = 0x10 # 10.000ms
        WINDOW = 0x10 # 10.000ms
        FILTER = 0x00 # All advertisements, not just whitelisted devices

        cmd_pkt = struct.pack("<BHHBB", SCAN_TYPE, INTERVAL, WINDOW, OWN_TYPE, FILTER)
        bluez.hci_send_cmd(self.sock, OGF_LE_CTL, OCF_LE_SET_SCAN_PARAMETERS, cmd_pkt)

        if DEBUG: print "--- sent scan parameters command"

        # pkt = sock.recv(255)
        # print "socked recieved"
        # status,mode = struct.unpack("xxxxxxBB", pkt)
        # print status

    def print_detect(self, bdaddr, rssi, re_type, name=None):
        # msg = datetime.datetime.utcnow().isoformat()
        # msg += ' [%s] [%s] %s' % (bdaddr, rssi, re_type)
        # if name: msg += ' - %s' % name
        # print msg

        print json.dumps({
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'bdaddr': bdaddr,
            'rssi': rssi,
            'type': re_type,
            'name': name
        }, sort_keys=True)

    def handle_events(self, callback=None):
        if callback is None: callback = self.print_detect

        self.old_filter = self.sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

        flt = bluez.hci_filter_new()
        bluez.hci_filter_all_events(flt)
        bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
        self.sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )

        while True:
            pkt = self.sock.recv(255)
            ptype, event, plen = struct.unpack("BBB", pkt[:3])

            if DEBUG: print "-------------- ptype: 0x%02x event: 0x%02x plen: 0x%02x" % (ptype, event, plen)

            if event != LE_META_EVENT: continue

            subevent, = struct.unpack("B", pkt[3])
            pkt = pkt[4:]

            if DEBUG: print "LE META EVENT subevent: 0x%02x" %(subevent,)

            if subevent != EVT_LE_ADVERTISING_REPORT: continue

            if DEBUG: print "advertising report"
            num_reports, = struct.unpack("B", pkt[0])
            report_pkt_offset = 0
            if DEBUG: print "Number of reports in the report: 0x%02x" % num_reports
            for i in range(0, num_reports):
                if DEBUG: print "report", i
                report_event_type = struct.unpack("B", pkt[report_pkt_offset + 1])[0]
                bdaddr_type = struct.unpack("B", pkt[report_pkt_offset + 2])[0]
                if DEBUG: print "\tadvertising report event type: 0x%02x" % report_event_type
                if DEBUG: print "\tbdaddr type: 0x%02x" % (bdaddr_type,)
                bdaddr = packed_bdaddr_to_string(pkt[report_pkt_offset + 3:report_pkt_offset + 9])
                if DEBUG: print "\tdevice address: ", bdaddr
                report_data_length, = struct.unpack("B", pkt[report_pkt_offset + 9])
                if DEBUG: print "\tadvertising packet metadata length: ", report_data_length
                report_event_type_human = ADV_TYPES.get(report_event_type, 'Unknown(%s)' % report_event_type)
                if DEBUG: print "\ttype: ", report_event_type_human

                name = None
                if report_event_type == ADV_SCAN_RSP:
                    local_name_len, = struct.unpack("B", pkt[report_pkt_offset + 11])
                    # TODO: the line below is probably bugged
                    name = pkt[report_pkt_offset + 12:report_pkt_offset + 12+local_name_len].split('\x00')[0]
                    if DEBUG: print "\tname:", name

                # each report is 2 (event type, bdaddr type) + 6 (the address)
                #    + 1 (data length field) + data length + 1 (rssi)
                report_pkt_offset = report_pkt_offset +  10 + report_data_length + 1
                rssi, = struct.unpack("b", pkt[report_pkt_offset -1])
                if DEBUG: print "\tRSSI:", rssi

                callback(bdaddr, rssi, report_event_type_human, name)

def main():
    l = LEScan()
    try:
        l.run()
    except KeyboardInterrupt:
        pass
    l.cleanup()

if __name__ == '__main__':
    main()
