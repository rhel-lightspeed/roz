"""Packages registry and protocol for roz."""

from roz.packages.goose import GoosePackage
from roz.packages.protocol import PackageProtocol


PACKAGES_MAP: dict[str, type[PackageProtocol]] = {
    "goose": GoosePackage,
}
