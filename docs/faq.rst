Frequently Asked Questions
==========================

Why do we have a Censys ASM for Splunk App and Censys Add-on for Splunk?
------------------------------------------------------------------------

The Censys ASM for Splunk App is intended to be installed on the customer's search head. This is the visual layer for the data ingested. The app includes functionality such as dashboards, one-click pivot to Censys ASM, and pre-configured alerts. The Censys Add-on for Splunk is traditionally installed at the forwarder layer. The Add-on is what pulls the logs from Censys. We separated the functionality to align to Splunk best practices. Forwarders are the Splunk recommended way to ingest logs. To simplify deployment and support Splunk Cloud customers, we are required to provide 2 modes of deployment.

Does the app and add-on support Splunk Cloud deployments?
---------------------------------------------------------

Splunk Cloud is the managed service offering of Splunk. Our application and add-on are both certified to be deployed in Splunk Cloud.

Does the add-on conform to the Common Information Model?
--------------------------------------------------------

Yes. The add-on is compliant with the `Common Information Model (CIM) <http://docs.splunk.com/Documentation/CIM/latest/User/Overview>`_.

Does the add-on work with the Splunk Enterprise Security app?
-------------------------------------------------------------

.. todo::

    Coming soon...

My question wasn't answered here
--------------------------------

.. todo::

    Coming soon...
