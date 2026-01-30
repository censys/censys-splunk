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

Search commands (e.g. ``censysasmrisktypes``, ``censysasmriskinstances``) do not use the Configuration proxy. They respect the **HTTPS_PROXY**, **HTTP_PROXY**, and **NO_PROXY** environment variables in the environment where Splunk runs the search.

- Set **HTTPS_PROXY** (and **HTTP_PROXY** if needed) to your proxy URL, for example ``https://proxy.example.com:8080`` or ``http://proxy.example.com:8080``.
- Set **NO_PROXY** to a comma-separated list of hostnames or IPs that should bypass the proxy (e.g. ``localhost,127.0.0.1``).

Configure these in the environment of the Splunk process (e.g. in the systemd unit, init script, or shell that starts Splunk), depending on how your deployment is set up.
