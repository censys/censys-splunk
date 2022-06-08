import json
import os
from argparse import ArgumentParser, Namespace
from enum import Enum
from pathlib import Path
from typing import Dict, List

from addonfactory_splunk_conf_parser_lib import TABConfigParser
from rst import rst

DEFAULT_TITLE = "Common Information Model Mapping"

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


SOURCE_TYPE_API_DOC_MAPS = {
    "censys:asm:logbook": "https://app.censys.io/api-docs",
    "censys:asm:risks": "https://app.censys.io/api/v2/risk-docs",
}


def parse_args() -> Namespace:
    """Parse command line arguments."""
    parser = ArgumentParser(description="Generate CIM documentation")
    parser.add_argument(
        "--title",
        dest="title",
        help="Title for the generated documentation",
        type=str,
        default=DEFAULT_TITLE,
    )
    parser.add_argument(
        "-o", "--output", dest="output", help="Output file", required=True, type=Path
    )
    parser.add_argument(
        "-a", "--addon", dest="addon", help="Add-on directory", required=True, type=Path
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
    props_conf: Dict[str, Dict[str, str]] = configurations[SplunkConfs.PROPS]
    # print(props_conf)
    rst_doc.add_child(rst.Section("Sourcetypes", depth=2))

    for stanza, properties in props_conf.items():
        if stanza_prefix not in stanza:
            continue

        title = codify(stanza)

        # Add KV Mode
        # kv_mode = properties.get("KV_MODE")
        # if kv_mode:
        #     title += f" ({codify(kv_mode)} kv mode)"

        rst_doc.add_child(rst.Section(title, depth=3))

        # Add API documentation link
        api_docs_url = SOURCE_TYPE_API_DOC_MAPS.get(stanza)
        if api_docs_url:
            api_link_title = stanza.replace("censys:asm:", "").capitalize()
            rst_doc.add_child(
                rst.Paragraph(link(f"{api_link_title} API docs", api_docs_url))
            )

        # Render field aliases
        properties_with_field_alias = {
            key: value
            for key, value in properties.items()
            if key.startswith("FIELDALIAS-")
        }
        if properties_with_field_alias:
            table_headers = ["Field", "CIM Alias"]
            table = rst.Table("Field Aliases", table_headers)
            for value in sorted(properties_with_field_alias.values()):
                to_alias, from_alias = value.split(" AS ")
                table.add_item((codify(to_alias), codify(from_alias)))
            rst_doc.add_child(table)


def write_docs(
    title: str,
    output_file: Path,
    configurations: Confs,
    samples: Samples,
):
    rst_doc = rst.Document(title)
    # if SplunkConfs.APP in configurations:
    #     generate_table_for_app_conf(rst_doc, configurations)
    if SplunkConfs.PROPS in configurations:
        generate_table_for_props_conf(rst_doc, configurations)

    # Write to file
    rst_doc.save(output_file)


def main():
    args = parse_args()
    configurations = read_config_files(args.addon)
    # print(configurations)
    samples = read_sample_files(args.addon)
    # print(samples)
    write_docs(args.title, args.output, configurations, samples)


if __name__ == "__main__":
    main()
