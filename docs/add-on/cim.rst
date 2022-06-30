================================
Common Information Model Mapping
================================



======================
``censys:asm:logbook``
======================

`Logbook API docs <https://app.censys.io/api-docs>`_

.. list-table:: CIM Models
    :header-rows: 1

    * -  Tag
      -  CIM Model
    * -  ``certificate``
      -  `Certificates <https://docs.splunk.com/Documentation/CIM/5.0.1/User/Certificates>`_
    * -  ``inventory``
      -  `ComputeInventory <https://docs.splunk.com/Documentation/CIM/5.0.1/User/ComputeInventory>`_
    * -  ``listening``
      -  `Endpoint <https://docs.splunk.com/Documentation/CIM/5.0.1/User/Endpoint>`_
    * -  ``network``
      -  `NetworkResolutionDNS <https://docs.splunk.com/Documentation/CIM/5.0.1/User/NetworkResolutionDNS>`_
    * -  ``port``
      -  `NetworkTraffic <https://docs.splunk.com/Documentation/CIM/5.0.1/User/NetworkTraffic>`_
    * -  ``report``
      -  `Endpoint <https://docs.splunk.com/Documentation/CIM/5.0.1/User/Endpoint>`_
    * -  ``service``
      -  `Endpoint <https://docs.splunk.com/Documentation/CIM/5.0.1/User/Endpoint>`_
    * -  ``ssl``
      -  `Certificates <https://docs.splunk.com/Documentation/CIM/5.0.1/User/Certificates>`_
    * -  ``storage``
      -  `ComputeInventory <https://docs.splunk.com/Documentation/CIM/5.0.1/User/ComputeInventory>`_
    * -  ``vulnerability``
      -  `Vulnerabilities <https://docs.splunk.com/Documentation/CIM/5.0.1/User/Vulnerabilities>`_
    * -  ``web``
      -  `Web <https://docs.splunk.com/Documentation/CIM/5.0.1/User/Web>`_
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


====================
``censys:asm:risks``
====================

`Risks API docs <https://app.censys.io/api/v2/risk-docs>`_

.. list-table:: CIM Models
    :header-rows: 1

    * -  Tag
      -  CIM Model
    * -  ``report``
      -  `Endpoint <https://docs.splunk.com/Documentation/CIM/5.0.1/User/Endpoint>`_
    * -  ``vulnerability``
      -  `Vulnerabilities <https://docs.splunk.com/Documentation/CIM/5.0.1/User/Vulnerabilities>`_
.. list-table:: Field Aliases
    :header-rows: 1

    * -  Field
      -  CIM Alias
    * -  ``riskName``
      -  ``signature``
    * -  ``riskType``
      -  ``signature_id``
    * -  ``ts``
      -  ``creation_time``
