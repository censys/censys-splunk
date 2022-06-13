import json
import re
from argparse import ArgumentParser, Namespace
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from addonfactory_splunk_conf_parser_lib import TABConfigParser
from rst import rst

CIM_TITLE = "Common Information Model Mapping"
CIM_VERSION = "5.0.1"

FIELDALIAS_PREFIX = "FIELDALIAS-"
SOURCE_TYPE_PREFIX = "censys:asm:"

Stanza = Sample = Dict[str, str]
Conf = Dict[str, Stanza]
Confs = Dict[str, Conf]
Samples = Dict[str, Sample]


class SplunkConfs(str, Enum):
    """Splunk configuration files."""

    APP = "app.conf"
    EVENTTYPES = "eventtypes.conf"
    INPUTS = "inputs.conf"
    PROPS = "props.conf"
    TAGS = "tags.conf"

    def __str__(self):
        return self.value


class SplunkAppStanzas(str, Enum):
    """Splunk app.conf stanzas."""

    LAUNCHER = "launcher"
    UI = "ui"
    PACKAGE = "package"
    INSTALL = "install"
    TRIGGERS = "triggers"

    def __str__(self):
        return self.value


FIELDS_TO_SKIP = ["data_input_name"]

SOURCE_TYPE_API_DOC_MAPS = {
    "censys:asm:logbook": "https://app.censys.io/api-docs",
    "censys:asm:risks": "https://app.censys.io/api/v2/risk-docs",
}

CIM_TAGS_MAP = {
    "certificate": "Certificates",
    "inventory": "ComputeInventory",
    "listening": "Endpoint",
    "network": "NetworkResolutionDNS",
    "port": "NetworkTraffic",
    "report": "Endpoint",
    "service": "Endpoint",
    "ssl": "Certificates",
    "storage": "ComputeInventory",
    "vulnerability": "Vulnerabilities",
    "web": "Web",
}


def parse_args() -> Namespace:
    """Parse command line arguments."""
    parser = ArgumentParser(description="Generate CIM documentation")
    parser.add_argument(
        "--output", dest="output_dir", help="Output directory", required=True, type=Path
    )
    parser.add_argument(
        "--addon",
        dest="addon_dir",
        help="Add-on directory",
        required=True,
        type=Path,
    )
    return parser.parse_args()


def read_config_files(addon_dir: Path) -> Confs:
    """Read configuration files from the add-on directory.

    Args:
        addon_dir (Path): Add-on directory.

    Returns:
        Confs: Map of configuration files.
    """
    configurations = {}
    default_path = addon_dir / "default"
    assert default_path.is_dir()
    for file_name in [conf_file.value for conf_file in SplunkConfs]:
        file_path = default_path / file_name
        if not file_path.is_file():
            continue
        file_contents = file_path.read_text()
        parser = TABConfigParser()
        parser.read_string(file_contents)
        configurations[file_name] = parser.item_dict()
    return configurations


def read_sample_files(addon_dir: Path) -> Samples:
    """Read sample files from the add-on directory.

    Args:
        addon_dir (Path): Add-on directory.

    Returns:
        Samples: Map of sample files.
    """
    samples: Dict[str, str] = {}
    samples_path = addon_dir / "samples"
    if not samples_path.is_dir():
        return samples
    for file_name in samples_path.iterdir():
        if not file_name.is_file():
            continue
        file_contents = file_name.read_text()
        try:
            json_data = json.loads(file_contents)
        except json.decoder.JSONDecodeError:
            continue
        samples[file_name.name] = json_data
    return samples


def codify(text: str) -> str:
    """Convert text to a string that can be used in a code block."""
    return f"``{text}``"


def link(text: str, url: str) -> str:
    """Create a link."""
    return f"`{text} <{url}>`_"


def generate_table_for_app_conf(
    rst_doc: rst.Document,
    configurations: Confs,
):
    """Generate a table for the app.conf file.

    Args:
        rst_doc (rst.Document): RST document.
        configurations (Confs): Map of configuration files.
    """
    details = {
        "Name": (SplunkAppStanzas.UI, "label"),
        "Description": (SplunkAppStanzas.LAUNCHER, "description"),
        "Author": (SplunkAppStanzas.LAUNCHER, "author"),
        "Version": (SplunkAppStanzas.LAUNCHER, "version"),
        "Build": (SplunkAppStanzas.INSTALL, "build"),
        "Package ID": (SplunkAppStanzas.PACKAGE, "id"),
    }
    app_conf = configurations[SplunkConfs.APP]

    table_headers = ["Key", "Value"]
    table = rst.Table("App Details", table_headers)
    for title, (stanza, key) in details.items():
        table.add_item((title, app_conf.get(stanza, {}).get(key)))
    rst_doc.add_child(table)


def get_cim_link(cim_name: str) -> str:
    """Get the link to the CIM documentation.

    Args:
        cim_name (str): Name of the CIM.

    Returns:
        str: Link to the CIM documentation.
    """
    cim_id = CIM_TAGS_MAP.get(cim_name)
    if not cim_id:
        cim_id = cim_name
    return f"https://docs.splunk.com/Documentation/CIM/{CIM_VERSION}/User/{cim_id}"


def generate_table_for_props_conf(
    rst_doc: rst.Document,
    configurations: Confs,
    stanza_prefix: str = "censys:",
):
    """Generate a table for the props.conf file.

    Args:
        rst_doc (rst.Document): RST document.
        configurations (Confs): Map of configuration files.
        stanza_prefix (str): Prefix for stanzas.
    """
    # Get all the configuration files
    props_conf: Dict[str, Dict[str, str]] = configurations.get(SplunkConfs.PROPS)
    eventtypes_conf: Dict[str, Dict[str, str]] = configurations.get(
        SplunkConfs.EVENTTYPES, {}
    )
    tags_conf: Dict[str, Dict[str, str]] = configurations.get(SplunkConfs.TAGS)

    # Props are required to generate the table.
    if not props_conf:
        return

    # Map sourcetypes to eventtypes.
    sourcetype_to_eventtype = {}
    for eventtype_name, eventtype_conf in eventtypes_conf.items():
        sourcetype_search = eventtype_conf.get("search")
        if not sourcetype_search:
            continue
        match = re.match(r"\(sourcetype\=(?P<sourcetype>[a-z:]+)\)", sourcetype_search)
        if not match:
            continue
        sourcetype_to_eventtype[match.group("sourcetype")] = eventtype_name

    for stanza, properties in props_conf.items():
        if stanza_prefix not in stanza:
            continue

        title = codify(stanza)

        rst_doc.add_child(rst.Paragraph())
        rst_doc.add_child(rst.Section(title, depth=1))

        # Add API documentation link
        api_title = stanza.replace(SOURCE_TYPE_PREFIX, "").capitalize()
        api_docs_url = SOURCE_TYPE_API_DOC_MAPS.get(stanza)
        if api_docs_url:
            rst_doc.add_child(
                rst.Paragraph(link(f"{api_title} API docs", api_docs_url))
            )

        # Add CIM tags and models table
        if tags_conf:
            eventtype_name = sourcetype_to_eventtype.get(stanza)
            eventtype_key = f"eventtype={eventtype_name}"
            if eventtype_name and eventtype_key in tags_conf:
                models = {
                    cim_tag: CIM_TAGS_MAP[cim_tag]
                    for cim_tag in tags_conf[eventtype_key].keys()
                    if cim_tag in CIM_TAGS_MAP
                }
                models_list = rst.Table("CIM Models", ["Tag", "CIM Model"])
                for tag, model in sorted(models.items()):
                    models_list.add_item(
                        (codify(tag), link(model, get_cim_link(model)))
                    )
                rst_doc.add_child(models_list)

        # Add field aliases table
        properties_with_field_alias = {
            key: value
            for key, value in properties.items()
            if key.startswith(FIELDALIAS_PREFIX)
        }
        if properties_with_field_alias:
            alias_table = rst.Table("Field Aliases", ["Field", "CIM Alias"])
            for value in sorted(properties_with_field_alias.values()):
                to_alias, from_alias = value.split(" AS ")
                if to_alias in FIELDS_TO_SKIP:
                    continue
                alias_table.add_item((codify(to_alias), codify(from_alias)))
            rst_doc.add_child(alias_table)


def generate_cim_docs(
    configurations: Confs,
    title: str = CIM_TITLE,
) -> rst.Document:
    """Generate CIM documentation.

    Args:
        configurations (Confs): Map of configuration files.
        title (str): Title for the CIM documentation.

    Returns:
        rst.Document: RST document.
    """
    rst_doc = rst.Document(title)
    generate_table_for_props_conf(rst_doc, configurations)
    return rst_doc


def write_docs(output_dir: Path, configurations: Confs, samples: Samples):
    """Write documentation to the output directory.

    Args:
        configurations (Confs): Map of configuration files.
        samples (Samples): Map of sample files.
    """
    docs = {
        "cim": generate_cim_docs(configurations),
    }
    for file_name, rst_doc in docs.items():
        output_file = output_dir / f"{file_name}.rst"
        rst_doc.save(output_file)


def main():
    """Main function."""
    args = parse_args()
    configurations = read_config_files(args.addon_dir)
    # print(configurations)
    samples = read_sample_files(args.addon_dir)
    write_docs(args.output_dir, configurations, samples)


if __name__ == "__main__":
    main()
