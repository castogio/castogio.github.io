Title: PyBeaconValidator: a project idea
Date: 2023-07-26 12:00
Category: 802.11

I have recently completed a one-week course on advanced Python programming, and
wanted to make something useful with the newly acquired knowledge to simplify
the mangement of my wireless laboratory.

I created the first iteration of **PyBeaconValidator**, a CLI program that can 
parse monitor mode packet captures, select the Beacon management frames, extract
the the content of their Information Elements, and match them with the
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
  manipulation library for Python. I selected, among other alternatives, as it
  seems to be the fastest library when it comes to parsing the capture files and
  it does not rely on 3rd party tools (such as tshark). On the flipside, much
  of the parsing of the field bytes is left for the programmer to do.

The program requires the use of Python 3.11 (or superior) to work correctly, and
I encourage usign a virtual environment, such as **pipenv** (used for the project)
or __poetry__ for better handling of the dependencies. Using pipenv the install 
procedure looks like the following:

    :::bash
    cd <PATH-TO-PROJECT>/pybeaconvalidator
    pipenv --python '3.11' # create pipenv environement
    pipenv install meraki
    pipenv install pypacker
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
analysed in _.pcap_ format, for instance taken on a MacBook using the wireless
sniffer tool. I decided not to integrade the capture function in the program as 
it would increase the complexity and often times the wireless network card of the
host machine would not be able to take monitor mode pcaps anyway.

Once the above is cleared, the program executes the following steps:

1. It reads the Cisco Meraki Network ID from the program arguments; the same
   is done to the path to the capture file.
2. It retrieves the details of the APs in the wireless network, such as the mame,
   serial number, model, MAC address, and tags.
3. It retrieves the BSSID data for each AP. The information will be matched with
   the Transmitter Address (TA) of the Beacons so that the program can identify
   which unit is broadcasting the frame.
4. It retrieves the configuration for all the SSIDs in the network. The Cisco
   Meraki Dashboard allows to configure up to 15 SSIDs at the time of this post.


