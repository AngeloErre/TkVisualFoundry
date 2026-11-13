import unittest
from unittest.mock import patch
from core import new_project
from editor_guidance import quote_pair,value_context,value_items
from component_docs import reference,documentation_urls
from startup_checks import stable_versions,package_check,check_link
from packaging.specifiers import SpecifierSet
from urllib.error import HTTPError
from components import descriptor

class GuidanceTests(unittest.TestCase):
    def setUp(self):
        self.p=new_project();self.p['forms'][0]['widgets']=[{'name':'Button1','kind':'Button','props':{'text':'Button','width':42,'takefocus':True}}]
    def test_strings_quotes_and_existing_values(self):
        source='self.Button1.configure(text='
        self.assertEqual(quote_pair(source,')',self.p),"''")
        self.assertEqual(quote_pair(source,"'existing')",self.p),'')
        self.assertEqual(quote_pair(source,'value)',self.p),'')
    def test_no_rewrite_literals_comments_comparisons(self):
        for source in ['# self.Button1.configure(text=', 's="self.Button1.configure(text=', 's="""self.Button1.configure(text=', 'self.Button1.configure(text==','other.configure(text=', 'self.Button1.configure(callback=lambda text=']:
            with self.subTest(source=source):self.assertEqual(quote_pair(source,'',self.p),'')
    def test_nested_multiline(self):
        self.assertEqual(quote_pair('self.Button1.configure(\nwidth=max(1, 3),\ntext=','',self.p),"''")
        self.assertEqual(quote_pair('self.Button1.configure(text=f(foo=','',self.p),'')
    def test_numbers_booleans_and_enums(self):
        self.assertEqual(quote_pair('self.Button1.configure(width=','',self.p),'')
        self.assertEqual([r['insert'] for r in value_items('self.Button1.configure(takefocus=',self.p)],['True','False'])
        items=value_items("self.Button1.configure(state='dis",self.p)
        self.assertEqual(items[0]['insert'],'disabled');self.assertEqual(items[0]['prefix_len'],3)
    def test_other_components(self):
        self.p['forms'][0]['widgets'].append({'name':'Label1','kind':'CTkLabel','props':{}})
        self.assertEqual(quote_pair('self.Label1.configure(text=','',self.p),"''")
        self.p['components']={'Custom':{'module':'customlib','class':'Widget','defaults':{'caption':'Hello'}}}
        self.p['forms'][0]['widgets'].append({'name':'Custom1','kind':'Custom','props':{}})
        self.assertEqual(quote_pair('self.Custom1.configure(caption=','',self.p),"''")

class DocumentationTests(unittest.TestCase):
    def test_reference_and_custom_url(self):
        p=new_project();ref=reference({'name':'Button1','kind':'Button','props':{}},p)
        self.assertIn('configure',ref['text']);self.assertIn('tkinter',ref['url'])
        p['components']={'Custom':{'module':'somewhere','class':'Widget','documentation':'https://example.org/help'}}
        self.assertIn('https://example.org/help',documentation_urls(p))
        with self.assertRaises(ValueError):descriptor({'module':'foo','class':'Bar','documentation':'javascript:bad'})
    def test_every_builtin_has_offline_reference(self):
        from components import registry
        p=new_project()
        for kind in registry(p):
            with self.subTest(kind=kind):self.assertTrue(reference({'name':'Example','kind':kind,'props':{}},p)['text'])

class StartupTests(unittest.TestCase):
    def test_only_stable_compatible_not_yanked(self):
        data={'releases':{'1.0':[{}],'1.1':[{'yanked':True}],'2.0rc1':[{}],'2.0':[{'requires_python':'>=4'}],'1.2':[{'requires_python':'>=3.10'}]}}
        self.assertEqual(stable_versions(data,SpecifierSet('<2'),'3.15.2'),'1.2')
        self.assertEqual(stable_versions(data,SpecifierSet('<1.2'),'3.15.2'),'1.0')
    def test_offline_missing_is_not_hidden(self):
        from packaging.requirements import Requirement
        with patch('urllib.request.urlopen',side_effect=OSError('offline')):
            row=package_check('foo',None,[Requirement('foo>=1')],'3.15.2')
        self.assertEqual(row['status'],'missing');self.assertIn('error',row)
    def test_broken_vs_restricted_links(self):
        for code,status in [(404,'broken'),(410,'broken'),(403,'unverified'),(503,'unverified')]:
            with patch('urllib.request.urlopen',side_effect=HTTPError('https://example.org',code,'failure',{},None)):
                self.assertEqual(check_link('https://example.org')['status'],status)
