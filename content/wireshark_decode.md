Title: Decoding AireOS monitor mode captures on Wireshark
Date: 2023-05-28 12:00
Category: 802.11

I am writing this blog post mostly for my own future reference, and while it 
will be nice and short, I hope it will save a few minutes to other
troubleshooters on the web.

I recently had to analyse the over-the-air traffic for a customer of mine, and
they used used a Cisco AireOS Lightweight AP (LAP) for their monitor mode captures.
Captures taken either on specialised sniffers or repurposed clients (e.g.
MacBooks or Raspberry Pi boxes with Kali Linux) do not require any special 
handling when opened with Wireshark and you would see the list of frames
immediately.

On the other hand, AireOS went down a different path and its captures require 
specialised decoding. This is due to the fact that the wireless frames are
encapsulated within packets from the LAP to the Wireless Lan Controller
(WLC) from UDP port 5555. The following screenshot shows what you would be able
to see when opening such kind of captures in Wireshark.

<center>
    ![AireOS capture in Wireshark]({static}/images/aireos_encoded_pcap/not_decoded_aireos.png)
</center>

As for many things in radio communications, the packets in question can be 
**decoded** using an appropriate interpretation method. Wireshark comes with a 
built-in tool found in the topbar under **Analyze > Decode As...** as showed in
the screenshot below.

<center>
    ![AireOS capture in Wireshark]({static}/images/aireos_encoded_pcap/adding_new_decode_rule.png)
</center>

Clickig in the + (plus) button, a new decode rule will be added to the list above.
You will need to insert the following decoding parameters:
- Field: UDP port
- Value: 5555
- Type: Integer, base 10
- Default: SIGCOMP
- Current: PEEKREMOTE

<center>
    ![AireOS capture in Wireshark]({static}/images/aireos_encoded_pcap/decode_rule.png)
</center>

After making sure that the values inserted are correct, click the "OK" button
and the list of frames in Wireshark will immediately change to reflect
the actual content of the monitor mode capture as below.

<center>
    ![AireOS capture in Wireshark]({static}/images/aireos_encoded_pcap/decoded_aireos.png)
</center>

### Referencesp
- “Analyze and Troubleshoot 802.11 Wireless Sniffing.” 
   Cisco Systems, Nov. 2022, https://bit.ly/43c7lAT. Accessed 28 May 2023.



