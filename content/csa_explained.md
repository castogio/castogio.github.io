Title: Channel Switch Announcements explained
Date: 2023-05-08 00:01
Category: 802.11

In this article, I would like to describe what I believe is an interesting 
mechanic of dot11 wireless networks called _Channel Switch Announcement_ (CSA). 
This is often overlooked as it usually works pretty much flawlessly, but it is
pretty much ubiquitous in today's deployments because admins
use automatic Resource Radio Management (RRM), which may prompt for 
(frequent) channel changes on the Access Points as they adapt to the surrounding
RF environment. CSAs are also used whenever a Dynamic Frequency Selection (DFS)
occurs in the 5 GHz band, and the AP must move to a non-radar channel.

The primary goal of CSAs is to allow the AP to change its channel, while keeping
the clients associated. Of course, the clients have to follow the AP along with 
the change, and start transmitting on the new channel (they may actually decide
to simply disassociate).

We will explore together the CSA procedures and the Information Element (IE) 
formats as defined in the IEEE802.11-2020 standard, and confirm the behaviours
in two Case Studies for DFS-triggered and RRM-triggered channel switches.
Please note that this blog post specifically describes the case of APs in a 
Basic Service Set (BSS).

## How channel switches are announced

First, we need to clarify where the AP puts Channel Switch Announcements. 
These CSAs are carried by the _CSA Information Element_ (IE) and the _Extended_
_CSA IE_ in the following types of frames right before the change is operated:

- **Beacon Management Frames** (Wireshark filter: wlan.fc.type_subtype == 8).
- **Probe Responses** (Wireshark filter: wlan.fc.type_subtype == 5).
- **Spectrum Management Action Frames** (Wireshark filter: wlan.fc.type_subtype == 13).

You can see an exhibit from Wireshark showing a sequence of Beacon frames and
an Action frame before a channel switch from Ch 112 to Ch 48.

<center>
    ![CSAs frames in Wireshark]({static}/images/csa_explained/wireshark_list_frames.png)
</center>

All these frames are _broadcast_ and they carry information regarding what the
_new channel_ will be, and they state how much time is left before the switch, 
expressed as a multiplicative factor of the 
TBTT (Target Beacon Transmission Time). 
I made sure the picture shows them  in a human-friendly format by re-naming the 
columns, but we will deep dive into the details of the IE in the next sections.

## CSA Information Element format

When it comes to Information Elements, the best place where to find clear
information is the standard paper itself, so this section takes heavily from
**IEEE 802.11-2020 Section 9.4.2.18**. The following figure shows the Channel
Switch Announcement IE format as defined in the standard to "advertise when [an 
AP] is changing to a new channel and the channel number of the new channel."
 This IE was introduced in the IEEE 802.11h amendment.

<center>
    ![CSA element format]({static}/images/csa_explained/csa_ie_format.png)
</center>

The following fields are defined:

- The _Element ID_ (1 byte) is 37.
- The _Channel Switch Mode_ Field (1 byte) can assume the value _0_ when the 
  client stations and the AP itself can continue exchanging frames before the
  channel switch happens. If the value is _1_, no more frames should be
  exchanged before the switch.
- The _New Channel Number_ field (1 byte) is the channel that will be used
  by the AP after the switch (you could call it the "new channel").
- The _Channel Switch Count_ field (1 byte) is tricky as it states how much
  time will elapse before the channel change, and it is expressed in multiples 
  of the TBTT, which is the target amount of time between a Beacon Frame and the 
  following one for the same BSS (assuming the medium is available). A TBTT is 
  composed of 100 Time Units (TUs), which in turn is 1024 
  microseconds. The Channel Switch Count value _1_ means that the AP will
  broadcast the next Beacon frame and continue operating in the new channel.
  Value _0_ indicates that the actual switch will happen _at any time_ after the 
  current frame is broadcasted (i.e. the clients may want to switch immediately
  to be prepared).


## Extended CSA Information Element format

**IEEE 802.11-2020 Section 9.4.2.52** defines the Extended Channel Switch
Announcement IE (E-CSA IE), which specifies if the "BSS is changing to a new 
channel in the same or a new operating class." This IE was first introduced in 
the IEEE 802.11y amendment to replace the CSA IE. The latter is still 
broadcasted for backward compatibility.

<center>
    ![Extended CSA element format]({static}/images/csa_explained/extended_csa_ie.png)
</center>

This IE carries almost the same information as the CSA IE, so we will focus on 
a subset of them, which are particularly interesting and justify the existence 
of the Extended CSA element:

- The _Element ID_ (1 byte) is 37.
- The _New Operating Class_ (1 byte) field specifies the new operating class
  after the channel switch happens. The values for classes are defined in 
  "Annex E" of the standard, they depend on the Regulatory Domain as specified 
  in the Country Element (Section 9.4.2.8), and they indicate the frequency of 
  the channel, the channel centre frequency, the maximum channel width, and 
  other behavioural constraints.

## Case Study: DFS-triggered channel changes

The standard is quite dry, so I recreated the conditions of a channel switch by 
simulating a DFS event in my lab network to observe what values populated the 
fields we described in the previous sections.

My AP was operating on channel 112, which falls in the 
Unlicensed National Information Infrastructure 2 Extended (U-NII-2e) range, and 
it might be affected by DFS events. These events can be caused by radars or any
other RF radiator mimicking radar. If an event is detected the AP must inform
the clients that they have to stop transmitting and move to a different channel,
usually referred to as a "mute" or "fallback" channel. The AP
and the clients have 10 seconds to leave the DFS channel.

<center>
    ![Captured CSA IE values for DFS]({static}/images/csa_explained/channel_switch_announcement_information_element.png)
</center>

As you can see in the figure above, the CSA IE states that the new channel is 
48 (a non-DFS channel in the U-NII-1 range), the switch will happen in 5 TBTTs,
and the _clients should not transmit any more frames over the current channel_.
The latter command is unsurprising, and it perfectly aligns with the 
DFS requirement.

The AP can send one or more CSA frames in the form of Beacons, Probe Responses 
and Action Frames to make sure that all its clients move and keep 
their association status.

<center>
    ![CapturedExtended CSA IE for DFS]({static}/images/csa_explained/extended_channel_switch_announcement_information_element.png)
</center>

The E-CSA field is contained in the same frames and it carries similar 
information with the addition of the "New Operating Class" equal to 0x01 
(hexadecimal). In Europe where I live, class 1 means that the new channel 
belongs a group composed of Channels 36, 40, 44, and 48 (i.e U-NII-1), the 
starting frequency for the group is 5 GHz, their channel spacing is 20 MHz, and
there are no additional behaviour limits (refer to Table E-2 from the standard).

## Case Study: RRM-triggered channel changes

Channel changes due to automatic RRM are another very interesting case study,
probably more relevant than the DFS one, as RRM can kick in very frequently 
when the RF environment is particularly harsh (e.g. high channel utilisation).

<center>
    ![Captured CSA for RRM Channel Change]({static}/images/csa_explained/csa_channel_change.png)
</center>

The figure above shows both the CSA and E-CSA IEs when the channel is about to 
switch to 161. The new operating class is 0x11 (hex for 17), which in Europe 
refers to the channel set containing 149, 153, 157, 161, 165, and 169 (also
known as U-NII-3).
Furthermore, note that the Channel Switch Mode is set to 0 so the 
clients and the AP may keep exchanging frames until the channel switch, hence 
virtually nullifying (or minimising as much as possible) any service 
interruptions during RRM channel switches.

## References
- IEEE 802.11-2020: Wireless LAN Medium Access Control (MAC) and Physical Layer 
  (PHY) Specifications (2020 revision), IEEE-SA, 2021
- Coleman, David D., and David A. Westcott. CWNA Certified Wireless Network 
  Administrator Study Guide: Exam CWNA-107. John Wiley & Sons, 2018.
