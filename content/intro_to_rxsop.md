Title: Introduction to RX-SOP Configuration 
Date: 2023-05-01 12:00
Category: 802.11

The Cisco Receiver Start of Packet Detection Threshold (RX-SOP) is 
a feature available on a multitude of enterprise access points, but experience 
taught me junior wireless engineers often misunderstand it.

In a sentence, the RX-SOP configuration declares the Wi-Fi power required for an 
access point to pick up signals, demodulation and then start decoding the 
physical layer protocol data unit (PPDU). 
This definition begs the question: why is such a feature required?
Having a clear picture of how signal decay 
over distance is necessary to understand the implications of RX-SOP.
​
## RF propagation refresher
​
We call an "isotropic radiator" an intentional radiator (IR) with no spatial 
dimensions (i.e. a dot) in the infinite void, emitting a wave
signal of amplitude P(tx) in all directions. This entity is, of course, ideal,
and it cannot be implemented in real life, but it will help us describe
the behaviour of radiation moving through space. 

<!-- The power emitted is maximum at the IR and equal to P(tx).  -->
A receiver at a distance _d_ for the IR would see a different power level 
_strictly less_ than P(tx), as the transmitted amount spreads 
to all directions; we can name the received power P(rx).
In the case of an isotropic IR, we can easily compute P(rx)
as the power spreads over a spherical wavefront.
The _power density I_ at a distance _d_ on a punctiform section of the sphere
is defined as follows:
​
<!-- I = \frac{P_{tx}}{2\pi d^{2}} -->
<center>
    ![transmit power density formula]({static}/images/rxsop_intro/power_density_formula.png)
</center>

In other words, the value "I" represents how the transmitted power distributes 
in a point at a distance _d_ from the IR. It also lets us compute how much power 
P(rx) can be captured by a punctiform section of the receiving antenna. 

Multiplying _I_ by the _effective area_ of the antenna will
give us the total received power. The effective area depends on the directivity 
of the receiving antenna in general. However, when the receiver is far away from 
the transmitter (at least two or three times the wavelength _lambda_), it can be 
[proven](https://bit.ly/40WJMdj) that:
​
<!-- P_{rx} = I A_{eff} = \frac{P_{tx}}{2\pi d^2}A_{eff} = 
    P_{tx} (\frac{\lambda}{2 \pi d})^2  = FSPL(d) * P_{tx}
-->
<center>
    ![received power formula]({static}/images/rxsop_intro/received_power_formula.png)
</center>
​
As you can see from the above, the distance _d_ contributes significantly to
the power loss in ideal conditions. We call this effect the Free 
Space Path Loss (FSPL). At a distance of 1 m from the IR, regardless of the
transmitted power, P(rx) is approximately 40%
less than the transmitted power. The figure below shows the decay of the 
received power for varying values of the distance _d_ when the transmit power 
P(tx) = 30 dBm and the lambda = 6 cm (frequency = 5 GHz) are set:

<center>
    ![rx power delay FSPL]({static}/images/rxsop_intro/fspl_grapth.png)
</center>
​
What we described superimposes to other detrimental effects, 
(such as material absorption) which are effectively multiplicative factors in 
the formula for P(rx) and it makes the curve decay faster.

​
## RX-SOP operations
​
Having a clearer picture of the harshness of the RF environment, the receiver 
needs to detect between actual signals, which intensity may be comparable to a 
whisper in a noisy environment. This is when RX-SOP comes into play.

There is a power level called "sensitivity," which is the signal strength 
(expressed in dBm) of the weakest signal that the AP can distinguish from 
the background noise and process successfully.
RX-SOP does not alter the sensitivity of your access point. On the other hand, 
changing the RX-SOP level forces the AP to _actively ignore_ signals below a 
specific power in dBm. For instance, Cisco Meraki APs use -95 dBm by default when
enabled on the Dashboard.

<center>
![meraki rx-sop default]({static}/images/rxsop_intro/meraki_rx_sop_default.png)
</center>


The described concept may sound familiar to those of you who are amateur radio
operators, as this is a form of 
"[carrier squelch](https://en.wikipedia.org/wiki/Squelch)", 
i.e. suppressing the receiver output if the input signal is not strong enough. 
You can see the effects of RX-SOP muting when the level is set to -70 dBm:
​
<!-- SEQUENCE DIAGRAM
    @startuml
    Client -[#green]> AP: frame received at -60 dBm (> -70 dBm)
    AP -[#green]> AP: PROCESSED
    Client -[#green]> AP: signal -50 dBm (> -70 dBm)
    AP -[#green]> AP: PROCESSED
    Client -[#red]> AP: signal -75 dBm (< -70 dBm)
    Client -[#red]> AP: signal -71 dBm (< -70 dBm)
    Client -[#red]> AP: signal -80 dBm (< -70 dBm)
    @enduml
-->

<center>
    ![RX-SOP operatiomns]({static}/images/rxsop_intro/rx_sop_operation.png)
</center>
​
Quoting from the Cisco documentation, this feature is "ideal for high-density environments [...]
where there are a large number of client devices connected per AP [... where
...] the smaller the cell size, the better."
​
The benefit might come from the fact that the AP will not reset its 
Network Allocation Vector (NAV) timer when receiving a signal below the 
threshold so that it can start transmitting relatively more frequently.
​
I saw this configuration altered in the wild by inexperienced administrators and 
troubleshooters without properly validating its effect on the environment,
primarily to address the issue of sticky clients. The latter is not advisable:
the RX-SOP is a receive-only configuration, and it applies **only** to the AP
side, while the client will continue receiving transmissions from the AP
as if nothing changed. The client may send a frame using its estimated 
"correct" power level for the AP to receive, while the AP ignores
the frame as the received signal strength is not above the set threshold. This
behaviour may lead to excessive retransmissions and client disconnections in
the worst scenarios, especially at the boundary of the cell coverage where the
asymmetry may be felt the most.
A better result in reducing _bidirectionally_ the cell size
could have been accomplished by simply reducing the AP transmit power while 
guaranteeing appropriate primary and secondary coverage.
​
## Final remarks
​
Altering the default value of RX-SOP is a risky matter leading to unexpected 
behaviours and interruption of the wireless service if you do not know what
you are trying to accomplish and you do not have a clear picture of the 
mathematics behind signal propagation. 
In general, RX-SOP should not be used without following a well-thought design, 
followed by validation and tuning after the deployment in high-density 
environments with many clients (e.g. auditoriums, stadiums). 

**tl;dr** -- never shoot off the hip when using RX-SOP, do your
homework with the design, and consider first decreasing power to reduce cell
sizes instead.
​
​
​
### Bibliography
- "High Density Experience (HDX) Deployment Guide, Release 8.0." Cisco, 
   Jun. 2015, https://bit.ly/3oTelUe. Accessed 30 Apr. 2023.
- "Free-space Path Loss." Scholarly Community Encyclopedia, 
   Oct. 2022, https://bit.ly/40WJMdj. Accessed 30 Apr. 2023.
- "Receive Start of Packet (RX-SOP)." Cisco Meraki, 
   Oct. 2020, https://bit.ly/41R9xxa. Accessed 30 Apr. 2023.

<!-- https://encyclopedia.pub/entry/31362#:~:text=The%20free%2Dspace%20path%20loss%20(FSPL)%20formula%20derives%20from,%CE%BB%204%20%CF%80%20d%20)%202 -->
<!-- https://www.cisco.com/c/en/us/td/docs/wireless/controller/technotes/8-0/hdx_final/b_hdx_dg_final/high_density_experience_features_added_in_release_8_0.html -->
<!--
https://documentation.meraki.com/MR/Radio_Settings/Receive_Start_of_Packet_(RX-SOP)
-->
​