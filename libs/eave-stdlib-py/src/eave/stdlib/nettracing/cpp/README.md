# Network-Trace

Mostly stolen from [pcap++ gh example](https://github.com/seladb/PcapPlusPlus/blob/v23.09/Examples/HttpAnalyzer/main.cpp#L448).
this program sucks, but here's how to use it

### Prereqs

must install PcapPlusPlus through homebrew or some other method as directed on their website (I could only get it work through brew).
probably need CMake installed if that's not already installed by default.

## Compiling

There's 2 commands you need to run to build the CMake project, but I never remember them, so I slapped them in the Makefile under the `all` alias. In your terminal run `make all` or even just `make` (as "all" is the default alias) to run the CMake commands to build the project.

It will produce an obviously named executbale.

## Running

This program requires some flags to run; you can see the help message if you want. We really only care about live capture, so you need to pass the `-i` and `-p` flags to specify the network interface and port number to capture packets from.

Port number is easy; 80 is for http traffic, and 443 is for https traffic. Remember that so you dont get confused like me when none of your https traffic is being captured when you clearly provided port 80.

Your network interface is a little tougher. This IP/interface must be for your local computer (NOT YOUR ROUTER PUBLIC IP) since this non-promiscuous program will only capture packets where the provided IP matches the packet final destination IP. I've been using my private IP address, which I found under the BROADCAST device from `ip -4 addr`. I think the IP or device name for that should work...

Then you have to run w/ sudo in order to have permissions to capture any network traffic. This is what I've been running:
```
sudo ./Network-Trace -i 'wlp170s0' -p '80'
```
or this w/ an IPv4 address is probs equivalent:
```
sudo ./Network-Trace -i '10.0.0.33' -p '80'
```

I hope that all worked bcus youre on your own now; i barely understand this shit

## PRoblems

* havent yet figured out how to run in promisicuous mode, so we only capture packets that are incoming to our device (no outgoing traffic).
* packet stitching?
* undetermined if pcap++ can read the data from the stitched packets. It must be able to, right???
