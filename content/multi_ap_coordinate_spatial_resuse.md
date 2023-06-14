Title: R&D sneak peek: Multi-AP Coordinated Spatial Reuse for Wi-Fi 8
Date: 2023-06-14 18:00
Category: 802.11

In this post, I would like to describe an interesting take on Multi-AP 
Coordination (MAPC) leveraging Spatial Reuse (SR). AP coordination has groups of
APs communicate with each other to minimise collisions while transmitting at the
same time and on the same frequency channel. I recently came across a scientific
article by David Nunez et al. in [1], which I believe is worth understanding as it
proposes an algorithm to identify coordinated AP groups and schedule
transmissions of their buffered frames at the same time.

## What is Spatial Reuse?

Spatial Reuse is not a new concept in wireless communications. If a transmitter
is “distant” enough from other transmitters on the same channel, it can consider
them as background noise when communicating with its intended clients. Think
about yourself speaking in English to an audience in a large garden. Other
people can do the same 20 yards away from yours and each other’s groups if
everyone agrees to be well-behaved. Communication is possible because sound is
affected by Path Loss; the same can be applied to 802.11 wireless communication
when considering a model such as the TGax model for Enterprise Scenarios [2]
which takes into account the distance between the transmitter and receiver, the
frequency used and the number of walls. The mathematical details are not
interesting for understanding the concept, but you may appreciate how being in a
harsh RF environment causing strong attenuation can reduce the reuse distance.
The picture below shows a client station, called STA, being able to hear 
AP<sub>4</sub> and AP<sub>5</sub> on the same channel used by AP<sub>2</sub>
to which it is connected.

<center>
    ![Spatial Reuse cells and co-channel interference]({static}/images/mapc_sr/spatial_reuse_cells.png)
</center>

AP4 and AP5 are interferers and contribute to the effect of background noise in
the communications from AP<sub>2</sub>, potentially preventing STA from
receiving readable signals. The effect of background noise and interference over
the useful signal is described by the following formula for the Signal to
Interference plus Noise Ratio (SINR) as seen on the client STA for the
transmission from AP<sub>2</sub>:

<!-- SINR_{STA}^{2} = \frac{P_2}{N + \sum_{j \neq 2} P_{j}} -->
<center>
    ![SINR formula]({static}/images/mapc_sr/sinr_formula.png)
</center>

where P<sub>2</sub> and P<sub>j</sub> are the received power from AP<sub>2</sub>
and the other _j_ APs as seen from STA respectively, and N is the noise power. 
We cannot alter the _N_ value as it is due to external factors in the
environment beyond our control (e.g. the APs of a neighbouring office),
so we should keep the sum of the P<sub>j</sub> as low as possible. 
The obvious course of action is not to have APs with higher interference power
transmit at the same time as AP<sub>2</sub>.
We face a new problem: how do we select the group of APs that can transmit at
the same time as AP<sub>2</sub>?

## Detecting Coordinated Groups for SR

The paper defines a “_Sharing AP_” as the coordinator for a group of
“_Shared APs._” They also assume that all the APs are within the coverage area
of the Sharing AP, which can access the medium and send a 
Multi-AP Request-To-Send (MAP-RST) to reserve the channel. In case of no
collisions on their side, the Shared APs reply with a MAP Clear-To-Send
(MAP-CTS), guaranteeing that the clients in the service area will stay silent
for the rest of the Transmit Opportunity Sharing (TXOP-sharing) transmission.
Once the Sharing AP can access the channel, the shared TXOP is divided into one
or more coordinated temporal slots. It also signals which APs should transmit
during each slot with a MAP Trigger Frame (MAP-TF).
Effectively the authors leverage _Time Division Multiple Access_ (TDMA)
as they have the Sharing AP reserving the channel, and they enhance it with SR
by selecting only transmitters that interfere the least.

<center>
    ![TXOP-sharing period]({static}/images/mapc_sr/TXOP_sharing_breakdown.png)
</center>

To create groups of APs that can transmit together, the authors define a Central
Controller (CC) that knows all the received powers P<sub>j</sub> as seen from
the STA and can compute the SIND for each AP. They assume that the RF channel
is always symmetric so that the power the client receives in transmissions from
the AP (downlink) is the same as the AP receives from the client on the way back
(uplink). In light of this, all the APs in the same coordinated group of size
M must guarantee that their SINR for each of their connected client STAs is
above an m threshold, so that:

<!-- \min_{j=1...M}SINR_{STA}^{j} \geqslant m -->
<center>
    ![SINR formula]({static}/images/mapc_sr/min_sinr_formula.png)
</center>

The APs within the same group of K units are identified using a 
[“greedy” strategy](https://en.wikipedia.org/wiki/Greedy_algorithm) called the 
“_At-most-K_” algorithm. An AP is selected as a reference, and on each iteration
a new AP is added if the formula described above holds and the SINR is still
high enough for all the client STAs connected to APs already in the group.

## Traffic Scheduling Algorithms

The operation can be repeated using different reference APs so that multiple
groups of “compatible” APs can be found. APs that are located in better
positions (or trivially far enough) may end up belonging to multiple groups.
Once the groups are identified, the CC must select what groups should transmit.
The paper proposes four strategies based on the number of packets buffered in
the APs of the group:

1. _NumPkSingle_: the CC selects the groups containing the AP with the highest 
   number of buffered packets, and then picks the single group with the highest 
   number of buffered packets across all the APs in the group.
2. _NumPkGroup_: the CC selects the group with the highest number of packets.
3. _OldOkSingle_: the CC selects the groups containing the AP with the oldest
   buffered packet, and then picks the single group with the highest aggregate
   group delay as a sum of the waiting times of the oldest buffered packets
   across all the APs in the group.
4. _OldPkGroup_: the CC selects the group with the highest aggregate group delay.

The algorithms prevent starvation between groups when using NumPkGroup and 
OldPkGroup by dividing the aggregated value by the number of APs in the groups;
this is particularly important whenever there are groups with just a few APs and
others with a large number of units. The simulation results presented in the
paper show that NumPkSingle and OldOkSingle (_per-AP selection_) outperform the
other strategies (_per-Group selection_) when the TXOP-sharing transmissions are
scheduled every 5 milliseconds and the SINR threshold is 20 dB, high enough to
guarantee the use of a high Modulation and Coding Scheme (MCS) in the simulation
using 9 APs transmitting on the same channel.

## Wrapping up

MAPC is still a hot topic for research, and commercially-available APs will
probably use some still-unknown solution. I hope this blog post picked the
readers’ interest in what is coming in the future iterations of IEEE 802.11,
probably in 8/10 years.

## References
1. Nunez, David, Malcom Smith, and Boris Bellalta. 
"_Multi-AP Coordinated Spatial Reuse for Wi-Fi 8: Group Creation and Scheduling._"
arXiv preprint arXiv:2305.04846 (2023).
2. Merlin, Simone, et al. "_TGax simulation scenarios._" IEEE802 (2015): 11-14.
