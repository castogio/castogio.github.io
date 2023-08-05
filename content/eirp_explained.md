Title: Effective Isotropic Radiated Power (EIRP) explained
Date: 2023-08-05 00:07
Category: 802.11

In this post, I would like to discuss a topic that, surprisingly, has kept
coming over and over in the discussions with my customers: the difference
between the concepts of Transmit (TX) Power and the Effective Isotropic
Radiated Power (EIRP). People tend to confuse the two terms and this
create a lot of headaches when it comes to troubleshooting tickets relating to
poor signal quality.

## Glossary

Let's clarify immediately some of the terms that will show up later in the post:

- **TX Power**: it is the amount of power measured in Watts (W) at the output 
   of a transmitter.
- **Loss/Attenuation**: it is the decrease of strength in a signal propagating
  through a physical medium. An example is Free-Space Path Loss (FSPL) is
  observed at the receiver after the signal propagates through free space
  (normally air) and it increases with the distance between the transmitter and 
  the receiver. Cables and waveguides introduce losses.
<!-- - **Intentional Radiator** (IR): as defined in the FCC Code of Federal
  Regulations (CFR) Part 15, an IR is a device that _intentionally_ generates and
  emits radio frequency energy by radiation or induction. This broad definition 
  is better understood by negation. Something that emits RF
  energy as a byproduct of its internal operations without explicitly being
  designed to do so does not qualify as an IR. An Access Point (AP) is an IR, 
  while a rotating coil generating in a factory causing interference is not an IR. -->
- **Isotropic Antenna**: it is a point antenna transmitting, and receiving, 
  signal equally in all directions. It is impossible to create such 
  an antenna in real life, so we use it as a reference.



## Antenna Gain

The Antenna Gain is the increase in transmitted (or received) signal
strength due to the antenna focusing the RF energy towards a direction. 
This gain is passive as the antenna does not add more external power to the
signal as an RF amplifier would (i.e. we do not need to power up an antenna). 
The direction of maximum gain is usually called _Antenna Boresight_. 

The gain G is an adimensional scalar computed as a ratio:

<!-- 
    https://latexeditor.lagrida.com/
    G = \frac{P_{rx}}{P_{rx,i}}
-->

<center>
    ![Antenna Gain definition]({static}/images/eirp_explained/gain_formula.png)
</center>

where P<sub>rx,i</sub> is the power of a sample signal received at an isotropic
antenna, while P<sub>rx</sub> is the power of the same sample signal received
at the antenna for which we are computing the gain. The Wikipedia article 
describing [Atenna Gains](https://en.wikipedia.org/wiki/Gain_(antenna)) 
shows the image below (public domain) to represent how a directional antenna
radiates the same power as an isotropic radiator while focusing it on a specific
direction:

<!-- https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Antenna_directive_gain_diagram.svg/2560px-Antenna_directive_gain_diagram.svg.png -->

<center>
    ![Wikipedia Antenna Gain example]({static}/images/eirp_explained/wikipedia_antenna_gain_image.png)
</center>

In the logarithmic scale, the gain is expressed in _dBi_ (with 0 dBi meaning
that the antenna is isotropic as the ratio equals 1).

## Computing the EIRP

In my previous blog post [Introduction to RX-SOP Configuration](https://castogio.github.io/introduction-to-rx-sop-configuration.html), I already described at a high level how to compute the power at the
receiver (RX) when the only relevant effect is FSPL, but I abused the 
notation P<sub>tx</sub> to refer to the power at the transmitter antenna.
I should have used the EIRP, which is defined as follows:

<!-- 
    https://latexeditor.lagrida.com/
    EIRP=\frac{P_{TX}*G_{tx,i}*G_{txbf}}{L_c} 
-->

<center>
    ![EIRP definition (linear scale)]({static}/images/eirp_explained/eirp_formula.png)
</center>

where P<sub>TX</sub> is the TX Power, G<sub>tx,i</sub> is the transmit antenna
gain with respect to the isotropic antenna, G<sub>txbf</sub> is the transmit 
beamforming gain, and L<sub>c</sub> is the loss due to the cable between the 
transmitter and the antenna. The beamforming gain is obtained in a 
Multiple-Input Multiple-Output (MIMO) system that focuses the RF power on a specific direction
combining the effect of multiple antennas transmitting at the same time with a 
constructive effect.
The EIRP formula can be expressed in decibels-to-milliwatt (dBm)
as follows:

<!-- EIRP~(dBm) = P_{TX}~(dBm)~+~G_{tx}~(dBi)~+~G_{txbf}~(dB)~-~L_c~(dB) -->
<center>
    ![EIRP definition (decibel scale)]({static}/images/eirp_explained/dbm_eirp_formula.png)
</center>

It is common to find in datasheets and regulatory domain documents EIRP values
expressed as a number in dBm followed by _e.i.r.p._ (for instance, 20 dBm e.i.r.p.).

## Why EIRP matters?

Now that the reader has a clearer idea of what EIRP is and how it correlates to
the TX power, we can explore how these two concepts influence our day-to-day. 

ETSI EN 300 328 v2.2 Section 4.3.2.2.3 set the power limit for 
non-Frequency Hopping Spread Spectrum wideband data transmission equipment, such
as 802.11 stations to be less or equal to 20 dBm e.i.r.p. in Europe. Section 5.3.2.2.4 
further specifies that in case a beamforming gain exists, it should be taken
into account for testing the equipment in the ETSI domain.

The above represents a constraint to the maximum TX power our APs can use.
Once we pick an antenna for our station, we will need to guarantee that the TX
power and the Transmit Beamforming gain (if the latter is used in the transmission)
stay within the specified limit. For instance, if our AP has an internal
antenna (no cable loss) with a 5 dBi and we know we get a 3 dB beamforming gain in our transmission,
then the maximum TX power in Europe must be less or equal to 12 dBm.


## References
- Coleman D.D., Westcott D.A. CWNA Certified Wireless Network Administrator
  Study Guide: Exam CWNA-107, Chapters 3 and 4, 5th Edition: Sybex. 2018.
- Haykin S., Moher M. Communication Systems, Chapter 6, 5th Edition: Wiley. 2010.
- Gain (antenna). (2023, March 28). Wikipedia. https://en.wikipedia.org/wiki/Gain_(antenna)
- ETSI, EN. "300 328 V2. 2.2 (2019-07)." Wideband transmission systems (2019).
