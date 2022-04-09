
# About 
Firewall rules can be complex and hard to analyze. This tool generates test packets,
that match a given rule/rules as so-called positive tests or do not as so-called negative tests. 

# Intro
Firewall is a software or hardware-based network security system, that monitors and controls 
an incoming and outgoing network traffic. Firewall intercepts a packet flow and examines its 
packet headers. Deciding what to do with the data flow is based on instructions in the so-called 
rule sets. Each rule specifies a condition, when packets match to this rule and an action to be 
made for those matched packets : typically discard or accept.

As we see, the rule syntax has in general a following format:

```sh
    Condition  ->  Action
```

A typical, real-world firewall rule looks like the following example:

```sh
1.1.1.1/31  5.5.5.5/31  9:9  7:7  6  ->  DROP
```

where :

* 1.1.1.1/31 is a source IP (IP range)
* 5.5.5.5/31 is a destination IP (IP range)
* 9:9 is a source port 
* 7:7 is a destination port
* 6 is a protocol number
* DROP is an action
    

# Application usage:

Usage: 

```sh
python tbgen.py <ruleset-file> <num of pos.tests> <num of negtests>
```

Output : generated packets for given rules in XML-format

Note :
1. Bounds for minimal and maximal number of tests are defined in section: 
    "CONSTANTS" (see the source code).

2. Rule format should have a following form :
    ```sh
        <src-net> <dst-net> <src-port> <dst-port> <protocol> "->" <action>
    ```

3. All first 5 fields can be negated via the '!' character
    Example :
    ```sh
         !192.151.11.17/32 15.0.120.4/32 !10 : 655 1221 : 1221 !6 -> DROP
    ```