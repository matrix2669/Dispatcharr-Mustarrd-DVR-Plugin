"""Disposable checks using unmodified official installer/loader source.

Usage: validate_dispatcharr.py OFFICIAL_SOURCE NEW_ZIP [OLD_ZIP]
Framework/database boundaries are stubs. No service or recording is contacted.
"""
import ast
import importlib.util
import json
import logging
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import types
import unittest
import zipfile

source = Path(sys.argv[1])
archive = Path(sys.argv[2])
root = Path(__file__).resolve().parents[1]
version = (root / 'VERSION').read_text().strip()
api_source = source / 'apps/plugins/api_views.py'
names = {'_compare_versions', '_sanitize_plugin_key', '_install_plugin_from_zip'}
tree = ast.parse(api_source.read_text())
nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
assert len(nodes) == len(names)
namespace = dict(os=os, re=re, zipfile=zipfile, tempfile=tempfile, shutil=shutil,
                 logger=logging.getLogger('installer'), MAX_PLUGIN_IMPORT_FILES=2000,
                 MAX_PLUGIN_IMPORT_BYTES=200 * 1024 * 1024,
                 MAX_PLUGIN_IMPORT_FILE_BYTES=200 * 1024 * 1024)
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(api_source), 'exec'), namespace)

# Load the complete official loader; only external ORM/framework boundaries are stubbed.
db = types.ModuleType('django.db')
db.close_old_connections = lambda: None
db.transaction = types.SimpleNamespace()
sys.modules['django'] = types.ModuleType('django')
sys.modules['django.db'] = db
models = types.ModuleType('disposable_dispatcharr.models')
config = types.SimpleNamespace(key="mustarrd_dvr_handoff", enabled=True, ever_enabled=True, settings={})
models.PluginConfig = types.SimpleNamespace(objects=types.SimpleNamespace(all=lambda: [config]))
sys.modules[models.__name__] = models
package = types.ModuleType('disposable_dispatcharr')
package.__path__ = [str(source / 'apps/plugins')]
sys.modules[package.__name__] = package
spec = importlib.util.spec_from_file_location('disposable_dispatcharr.loader', source / 'apps/plugins/loader.py')
loader = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = loader
spec.loader.exec_module(loader)
if 'requests' not in sys.modules:
    requests = types.ModuleType('requests')
    requests.RequestException = RuntimeError
    requests.Session = object
    sys.modules['requests'] = requests

with tempfile.TemporaryDirectory(prefix='mustarrd-disposable-') as temp:
    os.environ['DISPATCHARR_PLUGINS_DIR'] = temp
    os.environ['MUSTARRD_DVR_SCHEDULER_STATE'] = str(Path(temp) / 'scheduler.json')
    install = namespace['_install_plugin_from_zip']
    manager = loader.PluginManager()
    if len(sys.argv) > 3:
        with open(sys.argv[3], 'rb') as stream:
            previous = install(stream, temp)
        assert previous == {'success': True, 'plugin_key': 'mustarrd_dvr_handoff'}, previous
        old = json.loads((Path(temp) / 'mustarrd_dvr_handoff/plugin.json').read_text())
        assert old['version'] != version
        assert namespace['_compare_versions'](version, old['version']) > 0
    with archive.open('rb') as stream:
        result = install(stream, temp, allow_overwrite_key='mustarrd_dvr_handoff')
    assert result == {'success': True, 'plugin_key': 'mustarrd_dvr_handoff'}, result
    installed = Path(temp) / result['plugin_key']
    assert not (Path(temp) / 'mustarrd_dvr_handoff.__backup__').exists()
    manifest = json.loads((installed / 'plugin.json').read_text())
    assert manifest['version'] == version
    assert (installed / 'logo.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    plugin = manager.discover_plugins(sync_db=False, force_reload=True)[result['plugin_key']]
    assert plugin and plugin.version == version
    field = next(f for f in plugin.fields if f['id'] == 'handoff_minutes')
    assert field['default'] == 60 and 'Set to 0' in field['help_text']
    for zero in (0, '0'):
        merged = manager._merge_settings_with_defaults({'handoff_minutes': zero}, plugin.fields)
        assert merged['handoff_minutes'] == zero
    assert manager._merge_settings_with_defaults({}, plugin.fields)['handoff_minutes'] == 60
    assert plugin.instance._mustarrd_scheduler.thread is None

    # Run the actual handoff regression suite against the installed package's core,
    # rather than the checkout implementation. Fixtures isolate HTTP and DVR rows.
    sys.path.insert(0, str(root / 'tests'))
    import test_handoff_retention
    test_handoff_retention.CORE = plugin.module._core
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_handoff_retention)
    assert unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    plugin.instance.stop()
    print(f'Official Dispatcharr 0.31.0 disposable install/load/update checks passed: {version}')
