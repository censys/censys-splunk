Censys ASM App for Splunk
=========================

The Censys ASM App for Splunk allows ASM users to visualized Logbook API data with a pre-built dashboard that can be customized with additional views.

    **Note**: This app is dependent on `Censys Add-on for Splunk <https://splunkbase.splunk.com/app/6399/>`__.

This guide will help you:

- Set up the Censys Add-on for Splunk (if you haven't already)
- View our Attack Surface Management dashboard and create your own dashboards
- Set up reports and alerting
- Move seamlessly between Splunk and Censys ASM

Splunkbase: `Censys ASM App for Splunk <https://splunkbase.splunk.com/app/4830/>`__

ASM App Prerequisites
---------------------

1. A Splunk account and installation.

2. `Censys Add-on for Splunk <https://splunkbase.splunk.com/app/6399/>`__ installed and configured with your Censys API key.

-------

Install the Censys ASM App for Splunk
-------------------------------------

Install from Splunkbase (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. From the Splunk Web main page, click the **+ Find More Apps** button in the sidebar.

    .. image:: ../_static/find_more_apps.png

2. Type "**Censys**" in the search bar and press **Enter**.

3. On the results page, find the "Censys ASM App for Splunk" app card and click the green **Install** button.

    .. image:: ../_static/install_asm_app.png

4. Reenter login credentials to confirm your choice.

Install from File
^^^^^^^^^^^^^^^^^

1. Go to the Add-on's page on `Splunkbase <https://splunkbase.splunk.com/app/4830/>`__ and click the **Download** button.

    .. image:: ../_static/download_app.png

2. From the Splunk Web main page, click the gear icon next to **Apps**, then click **Install app from file**.

    .. image:: ../_static/install_from_file.png

---------

Use the App
-----------

Censys has provided several reports based on ASM data for users to start with.
These reports can be used for alerting and creating dashboards. Workflow actions provide a seamless transition between Splunk Search and Censys ASM.

Create Alerts from Reports
^^^^^^^^^^^^^^^^^^^^^^^^^^

To view the pre-configured reports, click the **Reports** tab at the top of the page.
To create an alert based on a report, click **Open in Search** next to the report you want to use.

    .. image:: ../_static/open_in_search.png

Modify the query to your liking or leave as is, then click **Save As Alert**.

    .. image:: ../_static/save_as_alert.png

Give your alert a title, set the alert to be scheduled or real-time, and configure the alert's trigger settings and trigger actions.

Interact with Dashboards
^^^^^^^^^^^^^^^^^^^^^^^^

To view the pre-configured dashboard, click the **Dashboards** tab at the top of the page.
To view a query in Splunk Search, click on panel.

    .. image:: ../_static/dashboard.png

Workflow Actions
^^^^^^^^^^^^^^^^

From the events page, click the dropdown to the left of the event's timestamp. This will show all the fields for the event.

    .. image:: ../_static/workflow_action.png

To view more information about an event, click the **Actions** dropdown next to the asset you'd like to view, then **[Domain|Host|Storage Asset|Certificate] in Censys ASM/Search**.

    .. image:: ../_static/asm_dashboard.png

Turn Queries into Reports, Alerts, and Dashboards
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From Splunk Search, any query can be used to create custom reports, alerts, and dashboards by clicking the **Save As** button in the top right corner.
A query can be added as a new panel to an existing dashboard or a new dashboard can be created.

Create Reports and Alerts from Scratch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

One more way to create reports and alerts is by going to **Settings -> Searches, reports, and alerts**.

    .. image:: ../_static/search_report_alert.png

From there, you can manage current reports and alerts, create new reports and alerts from custom queries.

Set a Home Dashboard
^^^^^^^^^^^^^^^^^^^^

Easily check out the Censys ASM dashboard or your own custom dashboard by setting it as your home dashboard.

    .. image:: ../_static/home_dashboard.png

Now, when you open your Splunk Web main page, you'll easily see changes in your attack surface.

Set Up Splunk Event Generator (Eventgen)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Splunk Event Generator is a useful tool for generating configurable events to simulate real-time data. 
We have provided a sample ``eventgen.conf`` file along with sample events to get you started.

**1. Install and enable the Splunk Eventgen app**

From the Splunk Web main page, click the **+ Find More Apps** button in the sidebar.

    .. image:: ../_static/find_more_apps.png

Type "**Eventgen**" in the search bar and press **Enter**.

On the results page, find the **Eventgen** app card and click the green **Install** button.

    .. image:: ../_static/install_eventgen.png

Go to **Settings > Data inputs** and click **SA-Eventgen**.

    .. image:: ../_static/enable_eventgen.png

Click **Enable** in the **modinput_eventgen** row.

    .. image:: ../_static/enable_data_input.png

**2. Create an Index**

A new index for your sample events can be created through the Splunk Web UI or the Splunk Enterprise CLI. 
Instructions for each option are detailed below.

**Option #1:** Splunk Web UI

Go to **Settings > Indexes**.

    .. image:: ../_static/settings_index.png

On the Indexes page, click **New Index**.

Enter "**demo**" in the **Index Name** field and select **SA-Eventgen** in the **App** field.

    .. image:: ../_static/add_index.png

Click **Save**.

**Option #2:** Splunk Enterprise CLI

From the terminal (Mac or Linux), navigate to ``$SPLUNK_HOME/bin`` and enter the following command:
    .. code:: bash
    
        ./splunk add index demo

You will likely need to enter your Splunk username and password.

    **Note:** If you would like to name your index something other than **demo**, you will need to edit the ``eventgen.conf`` file.

**3. View your Sample Events**

In the Censys ASM App, click the **Search** tab at the top of the page.

Enter the search query ``index=demo`` to see all sample events.

**Additional Resources**

- `Splunk Eventgen Documentation <http://splunk.github.io/eventgen/>`__
- `Splunk Dev Eventgen Setup Tutorial <https://dev.splunk.com/enterprise/tutorials/module_getstarted/useeventgen/>`__

----

Additional information can be found in Splunk documentation:

- `Splunk Alerting Manual <https://docs.splunk.com/Documentation/Splunk/8.2.6/Alert/AlertWorkflowOverview>`__
- `Splunk Reporting Manual <https://docs.splunk.com/Documentation/Splunk/8.2.6/Report/Createandeditreports>`__
- `Splunk Search Manual <https://docs.splunk.com/Documentation/Splunk/8.2.6/Search/GetstartedwithSearch>`__
