"""Set deterministic OOXML core and extended properties without editing cells.

The research matrix itself is authored with artifact-tool. This helper adds the
standard package-level authorship and rights metadata that artifact-tool does
not currently emit.
"""

from __future__ import annotations

import argparse
import os
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


CORE_REL = "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties"
APP_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties"
CORE_TYPE = "application/vnd.openxmlformats-package.core-properties+xml"
APP_TYPE = "application/vnd.openxmlformats-officedocument.extended-properties+xml"
REL_NAMESPACE = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_TYPES_NAMESPACE = "http://schemas.openxmlformats.org/package/2006/content-types"
FIXED_TIMESTAMP = (2026, 8, 16, 0, 0, 0)


def _xml_bytes(element: ET.Element) -> bytes:
    return b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + ET.tostring(
        element,
        encoding="utf-8",
        xml_declaration=False,
    )


def _set_relationship(root: ET.Element, relationship_type: str, target: str) -> None:
    relationship_tag = f"{{{REL_NAMESPACE}}}Relationship"
    for relationship in root.findall(relationship_tag):
        if relationship.get("Type") == relationship_type:
            relationship.set("Target", target)
            return
    used_ids = {item.get("Id", "") for item in root.findall(relationship_tag)}
    index = 1
    while f"rId{index}" in used_ids:
        index += 1
    ET.SubElement(root, relationship_tag, {"Id": f"rId{index}", "Type": relationship_type, "Target": target})


def _set_content_type(root: ET.Element, part_name: str, content_type: str) -> None:
    override_tag = f"{{{CONTENT_TYPES_NAMESPACE}}}Override"
    for override in root.findall(override_tag):
        if override.get("PartName") == part_name:
            override.set("ContentType", content_type)
            return
    ET.SubElement(root, override_tag, {"PartName": part_name, "ContentType": content_type})


def _core_properties(*, title: str, author: str, rights: str, subject: str) -> bytes:
    namespaces = {
        "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
        "dc": "http://purl.org/dc/elements/1.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "dcmitype": "http://purl.org/dc/dcmitype/",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
    root = ET.Element(f"{{{namespaces['cp']}}}coreProperties")
    ET.SubElement(root, f"{{{namespaces['dc']}}}title").text = title
    ET.SubElement(root, f"{{{namespaces['dc']}}}subject").text = subject
    ET.SubElement(root, f"{{{namespaces['dc']}}}creator").text = author
    ET.SubElement(root, f"{{{namespaces['dc']}}}rights").text = rights
    ET.SubElement(root, f"{{{namespaces['cp']}}}keywords").text = "NewsLens AI, literature survey, research matrix"
    ET.SubElement(root, f"{{{namespaces['cp']}}}lastModifiedBy").text = author
    created = ET.SubElement(root, f"{{{namespaces['dcterms']}}}created")
    created.set(f"{{{namespaces['xsi']}}}type", "dcterms:W3CDTF")
    created.text = "2026-08-16T00:00:00Z"
    modified = ET.SubElement(root, f"{{{namespaces['dcterms']}}}modified")
    modified.set(f"{{{namespaces['xsi']}}}type", "dcterms:W3CDTF")
    modified.text = "2026-08-16T00:00:00Z"
    return _xml_bytes(root)


def _extended_properties(author: str) -> bytes:
    namespace = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
    ET.register_namespace("", namespace)
    root = ET.Element(f"{{{namespace}}}Properties")
    ET.SubElement(root, f"{{{namespace}}}Application").text = "NewsLens AI"
    ET.SubElement(root, f"{{{namespace}}}Company").text = author
    ET.SubElement(root, f"{{{namespace}}}AppVersion").text = "1.0"
    return _xml_bytes(root)


def update_metadata(path: Path, *, title: str, author: str, rights: str, subject: str) -> None:
    with zipfile.ZipFile(path, "r") as source:
        relationships = ET.fromstring(source.read("_rels/.rels"))
        content_types = ET.fromstring(source.read("[Content_Types].xml"))
        _set_relationship(relationships, CORE_REL, "docProps/core.xml")
        _set_relationship(relationships, APP_REL, "docProps/app.xml")
        _set_content_type(content_types, "/docProps/core.xml", CORE_TYPE)
        _set_content_type(content_types, "/docProps/app.xml", APP_TYPE)

        # Keep the package root elements in their conventional default
        # namespaces. Some spreadsheet readers are stricter than generic XML
        # parsers about prefixed Relationships/Types root elements.
        ET.register_namespace("", REL_NAMESPACE)
        relationships_xml = _xml_bytes(relationships)
        ET.register_namespace("", CONTENT_TYPES_NAMESPACE)
        content_types_xml = _xml_bytes(content_types)

        file_descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.stem}-", suffix=".xlsx", dir=path.parent)
        os.close(file_descriptor)
        temporary_path = Path(temporary_name)
        try:
            with zipfile.ZipFile(temporary_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as destination:
                replacements = {
                    "_rels/.rels": relationships_xml,
                    "[Content_Types].xml": content_types_xml,
                }
                for item in source.infolist():
                    if item.filename in {"docProps/core.xml", "docProps/app.xml"}:
                        continue
                    destination.writestr(item, replacements.get(item.filename, source.read(item.filename)))
                for name, data in {
                    "docProps/core.xml": _core_properties(title=title, author=author, rights=rights, subject=subject),
                    "docProps/app.xml": _extended_properties(author),
                }.items():
                    info = zipfile.ZipInfo(name, date_time=FIXED_TIMESTAMP)
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    destination.writestr(info, data)
            os.replace(temporary_path, path)
        finally:
            temporary_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", required=True)
    parser.add_argument("--rights", required=True)
    parser.add_argument("--subject", required=True)
    args = parser.parse_args()
    update_metadata(args.path, title=args.title, author=args.author, rights=args.rights, subject=args.subject)


if __name__ == "__main__":
    main()
