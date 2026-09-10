# Change Log

## 4.1.7

- **Breaking**: the app now requires Splunk Enterprise 10.4 or later, or Splunk Cloud
  Platform. The `start` and `setup` views previously rendered through the app's own Mako
  template, `appserver/templates/start.html`. That template has been removed and both views
  now use the platform-provided `pages/splunk_ui_app.html`, which ships with Splunk 10.4
  and later. Custom Mako templates are deprecated in Splunk 10.4 and are reported by
  AppInspect as `check_for_custom_mako_templates` and, because the template contained a
  Python code block, `check_for_existence_of_python_code_block_in_mako_template`.
- The app's own stylesheets, `bootstrap-enterprise.css` and `styles.css`, are now attached
  by the page bundles rather than by the removed template.
- Knowledge objects now grant write access to `sc_admin` in addition to `admin`. Splunk
  Cloud customers hold `sc_admin` rather than `admin`, so objects restricted to `admin`
  alone were not editable by them (`check_kos_are_accessible`).
- Added `default/server.conf` declaring `conf_replication_include.splunk_create` under
  `[shclustering]`, so the app's custom configuration replicates across search head
  cluster members (`check_custom_conf_replication`).
- Removed the stale `splunk_sdk-1.7.3.dist-info` and `splunk_sdk-2.0.2.dist-info`
  directories, which described Splunk SDK for Python versions that were not vendored in the
  app. AppInspect reads every `splunk_sdk-*.dist-info/METADATA` under `bin/` and `lib/`, so
  the 1.7.3 metadata was reported as an out-of-date SDK (`check_python_sdk_version`) even
  though the vendored code was 2.1.0.

## 0.0.1 – Release date: TBA

- Initial version
