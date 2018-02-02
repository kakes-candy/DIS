import unittest
from classes import Patient, DBCTraject, Zorgtraject, Tijdschrijven, Diagnose



class testPatient(unittest.TestCase):
    def setUp(self):
        self.patient1 = Patient(_1430 = '73730802')
        self.Zorgtraject = Zorgtraject()

    def test_patient_write_to_string(self):
        # de lengte van de output kan worden afgeleid uit de format_definitions
        specced_length = int(self.patient1.format_definitions[-1]['Eind'])
        length_output = len(self.patient1.write_to_string())
        self.assertEqual(specced_length, length_output)

    def test_add_member(self):
        self.patient1.add_member('Zorgtraject', self.Zorgtraject)
        self.assertIn(self.Zorgtraject, self.patient1.children['Zorgtraject'])

    def test_remove_member(self):
        self.patient1.add_member('Zorgtraject', self.Zorgtraject)
        self.assertIn(self.Zorgtraject, self.patient1.children['Zorgtraject'])
        self.patient1.delete_member('Zorgtraject', self.Zorgtraject)
        self.assertNotIn(self.Zorgtraject, self.patient1.children['Zorgtraject'])

    def test_from_string(self):
        string =  '7373080201'
        self.patient = Patient().from_string(string)
        self.assertEqual(self.patient._1430, '73730802')

    def test_from_list(self):
        lijst = ['73730802', '1']
        self.patient = Patient().from_list(lijst = lijst)
        self.assertEqual(self.patient._1430, '73730802')




if __name__ == '__main__':
    unittest.main()
