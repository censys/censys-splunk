Censys Search App for Splunk
============================

The Censys Search App for Splunk enables rapid enrichment of logs with the most up-to-date information on public hosts and certificates.

This guide will help you:

- Install the Censys Search App in your Splunk environment
- Configure the Censys Search app
- Use the Censys Search command to enrich Splunk logs by IP address

Splunkbase: `Censys Search App for Splunk <https://splunkbase.splunk.com/app/5619/>`__

Search App Prerequisites
------------------------

1. Your Censys Search API key and secret.

    .. image:: ../_static/search_api_key.png

2. A Splunk account and installation.

Install the Censys Search App for Splunk
----------------------------------------

**Install from Splunkbase**

1. From the Splunk main page, click the **+ Find More Apps** button in the sidebar.

    .. image:: ../_static/find_more_apps.png

2. Type "Censys" in the search bar.

    .. image:: ../_static/browse_more_apps.png

3. On the results page, find the "Censys Search for Splunk" app card and click the green **Install** button.

    .. image:: ../_static/install_search_app.png

4. Enter your Splunkbase credentials and click the **Login and Install** button.

Configure the Censys Search App
-------------------------------

1. From the Splunk main page, click the **Manage Apps** gear in the top left corner of the page.

    .. image:: ../_static/manage_apps.png

2. Find "Censys Search" in the list of installed apps.

3. Click the **Set up** button to open the Censys Search app.

    .. image:: ../_static/setup_search_app.png

4. Enter your Censys Search API key and secret in the fields provided.

    .. image:: ../_static/setup_search_app_fields.png

Use the Censys Search command
-----------------------------

``censyssearch``
^^^^^^^^^^^^^^^^

The ``censyssearch`` command enables the enrichment of events by IP address. This command takes the events from a search as input and adds context to the events by querying the Censys API.

**Syntax**

.. code:: abnf

    censyssearch <ip_address_field> <summary|verbose>

+----------------------+-------------------------------------------------------------------+
| Parameter            | Usage                                                             |
+======================+===================================================================+
| ``ip_address_field`` | The name of the field containing the IP address to search.        |
+----------------------+-------------------------------------------------------------------+
| ``verbosity``        | The level of detail to return. Either ``summary`` or ``verbose``. |
+----------------------+-------------------------------------------------------------------+

.. note::

    For each enrichment command executed, responses will be cached for previously seen IPs, so the number of API credits consumed will equal the number of unique IPs enriched.

**Examples**

.. code:: abnf

    sourcetype="access_combined" | dedupe clientIP | censyssearch clientIP verbose

.. code:: abnf

    sourcetype="censys:asm:logbook" | dedupe ip | censyssearch ip summary

.. seealso::

    For more information on how Censys collects and models host data, visit our `help center <https://support.censys.io/hc/en-us/categories/4405770552724-Censys-Search>`_.
