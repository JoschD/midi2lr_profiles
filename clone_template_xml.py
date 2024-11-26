from collections.abc import Sequence
from pathlib import Path
import xml.etree.ElementTree as ET

THIS_DIR = Path(__file__).parent
BEHRINGER_PROFILES = THIS_DIR / "behringer-xtouch-mini" / "profiles"

CONTROLLER = "controller"
NOTE = "note"
SETTING = "setting"
COMMAND = "command_string"

def sort_settings_by_note_controller(xml_files: Sequence[Path], output_dir: Path = None):
    """ Sort the settings by note and controller values. 
    Makes it easier to compare files. """
    for target_file in xml_files:
        print(f"Sorting: {target_file.name}")
        tree = ET.parse(target_file)
        root = tree.getroot()

        # Separate tags by type (controller or note)
        grouped_elements = {
            CONTROLLER: [setting for setting in root.findall(SETTING) if CONTROLLER in setting.attrib], 
            NOTE: [setting for setting in root.findall(SETTING) if NOTE in setting.attrib], 
        }

        # Sort each group by the integer value of "controller" or "note"
        for key, elements in grouped_elements.items():
            elements.sort(key=lambda x: int(x.attrib[key]))  # inplace :-/

        # Clear existing children and add sorted elements back
        root.clear()
        for group in grouped_elements.values():
            for element in group:
                root.append(element)
        
        write_xml(tree, target_file, output_dir)

def clone_template(template: Path, xml_files: Sequence[Path], output_dir: Path = None):
    """ Clone the template entries into the given xml files. """
    template_tree = ET.parse(template)

    for target_file in xml_files:
        print(f"Cloning template {template.name} into {target_file.name}.")
        target_tree = ET.parse(target_file)
        target_tree = assign_template(template_tree, target_tree)
        write_xml(target_tree, target_file, output_dir)

    pass

def assign_template(template: ET, target: ET) -> ET:
    template_root = template.getroot()
    target_root = target.getroot()

    for template_setting in template_root.findall(SETTING):
        command = template_setting.attrib[COMMAND]
        for setting in target_root.findall(SETTING):
            if note_or_controller_equal(template_setting, setting):
                print(f"Override '{command}'.")
                setting.attrib[COMMAND] = command
                break
        else:
            print(f"Adding '{command}'.")
            target_root.append(template_setting)
    
    return target


def note_or_controller_equal(a, b) -> bool:
    for key in (NOTE, CONTROLLER):
        a_val = a.attrib.get(key, None)
        if a_val is not None:
            return a_val == b.attrib.get(key, None)
    return False






def write_xml(tree: ET, file_path: Path, output_dir: Path = None):
        ET.indent(tree, '    ')
        if output_dir is None:
            tree.write(file_path)
            return 

        output_dir.mkdir(exist_ok=True, parents=True)
        tree.write(output_dir / file_path.name, encoding="UTF-8", xml_declaration=True)
         






if __name__ == "__main__":
    clone_template(
        template=BEHRINGER_PROFILES / "Template-Action.xml",
        xml_files=[f for f in BEHRINGER_PROFILES.glob("*.xml") if not f.name.startswith("Template")],
        # output_dir=THIS_DIR / "test"
    )

    clone_template(
        template=BEHRINGER_PROFILES / "Template-Common.xml",
        xml_files=[
            BEHRINGER_PROFILES / "Basic.xml",
            BEHRINGER_PROFILES / "Colors-Gray.xml",
            BEHRINGER_PROFILES / "Colors-Hue.xml",
            BEHRINGER_PROFILES / "Colors-Luminance.xml",
            BEHRINGER_PROFILES / "Colors-Saturation.xml",
            BEHRINGER_PROFILES / "Crop.xml",
            BEHRINGER_PROFILES / "Detail.xml",
            BEHRINGER_PROFILES / "Effects.xml",
            BEHRINGER_PROFILES / "SpotRemoval.xml",
            # BEHRINGER_PROFILES / ".xml",
        ],
        # output_dir=THIS_DIR / "test"
    )

    sort_settings_by_note_controller(
        xml_files=BEHRINGER_PROFILES.glob("*.xml"),
        # output_dir=THIS_DIR / "test"
    )