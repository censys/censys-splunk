.. Censys Splunk documentation master file, created by
   sphinx-quickstart on Wed May  4 13:56:05 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Censys Splunk's documentation!
=========================================

The Censys for Splunk apps and add-ons allow Censys users to import ASM and Search data into Splunk.

Features
--------

**Censys Add-on for Splunk**

- Import data from the Censys ASM Logbook API into Splunk
- Import data from the Censys ASM Risk Events API into Splunk

**Censys ASM App for Splunk**

- Dashboards for Censys ASM Logbook and Risk Events APIs
- Custom query-based alerts and reports

**Censys Search App for Splunk**

- Enrich logs with the most up-to-date information on public hosts and certificates

.. toctree::
   :maxdepth: 2
   :caption: Introduction
   :hidden:

   self
   faq
   troubleshooting
   support

.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   :hidden:
   :glob:

   quick-start
   add-on/index
   asm-app/*
   search-app/*
   add-on/cim
