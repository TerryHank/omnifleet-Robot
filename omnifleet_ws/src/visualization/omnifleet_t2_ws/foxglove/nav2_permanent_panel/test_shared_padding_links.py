from nav2_parameter_store import HEIGHT_FILE, SELECTED_FILE, SPECS, YAML_FILE
import parameter_links


def test_shared_padding_has_two_config_targets_and_official_docs():
    links = parameter_links.catalog(SPECS, YAML_FILE, HEIGHT_FILE, SELECTED_FILE)
    entry = links['costmap_padding']
    assert [target['label'] for target in entry['targets']] == [
        '局部配置', '全局配置']
    assert all(target['path'] == str(YAML_FILE.resolve()) for target in entry['targets'])
    assert entry['docs']['anchor_found'] is True
    assert entry['docs']['url'].endswith('#footprint_padding')
