import unittest
from classes import Patient



class testPatient(unittest.TestCase):
    def setUp(self):
        self.patient1 = Patient(_1430 = '73730802')

    def test_patient_write_to_string(self):
        # de lengte van de output kan worden afgeleid uit de format_definitions
        specced_length = int(self.patient1.format_definitions[-1]['Eind'])
        length_output = len(self.patient1.write_to_string())
        self.assertEqual(specced_length, length_output)




if __name__ == '__main__':
    unittest.main()
