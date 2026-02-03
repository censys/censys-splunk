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

The Censys Add-on for Splunk supports proxy configuration for outbound API traffic. This is useful in environments where direct internet access is restricted. How you configure the proxy depends on whether you use modular inputs (Inputs tab) or search commands (Search tab).

**Proxy for modular inputs (Inputs tab)**

Modular inputs (e.g. Censys ASM Risks, Censys ASM Logbook) use the proxy configured in the add-on's Configuration page.

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

   Proxy settings are then applied automatically to all API calls made by the modular inputs.

**Proxy for search commands (Search tab)**

Search commands (e.g. ``censysasmrisktypes``, ``censysasmriskinstances``) do not use the Configuration proxy. They use **HTTPS_PROXY** and **NO_PROXY** from the environment. Search commands run in worker subprocesses that often do not receive app-level environment variables from ``server.conf``. Use **splunk-launch.conf** so the variables apply to all Splunk processes, including search workers.

**Configure proxy using splunk-launch.conf (recommended)**

1. Open **splunk-launch.conf** on the Splunk server:

   - Path: ``$SPLUNK_HOME/etc/splunk-launch.conf``
   - Examples: ``/opt/splunk/etc/splunk-launch.conf`` (Linux), ``C:\Program Files\Splunk\etc\splunk-launch.conf`` (Windows)

2. Add or edit an ``[env]`` stanza at the end of the file:

   .. code-block:: ini

      [env]
      HTTPS_PROXY = https://your-proxy-host:8080
      NO_PROXY = localhost,127.0.0.1

   Use your actual proxy URL and port. The proxy URL itself can use ``https://`` or ``http://`` (e.g. ``http://proxy.example.com:8080`` is fine for HTTPS traffic); **HTTPS_PROXY** is the variable that must be set for the Censys search commands.

3. Restart Splunk so the new environment is picked up:

   .. code-block:: bash

      $SPLUNK_HOME/bin/splunk restart

4. Run a search that uses a Censys search command (e.g. ``| censysasmriskinstances``).
