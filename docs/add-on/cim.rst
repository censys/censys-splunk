================================
Common Information Model Mapping
================================


Sourcetypes
-----------


``censys:asm:logbook``
++++++++++++++++++++++

`Logbook API docs <https://app.censys.io/api-docs>`_

.. list-table:: Field Aliases
    :header-rows: 1

    * -  Field
      -  CIM Alias
    * -  ``data.cve``
      -  ``cve``
    * -  ``data.cvss``
      -  ``cvss``
    * -  ``data.mailExchange``
      -  ``dest_name``
    * -  ``data.port``
      -  ``dest_port``
    * -  ``data.port``
      -  ``src_port``
    * -  ``data.severity``
      -  ``severity``
    * -  ``data.sha256``
      -  ``ssl_hash``
    * -  ``data.softwareName``
      -  ``app``
    * -  ``data.softwareName``
      -  ``service_name``
    * -  ``data.softwareProduct``
      -  ``service``
    * -  ``data.softwareSource``
      -  ``src``
    * -  ``data.softwareUri``
      -  ``service_id``
    * -  ``data.softwareVendor``
      -  ``vendor_product``
    * -  ``data.subdomain``
      -  ``dest_name``
    * -  ``data.title``
      -  ``signature``
    * -  ``data.transportProtocol``
      -  ``transport``
    * -  ``entity.domain``
      -  ``dns``
    * -  ``entity.domain``
      -  ``src_name``
    * -  ``entity.hostname``
      -  ``dns``
    * -  ``entity.hostname``
      -  ``site``
    * -  ``entity.hostname``
      -  ``src_host``
    * -  ``entity.hostname``
      -  ``ssl_subject_common_name``
    * -  ``entity.ipAddress``
      -  ``ip``
    * -  ``entity.ipAddress``
      -  ``src_ip``
    * -  ``entity.objectStorageName``
      -  ``storage_name``
    * -  ``entity.objectStorageName``
      -  ``url``
    * -  ``entity.sha256``
      -  ``ssl_hash``
    * -  ``timestamp``
      -  ``creation_time``

``censys:asm:risks``
++++++++++++++++++++

`Risks API docs <https://app.censys.io/api/v2/risk-docs>`_
