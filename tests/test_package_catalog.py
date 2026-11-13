import io
import json
import tempfile
import threading
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from package_catalog import project_names,search_names
from library_explorer import package_info,recommended_packages,LibraryExplorer

class IndexTests(unittest.TestCase):
    def response(self,body):
        stream=io.BytesIO(body);stream.headers={};return stream
    def test_download_cache_and_offline_search(self):
        page=b'<html><body><a href="/simple/numpy/">NumPy</a><a href="/simple/pandas/">pandas</a><a>not a valid name</a></body></html>'
        with tempfile.TemporaryDirectory() as folder:
            cache=Path(folder)/'index.txt'
            with patch('package_catalog.urlopen',return_value=self.response(page)) as request:
                result=project_names(cache);self.assertEqual(result['names'],['NumPy','pandas']);self.assertFalse(result['cached']);request.assert_called_once()
            with patch('package_catalog.urlopen',side_effect=OSError('offline')):
                self.assertTrue(project_names(cache)['cached'])
                self.assertEqual(search_names(result['names'],'NUM')['names'],['NumPy'])
    def test_failed_refresh_preserves_cache(self):
        with tempfile.TemporaryDirectory() as folder:
            cache=Path(folder)/'index.txt';cache.write_text('numpy\n')
            with patch('package_catalog.urlopen',return_value=self.response(b'<html><a>partial')):
                with self.assertRaises(ValueError):project_names(cache,refresh=True)
            self.assertEqual(cache.read_text(),'numpy\n')
    def test_cancelled_download_does_not_save_partial_file(self):
        with tempfile.TemporaryDirectory() as folder:
            cache=Path(folder)/'index.txt';event=threading.Event();event.set()
            with patch('package_catalog.urlopen',return_value=self.response(b'<html><a>numpy</a></html>')):
                with self.assertRaises(InterruptedError):project_names(cache,cancelled=event)
            self.assertFalse(cache.exists())
    def test_pagination_and_exact_priority(self):
        names=['x-numpy','numpy-extra','numpy']+[f'package-{i:03}' for i in range(230)]
        self.assertEqual(search_names(names,'numpy')['names'],['numpy','numpy-extra','x-numpy'])
        page=search_names(names,'package',100);self.assertEqual(page['total'],230);self.assertEqual(len(page['names']),100);self.assertEqual(page['names'][0],'package-100')

class MetadataTests(unittest.TestCase):
    def test_compatible_older_release_metadata(self):
        latest={'info':{'name':'example','version':'2.0','requires_python':'>=4'},'releases':{'1.0':[{'requires_python':'>=3.10'}],'2.0':[{'requires_python':'>=4'}],'3.0rc1':[{}]}}
        older={'info':{'name':'example','version':'1.0','requires_python':'>=3.10'}}
        with patch('library_explorer.urlopen',side_effect=[io.BytesIO(json.dumps(latest).encode()),io.BytesIO(json.dumps(older).encode())]):
            info=package_info('example','3.15.2');self.assertEqual(info['version'],'1.0');self.assertEqual(info['requires_python'],'>=3.10')
    def test_recommendations_include_new_service_packages(self):
        names=dict(recommended_packages());self.assertIn('openai',names);self.assertIn('openpyxl',names);self.assertIn('pypdf',names)
    def test_stale_metadata_cannot_install_in_changed_interpreter(self):
        fake=types.SimpleNamespace(info={'name':'numpy','version':'2'},metadata_python='/old',studio=types.SimpleNamespace(config_data={'python':'/new'}))
        with self.assertRaises(ValueError):LibraryExplorer.selected_spec(fake)

class ExistingWizardTests(unittest.TestCase):
    def test_different_idle_plan_is_replaced(self):
        from configuration_ui import ConfigurationMixin
        from unittest.mock import Mock
        previous=Mock(busy=False,python='/python',specs=['old==1']);previous.winfo_exists.return_value=True
        fake=types.SimpleNamespace(dependency_window=previous,config_data={'python':'/python'})
        with patch('configuration_ui.DependencyWizard') as wizard:
            ConfigurationMixin.open_dependencies(fake,specs=['new==2']);previous.dispose.assert_called_once();wizard.assert_called_once()
    def test_running_install_is_not_replaced(self):
        from configuration_ui import ConfigurationMixin
        from unittest.mock import Mock
        previous=Mock(busy=True);previous.winfo_exists.return_value=True
        fake=types.SimpleNamespace(dependency_window=previous,config_data={'python':'/python'})
        with patch('configuration_ui.DependencyWizard') as wizard:
            self.assertIs(ConfigurationMixin.open_dependencies(fake,specs=['new==2']),previous);wizard.assert_not_called();previous.dispose.assert_not_called()
