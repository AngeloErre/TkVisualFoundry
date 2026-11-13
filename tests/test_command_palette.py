import unittest
from unittest.mock import Mock
from command_palette import menu_commands,matching_commands
class CommandPaletteTests(unittest.TestCase):
    def test_bilingual_search_and_accent_normalization(self):
        rows=menu_commands([('File',[('Salva',lambda:None),('Apri progetto…',lambda:None)]),('Vista',[('Proprietà avanzate',lambda:None)])])
        self.assertEqual(matching_commands(rows,'save')[0]['name'],'Salva')
        self.assertEqual(matching_commands(rows,'open project')[0]['name'],'Apri progetto…')
        self.assertEqual(matching_commands(rows,'PROPRIETA')[0]['category'],'Vista')
        english=menu_commands([('File',[('Save',lambda:None)])]);self.assertEqual(matching_commands(english,'salva')[0]['name'],'Save')
    def test_discovery_never_invokes_actions(self):
        action=Mock(side_effect=AssertionError('Executed during search'))
        rows=menu_commands([('PIP',[('Installa un pacchetto…',action)])]);self.assertEqual(len(matching_commands(rows,'pip install')),1);action.assert_not_called()
        self.assertEqual(matching_commands(rows,'unknown'),[])
    def test_recent_commands_and_exact_label_priority(self):
        rows=menu_commands([('File',[('Salva con nome…',lambda:None),('Salva',lambda:None),('Apri',lambda:None)])])
        self.assertEqual([r['id'] for r in matching_commands(rows,'',[2,1])],[2,1,0])
        self.assertEqual(matching_commands(rows,'salva',[0])[0]['name'],'Salva')
