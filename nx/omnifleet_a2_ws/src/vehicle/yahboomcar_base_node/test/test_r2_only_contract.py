from pathlib import Path
import re


SRC_ROOT = Path(__file__).parents[2]
PACKAGES = (
    SRC_ROOT / "yahboomcar_base_node",
    SRC_ROOT / "yahboomcar_bringup",
    SRC_ROOT / "yahboomcar_ctrl",
)
FIRMWARE = SRC_ROOT / "robot_stm32"
NAME_PATTERN = re.compile(r"(?i)(?:^|[_-])x[13](?:[_.-]|$)")
TEXT_PATTERN = re.compile(r"(?i)(?<![0-9a-f])x[13](?![0-9a-f])")
FIRMWARE_MODEL_PATTERN = re.compile(
    r"(?i)(?:RDK[-_ ]?X[3]|X[3]\s*PLUS|X[1]\s*,\s*X[3]|四轮普通小车\s*X[1])"
)
TEXT_SUFFIXES = {
    ".c", ".cpp", ".h", ".hpp", ".py", ".txt", ".md", ".xml", ".yaml", ".yml"
}


def _source_files():
    for package in PACKAGES:
        for path in package.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.suffix.lower() in TEXT_SUFFIXES or path.name in {
                "CMakeLists.txt", "setup.py", "setup.cfg"
            }:
                yield path


def test_only_r2_chassis_sources_and_entry_points_remain():
    obsolete_names = [
        path
        for package in PACKAGES
        for path in package.rglob("*")
        if NAME_PATTERN.search(path.name)
    ]
    obsolete_text = [
        path
        for path in _source_files()
        if TEXT_PATTERN.search(path.read_text(encoding="utf-8", errors="ignore"))
    ]

    assert obsolete_names == []
    assert obsolete_text == []


def test_obsolete_chassis_labels_do_not_return_to_stm32_sources():
    obsolete_text = [
        path
        for path in FIRMWARE.rglob("*")
        if path.is_file()
        and path.suffix.lower() in TEXT_SUFFIXES
        and FIRMWARE_MODEL_PATTERN.search(
            path.read_text(encoding="utf-8", errors="ignore")
        )
    ]
