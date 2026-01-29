Troubleshooting
===============

Troubleshooting Add-on
----------------------

**Enable Debug Logging**

1. Navigate to the **Censys Add-on for Splunk**.

    .. image:: ./_static/open_add_on.png

2. Navigate to the **Configuration** tab.

    .. image:: ./_static/configure_add_on.png

3. Navigate to the **Logging** section.

    .. image:: ./_static/configure_add_on_logging.png

4. Select the ``DEBUG`` option from the **Log level** dropdown menu.

    .. image:: ./_static/configure_add_on_debug.png

**Configure Proxy Settings**

The Censys Add-on for Splunk supports proxy configuration for outbound API traffic. This is useful in environments where direct internet access is restricted.

1. Navigate to the **Censys Add-on for Splunk**.

    .. image:: ./_static/open_add_on.png

2. Navigate to the **Configuration** tab.

    .. image:: ./_static/configure_add_on.png

3. Navigate to the **Proxy** section.

4. Configure the following settings:

   - **Enable**: Check this box to enable proxy support
   - **Proxy Type**: Select the proxy protocol type:
     
     - ``http`` - HTTP proxy (most common, supports both HTTP and HTTPS traffic)
     - ``socks4`` - SOCKS4 proxy
     - ``socks5`` - SOCKS5 proxy
   
   - **Host**: Enter the proxy server hostname or IP address
   - **Port**: Enter the proxy server port number
   - **Username**: (Optional) Enter proxy authentication username if required
   - **Password**: (Optional) Enter proxy authentication password if required

5. Save the configuration.

**Important Notes:**

- Proxy settings are automatically applied to all API calls made by the Add-on.
- To use an HTTPS destination behind your proxy, you can configure your proxy server to forward HTTP proxy traffic to HTTPS.
- To verify proxy configuration is working, enable debug logging and check the logs for messages containing "proxy" or "Proxy configured".

**Where Censys ASM Risks Input Logs Are Written**

The Censys ASM Risks modular input writes its logs to a dedicated file (not splunkd.log). After you run "Collect data" or when the input runs on schedule, check:

- **Path:** ``$SPLUNK_HOME/var/log/splunk/splunk_ta_censys_censys_asm_risks.log``
- **Example (macOS):** ``/Applications/Splunk/var/log/splunk/splunk_ta_censys_censys_asm_risks.log``

Look for lines such as:

- ``Censys ASM Risks: collect_events started`` / ``collect_events finished``
- ``write_risk_events started for stanza '…'``
- ``Pulling risk events for input '…'``
- ``Processing N risk event(s)``
- ``Enrichment applied for riskID=…``

If you see none of these after running the input, Splunk may be using a different build of the add-on (for example from ``etc/apps/Splunk_TA_censys``). Reload or redeploy the add-on so your changes are used, then run the input again and recheck that log file.
