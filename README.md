# Censys for Splunk

Censys Add-On for Splunk.

Enables you to rapidly query Censys by IP, port, domain, or certificate hash, and enrich events with Censys data. Also enables you to collect Censys Enterprise Platform logs.

## Overview

### Features

- Workflow actions to search Censys from the UI
- A new `censys` streaming command to enrich search results by IP for banners, device description, web page titles, open ports, and TLS names
- A logbook application for Censys Enterprise, including an application to consume the logbook API and display data

### Release Notes

Version 1.0.x of Censys-Splunk is compatible with:

| Splunk Enterprise versions | 7.3.x |
| Platforms                  | Platform independent |
| Vendor Products            | Censys Basic, Pro and Enterprise; Censys Enterprise Platform |
| Lookup file changes        | None |

## Installation and Configuration

### Requirements

**Hardware requirements**
- None

**Softwrae requirements**
To function properly, Censys-Splunk requires the following software:
- Splunk Enterprise 7.3+

### Installation

Install this app on your search head/s as you would with any other app, then restart Splunk.

### Configuration

Edit the file `$SPLUNK_HOME/etc/apps/censys/bin/splunk_conf/censys.conf` and input your Censys API ID and secret, and optionally your Censys Enterprise Platform API key.

## Usage

`... | censys [ip address field] {title, ports, banners, description, tls_names}`

### Dashboard

The Censys dashboard, displaying Censys Enterprise Platform events for your account, can be access from the Censys app using the "Dashboards" menu.

### In-line search

The app introduces a new streaming command, `censys`, which allows you to perform lookups for each record based on the IP address. The command takes two arguments, in order:

- The name of the field containing the IP address to query (e.g. dst_ip)
- The name of the enrichment you wish to perform, one of: 
  - title - the web page title if there is any, on ports 80, 443, 8080, and 8888
  - ports - the ports and protocols found open on the host
  - banners - the banners of 20 common protocols and HTTP server information
  - description - the device description, if known
  - tls_names - the DNS names found on any TLS certificates observed on the host

In searches containing IP addresses, this `censys` command can be used to enrich events. For example:

	host="apache"
	| censys clientip ports
	| mvexpand protocols
	| top protocols

The command will execute a query for each IP address in the data set, but will cache responses per execution for previously seen IPs. This means that each run of the command will consume as many API credits as you have unique IPs.