Censys Add-on for Splunk
========================

The Censys Add-on for Splunk allows Censys ASM users to import Logbook and Risks data into Splunk®, where changes in their attack surface can be easily directed to downstream security and analytics applications.

This guide will help you:

- Install the Censys Add-on in your Splunk environment
- Configure the Censys Add-on
- Use the Censys Add-on to monitor your attack surface

Splunkbase: `Censys Add-on for Splunk <https://splunkbase.splunk.com/app/6399/>`__

--------

Add-on Prerequisites
--------------------

1. Your Censys ASM API key

    Find your key on the Censys ASM `integrations page <https://app.censys.io/integrations/>`__.

    .. image:: ../_static/asm_api_key.png

2. A Splunk account and installation.

--------

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

--------

Configure the Add-on
--------------------

Global Settings
^^^^^^^^^^^^^^^

If you will be using the same Censys workspace for all Splunk work, you can enter your Censys API in one place, rather than for each input.

1. Click on the Configuration tab at the top of the page

2. Under the Censys Settings tab, enter your API key (check out :ref:`add-on/index:add-on prerequisites` for help finding this)

    .. image:: ../_static/configure_global_settings.png

Logbook
^^^^^^^

From the Inputs page, select Create New Input. Fill out the following fields:

- Name for your data input
- Adjust the Interval field if desired. This determines how frequently data will be fetched from Censys ASM.
- [**Optional**: This will override any :ref:`add-on/index:global settings`] Censys ASM API key from the Censys ASM `integrations page <https://app.censys.io/integrations/>`__

.. image:: ../_static/logbook_config.png

.. seealso::

    For more information on logbook events, visit our `Logbook Event Catalog <https://support.censys.io/hc/en-us/articles/4412836964244-Logbook-Event-Catalog-Reference->`_.


Risks
^^^^^

.. todo::

    Coming soon...

--------

Use the Add-on
--------------

Download our :ref:`Censys ASM App for Splunk<asm-app/index:censys asm app for splunk>`!

Under the Search tab, you can enter queries on your data inputs.
If you are not familiar with Splunk search syntax, Splunk has the following helpful resources:

- `Splunk Search Documentation <https://docs.splunk.com/Documentation/Splunk/8.2.5/Search/GetstartedwithSearch?ref=hk/>`_
- `Splunk Search Tutorial <https://docs.splunk.com/Documentation/Splunk/8.2.5/SearchTutorial/WelcometotheSearchTutorial?ref=hk/>`_

--------

FAQs
----

What if I'm seeing no events in my index?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Confirm your :ref:`Censys ASM API key <add-on/index:add-on prerequisites>` is up to date

2. Confirm your index is accessible
