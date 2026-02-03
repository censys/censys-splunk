Censys Add-on for Splunk
========================

The Censys Add-on for Splunk allows Censys ASM users to import Logbook and Risks data into Splunk®, where changes in their attack surface can be easily directed to downstream security and analytics applications.

This guide will help you:

- Install the Censys Add-on in your Splunk environment
- Configure the Censys Add-on
- Use the Censys Add-on to monitor your attack surface

Splunkbase: `Censys Add-on for Splunk <https://splunkbase.splunk.com/app/6399/>`__

----

Add-on Prerequisites
--------------------

1. Your Censys ASM API key

    Find your key on the Censys ASM `integrations page <https://app.censys.io/integrations/>`__.

    .. image:: ../_static/asm_api_key.png

2. A Splunk account and installation.

----

Install the Censys Add-on for Splunk
-------------------------------------

Install from Splunkbase (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. From the Splunk main page, click the **+ Find More Apps** button in the sidebar.

    .. image:: ../_static/find_more_apps.png

2. Type "Censys" in the search bar.

3. On the results page, find the "Censys Add-on for Splunk" app card and click the green **Install** button.

    .. image:: ../_static/install_addon.png

4. Reenter login credentials to confirm your choice.

Install from File
^^^^^^^^^^^^^^^^^

1. Go to the Add-on's page on `Splunkbase <https://splunkbase.splunk.com/app/6399/>`__ and click the **Download** button.

    .. image:: ../_static/download_addon.png

2. From the Splunk Web main page, click the gear icon next to **Apps**, then click **Install app from file**.

    .. image:: ../_static/install_from_file.png

----

.. _configure-the-add-on:

Configure the Add-on
--------------------

Global Settings
^^^^^^^^^^^^^^^

If you will be using the same Censys workspace for all Splunk work, you can enter your Censys ASM API key in one place, rather than for each input.

1. Click on the Configuration tab at the top of the page

2. Under the Accounts tab, you will see all of your configured accounts. Click "Add" to configure a new account.

    .. image:: ../_static/configure_global_accounts.png

3. Enter a name for this account (the name of your ASM workspace is a good choice) and enter your Censys ASM API key (check out :ref:`add-on/index:add-on prerequisites` for help finding this)

    .. image:: ../_static/add_account.png


Inputs
^^^^^^

From the Inputs page, select Create New Input. Select the API you would like to pull from.

    .. image:: ../_static/add_input.png

Fill out the following fields:

- Input Name (required): A name for the input
- Interval (in seconds): How often the input should run (default is 3600 seconds, or 1 hour)
- Index: The index where the data will be stored
- Account: The Censys account to use (if you have multiple accounts)

    .. image:: ../_static/risks_input.png

.. seealso::

    For more information on logbook events, visit our `Logbook Event Catalog <https://support.censys.io/hc/en-us/articles/4412836964244-Logbook-Event-Catalog-Reference->`_.

----

Use the Add-on
--------------

Download our :ref:`Censys ASM App for Splunk<asm-app/index:censys asm app for splunk>`!

Under the Search tab, you can enter queries on your data inputs.
If you are not familiar with Splunk search syntax, Splunk has the following helpful resources:

- `Splunk Search Documentation <https://docs.splunk.com/Documentation/Splunk/9.0.2/Search/GetstartedwithSearch?ref=hk/>`_
- `Splunk Search Tutorial <https://docs.splunk.com/Documentation/Splunk/9.0.2/SearchTutorial/WelcometotheSearchTutorial?ref=hk/>`_

ASM search commands
-------------------

Two search commands pull live data from the Censys ASM API and can be used to enrich your existing data: ``censysasmrisktypes`` and ``censysasmriskinstances``. They require your ASM API key to be configured in the add-on (see :ref:`configure-the-add-on`).

``censysasmrisktypes``
^^^^^^^^^^^^^^^^^^^^^^

Returns the list of risk types defined in your ASM workspace (e.g. open ports, vulnerable software). Use it to see available risk types or to join/lookup with other data.

**Syntax**

.. code-block:: text

   | censysasmrisktypes

**Examples**

.. code-block:: text

   | censysasmrisktypes

   | censysasmrisktypes | spath | table id, name, description, defaultSeverity

``censysasmriskinstances``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns the current risk instances from ASM (each instance is a specific finding, e.g. a host with an open port or a vulnerability). Use it to get up-to-date risk data or to enrich risk events (e.g. ``censys:asm:risks``) with severity and display name.

**Syntax**

.. code-block:: text

   | censysasmriskinstances

**Examples**

.. code-block:: text

   | censysasmriskinstances

   | censysasmriskinstances | spath | table id, displayName, severity, status

Enriching risk events with risk instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To enrich ingested risk events (sourcetype ``censys:asm:risks``) with current severity and display name from the API, join events to the output of ``censysasmriskinstances`` by risk ID:

.. code-block:: text

   index=* sourcetype="censys:asm:risks"
   | spath
   | eval riskID=id
   | join type=left riskID [
       | censysasmriskinstances
       | spath
       | eval riskID=id
       | table riskID severity displayName
     ]
   | where isnotnull(severity) AND severity!=""
   | table id, op, reason, riskID, severity, displayName, delta.*

This keeps only events that matched a risk instance with a non-empty severity. For large or repeated use, consider populating the ``asm_risk_instances_lookup`` lookup (via the scheduled search that runs ``| censysasmriskinstances | ... | outputlookup asm_risk_instances_lookup``) and using ``lookup asm_risk_instances_lookup`` instead of the join to avoid calling the API on every search.

--------

FAQs
----

What if I'm seeing no events in my index?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Confirm your :ref:`Censys ASM API key <add-on/index:add-on prerequisites>` is up to date

2. Confirm your index is accessible
