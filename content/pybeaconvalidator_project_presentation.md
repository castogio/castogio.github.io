Title: PyBeaconValidator: a project idea
Date: 2023-07-26 12:00
Category: 802.11

I have recently completed a one-week course on advanced Python programming, and
wanted to make something useful with the newly acquired knowledge to simplify
the management of my wireless laboratory.

I created the first iteration of **PyBeaconValidator**, a CLI program that can 
parse monitor mode packet captures, select the Beacon management frames, extract
the content of their Information Elements, and match them with the
configuration specified on the Cisco Meraki Dashboard. The program allows to 
validate if the AP is operating as per its configuration without opening the
Dashboard webpage. This is very helpful in my laboratory when conducting 
experiments as the APs may not fetch new configurations due to the lack of
Internet reachability or otherwise operate incorrectly due to a defect. As a 
side-effect, the program could also confirm if the Beacons are being spoofed.

The readers can find the GitHub repository at
[this link](https://github.com/castogio/pybeaconvalidator). The project is 
at a very early stage, but it already has all the components that will be used
for the "usable" version. The program is released as a _Free/Libre Software_ 
with a [GNU GPLv3 software license](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Forewords

PyBeaconValidator heavily relies on the Cisco Meraki API for accessing the
configuration of the APs on the Dashboard. Having access to a working Dashboard,
administrators can enable the API access under **Organization > Settings > Dashboard API access** 
by selecting the tickbox. After enabling the API, an API
key (i.e. an access token) can be created under **My Profile**. More information
can be found at [this link](https://documentation.meraki.com/General_Administration/Other_Topics/Cisco_Meraki_Dashboard_API).

The user needs to have the following dependencies installed from PyPI:
- The [dashboard-api-python by Cisco Meraki](https://github.com/meraki/dashboard-api-python), 
  which provides all the current Dashboard API endpoints.
- [pypacker](https://gitlab.com/mike01/pypacker) a very slim low-level packet
  manipulation library for Python.

The program requires the use of Python 3.11 (or superior) to work correctly, and
I encourage using a virtual environment, such as **pipenv** (used for the project)
or __poetry__ for better handling of the dependencies. Using pipenv the install 
procedure looks like the following:

    :::bash
    cd <PATH-TO-PROJECT>/pybeaconvalidator
    pipenv --python '3.11' # create pipenv environement
    pipenv install meraki
    sudo apt install python3.11-dev
    pipenv install pypacker netifaces
    pipenv shell # enable pipenv environment

I am developing the tool on a Trisquel GNU/Linux-libre machine (x86_64).
I intend to test the tool on Apple macOS down the line and, potentially, adapt
it to Microsoft Windows.

## High-level Program Workflow

The idea behind the project is fairly simple, so I wanted the user workflow
to be simple as well.

The user needs to know their API key as described previously and it should
specified in the program shell environment as follows:

    :::bash
    export MERAKI_DASHBOARD_API_KEY=<your-api-key> 

PyBeaconValidator also assumes the user captured a monitor mode packet capture to be
analysed in _.pcap_ format, for instance, taken on a MacBook using the wireless
sniffer tool. I decided not to integrate the capture function into the program as 
it would increase the complexity and often the wireless network card of the
host machine would not be able to take monitor mode pcaps anyway.

Once the above is cleared, PyBeaconValidator executes the following steps:

1. The program reads the Cisco Meraki Network ID from the program arguments; the same
   is done to the path to the capture file.
2. The program retrieves the details of the APs in the wireless network, such as the name,
   serial number, model, MAC address, and tags.
3. The program retrieves the BSSID data for each AP. The information will be matched with
   the Transmitter Address (TA) of the Beacons so that the program can identify
   which unit is broadcasting the frame.
4. The program retrieves the configuration for all the SSIDs in the network. The Cisco
   Meraki Dashboard allows configuring up to 15 SSIDs at the time of this post.
5. The program parses the packet capture, filtering the Beacon management frames only and
   extracting their information, such as the TA, the channel (from the RadioTap 
   header), the SSID name, and the Supported Rates Information Element (IE).
   The extracted IEs are ones I need at the moment, but more might be added in the
   future, feel free to contribute on GitHub.
6. The program creates a list of pairs for each network configuration containing
   the _expected_ value as configured on Dashboard and the _actual_ value
   advertised in the beacon frames in the packet capture.
7. If there is a mismatch between the expected and the actual value,
   the program alerts the user with a warning on the screen.

The sequence diagram below shows the high-level workflow described previously:

<!-- 
@startuml PyBeaconValidator
actor User as u #red
participant PyBeaconValidator as pr 
participant "Cisco Meraki Cloud" as mc #LightGreen
database "FileSystem" as fs

u->pr: network_id, pcap_path
pr->mc: get_all_aps(network_id)
pr<--mc: list[access_point]
loop for each access_point
    pr->mc: get_all_bssids(access_point)
    pr<--mc: list[bssid]
end
pr->mc: get_all_ssid_config(network_id)
pr<--mc: list[ssid_config]
pr->fs: read_file(pcap_path)
pr<--fs: pcap_file
pr->pr: parse pcap_file
pr->pr: compare(expected, actual)
u<--pr: show mismatches
@enduml
-->

![PyBeaconValidator sequence diagram]({static}/images/pybeaconvalidator_presentation/pybeaconvalidator_seq_diagram.png)

## Exemple of execution

The User Interface of PyBeaconValidator in this first iteration is still fairly
minimal; however, it allows to execute test runs for debugging quite easily
with minimal user interaction as the commands can be issued automatically by
programming editors such as VSCodium or Vim. You can run the program from
the shell as follows:

![PyBeaconValidator command]({static}/images/pybeaconvalidator_presentation/running_program.png)

At the moment, the output is silent if there is no mismatch. I created an
"artificial" mismatch by blocking the traffic from the APs to the Cisco Meraki
Cloud using a firewall and then changing the _minimum_ (basic) bitrate configuration.
As shown in the screenshot below, the program shows a _WARNING_ log for the
mismatch containing the timestamp (ts) of the beacon in the file, the Serial
Number (sn) of the AP in question, the BSSID and the expected vs. actual (seen)
values for the bitrate:

![Minimum bitrate mismatch warning]({static}/images/pybeaconvalidator_presentation/output.png)

## Frame processing insights

I selected _pypacker_ as the capture parser among other alternatives as it seems 
to be the fastest library available at the moment. I gave a go to
[pyshark](https://github.com/KimiNewt/pyshark), which is a Python wrapper for
[tshark](https://man.archlinux.org/man/tshark.1), but it was unbearably slow
even for small captures.

The following code snippet shows how the beacons are extracted from the capture 
file in the program when using Pypacker:

    :::python
    from pypacker import ppcap
    from pypacker.layer12 import radiotap, ieee80211

    ...

    beacons = list()
    with ppcap.Reader(capture_file_path) as capture_reader:
        for ts_ns, buf in capture_reader:

            # all the frames in the .pcap file are incapsulated into Radiotab
            frame = radiotap.Radiotap(buf) 

            # decapsulate the Radiotap, IEEE802.11 header and the Beacon payload
            radiotap_header, dot11_header, beacon_payload = frame[None, 
                                                                  ieee80211.IEEE80211, 
                                                                  ieee80211.IEEE80211.Beacon]

            # the frame is not a Beacon, the payload is None
            if beacon_payload is None:
                continue # skip frame and go to the next one

            # extract all required the fields from the Beacon frame
            beacon_frame = _process_pypacker_frame_headers(radiotap_header,
                                                           dot11_header, 
                                                           beacon_header, ts_ns)
            beacons.append(beacon_frame)

Despite the conceptual simplicity of Pypacker's programming interface, it
offloads much of the responsibility of parsing of the raw byte content of the IEs
to the programmer. This behaviour gives more freedom to the programmer, but
it increases the difficulty in analysing the most common IE, such as the
Supported Rates. As you can see in the snippet below the computation required on
the byte octets in the IE (each one refers to a supported rate):

    :::python
    supported_rates_ie = beacon_header.params[1]
    for b in supported_rates_ie.body_bytes:

        # check if the bitrate value refers to a BASIC bitrate by checking the
        # first bit of the octect e.g. 1000 0000 --> Basic Bitrate
        is_mandatory = bool(b >> 7) 

        # compute bitrate in Mbps by multiplying octect
        # remove if 1st bit in case of mandatory bitrate
        # bitrate = (octect * 500 kbps) // 1000
        bitrate = ((b - (1 << 7)) if is_mandatory else b) // 2

## Frame processing insights

This project is still at a very early stage and I intend to go ahead adding
more and more features over time. I consider it a great opportunity to get
hands-on experience with frame processing and learn more about network
automation in Python. PyBeaconValidator is freely available on GitHub so the
readers can download the source code, study it, modify and redistribute their
copies.

## References

- “Meraki Dashboard API Python Library”, 
   Cisco Meraki, GitHub, https://github.com/meraki/dashboard-api-python. 
   Accessed 16 July 2023.

- “pypacker”, Michael Stahn, GitLab, https://gitlab.com/mike01/pypacker. 
   Accessed 16 July 2023.


