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

| Splunk Enterprise versions | 7.2.x |
| Platforms                  | Platform independent |
| Vendor Products            | Censys Basic, Pro and Enterprise; Censys Enterprise Platform |
| Lookup file changes        | None |

## Installation and Configuration

### Requirements

**Hardware requirements**
- None

**Software requirements**
To function properly, Censys-Splunk requires the following software:
- Splunk Enterprise 7.2+

### Installation

Install this app on your search head/s as you would with any other app, then restart Splunk.

### Configuration

The app supports Censys' two products, and depending on what you have you may have one or both sets of API credentials. 

**SaaS users** can configure the app, which feeds dashboards from the logbook API, using the "inputs" section under the "settings" menu. From the platform UI, find your API key under the "Admin" view and copy it here. It will then be able to poll the API for logbook entries. A logbook dashboard is also included.

**Search users** configure your API ID and secret under the "manage apps" menu, and for the Censys app click "set up". Find your API credentials and copy them here. This will unlock the "censys" streaming command. 

## Usage

The "censys" streaming command lets you enrich results by IP address. Syntax: `... | censys [ip address field] {title, ports, banners, description, tls_names}`

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