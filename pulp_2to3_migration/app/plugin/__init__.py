import pkg_resources

# { plugin_name: PluginMigratorClass }
PLUGIN_MIGRATORS = {}

if not PLUGIN_MIGRATORS:
    for entry_point in pkg_resources.iter_entry_points(group='migrators'):
        if entry_point.name == 'docker':
            continue
        PLUGIN_MIGRATORS[entry_point.name] = entry_point.load()
