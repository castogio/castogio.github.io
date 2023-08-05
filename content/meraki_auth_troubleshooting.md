Title: Troubleshooting WPA2-Enterprise with Meraki Cloud Authentication
Date: 2023-04-26 23:00
Category: 802.11

<!-- write an introduction -->
I was tinkering in my lab with my ancient MacBook, now running Windows 10, 
a few days ago, looking for ways to simplify my troubleshooting activities at work.
There is a service that the Cisco Meraki access points offer called Meraki 
Cloud Authentication, which offers an authentication server for 802.1X running
24/7 on their server. It uses the EAP-PEAP/EAP-TLS method to authenticate
users with an email username and a password. 

The email requested by the server is case-sensitive. Unsurprisingly an easy way 
to fail authentication is to write the correct email with one or more 
characters in the wrong case. Another common L8 issue is, of course, typing the
incorrect password because the user forgot it.

In this blog post, I would like to present some valuable tips to troubleshoot
incorrect authentication credentials using the Event Viewer in Windows 10.
This tool ships natively with the OS, and it provides a step-by-step report of
what is happening when connecting to an SSID, as it allows monitoring 
the service called "_WLAN-AutoConfig_," in charge of the 802.11 state machine.

## Accessing the Event Viewer

Let's start by accessing the logs. This is easily done by opening
the Start menu and searching for "Event Viewer." 
You can now navigate as follows in the menu on the left (each section is a 
dropdown item you can unfold):

1. Applications and Service Logs  > Microsoft > Windows > WLAN-AutoConfig.
2. Click on the WLAN-Autoconfig item.
3. Right-click on the "Operational" logs and make sure the log is enabled.
   (you will see the button "Disable Log").
4. Right-click on the "Operational" logs to make sure you opened the logs.

Most likely, you will see a list of events in the centre frame of the Event
Viewer; this is normal, and these logs refer to previous operations executed 
by your wireless network card.

## Dissecting a successful authentication

From the perspective of the Client station, there is no difference between a 
server located on-premises or in the cloud. Referring to the sequence diagram
shown below,
the administrator will notice a negligible deviation from what they may expect 
from standard 802.1X authentication processes; however, the actual RADIUS
exchanges are tunnelled between the Meraki APs (MR) and the cloud server.
You will not be able to see the traffic being sent and received on the 
distribution system, as the packets are encrypted.

<!-- exchange UML -->
<center>
    ![meraki cloud auth exchange diagram]({static}/images/meraki_auth_troubleshooting/meraki_auth_exchange.png)
</center>

You can perform a monitor mode packet capture to EAP traffic over the air.
The following exchange can be seen:

1. There is Identity Request/Response exchange where the client sends 
   the username in clear text (we will not be so lucky with the password).
2. The authentication server sends an MD5 request.
3. The client rejects it with a Negative Acknowledgement (NAK) and requests
   to use Protected EAP (PEAP).
4. The server agrees to use PEAP/EAP-TLS.
5. The client and the server perform the encrypted EAP protocol exchanges.
6. The server sends an EAP Success message to the client.
7. The 4-way RSN handshake can start.

NOTE: you may notice that the client's wireless MAC address is translated by
Wireshark as "Apple." This is expected as I was running Windows dual-booted
on a MacBook.

<!-- packet capture success -->
<center>
    ![packet capture of EAP success]({static}/images/meraki_auth_troubleshooting/SUCCESS_meraki_auth_exchange.png)
</center>

You can follow the exchanges described above (and more!) in the Event Viewer,
which logs every operation and state transition performed by the 802.11 state 
machine in chronological order from bottom to top (an event lower in the list
happened before the ones on top of it) as you can see in the picture below. 
We will focus on the logs whose Task Category is _OneXAuthentication_ (i.e. 
they are associated with 802.1X). I highlighted the last 1X event, showing a 
successful authentication and specifying the correct email used as "Identity," 
here shown as "hello@correct.com" (just an example).

<!-- log success -->
<center>
    ![EAP log success on Windows]({static}/images/meraki_auth_troubleshooting/capture_success_windows.png)
</center>

## Dissecting a failed authentication

Despite what we have seen in the previous section, the operation may not
be smooth when your users report issues with "connecting with the Wi-Fi".
You may not have immediate access to your trusty sidekick
or a different client to collect monitor mode capture. Nonetheless, you can
still open the Event Viewer, ask the user to attempt a connection, see it failing
miserably, and review what is reported in the logs.

<!-- log failure -->
<center>
    ![EAP log failure on Windows]({static}/images/meraki_auth_troubleshooting/capture_FAILURE_windows.png)
</center>

As you can see above, the general structure of the reports mostly stayed the same
when compared to the _successful_ case. In particular, we can see that the client 
passed the Open Authentication and the Association phases, but it stalled
when attempting the 802.1X operation.

Opening the log in question (helpfully marked as an "Error"), we can see that
WLAN-AutoConfig reports the fact that this was an _explicit_ EAP authentication
failure and that we sent the identity "HELLO@correct.com" (which we know is 
incorrect, as seen previously).

Being in my laboratory, I could take the packet capture and, indeed, all the EAP 
exchanges seen previously show up again, with the sole exception of the last
frame, which contains an EAP failure message (matching what was reported in the
Event Viewer).

<!-- packet capture failure -->
<center>
    ![packet capture of EAP failure]({static}/images/meraki_auth_troubleshooting/FAIL_meraki_auth_exchange.png)
</center>

Having been burnt in the past, I recommend you cross-check and confirm the
reports from any facility using additional external tools. In the scenario
described in this post, the Event Viewer correctly pointed to the root cause, 
but it might not be direct regarding more complex problems (also, bugs
are a thing). Seeing an EAP failure in the packet capture confirmed the fact. 

## Conclusion and Lesson Learned

The main takeaway of this little demo is "_know your tools_".
Client devices offer many built-in programs that will immensely 
simplify your day-to-day as a wireless analyst, especially when 
you cannot access more sophisticated equipment. The Event Viewer is the perfect 
example of a tool that ships with Windows and can show you what the client
is doing, what **it believes** is going wrong, and potentially, how to 
remediate the issue, as in our case.


### Bibliography
- “Managing User Accounts Using Meraki Cloud Authentication.” 
   Cisco Meraki, Feb. 2023, https://bit.ly/3UQh38T. Accessed 25 Apr. 2023.
- "Event Viewer." Microsoft, 
   Jan. 2019, https://bit.ly/41SfPMC. Accessed 26 Apr. 2023.