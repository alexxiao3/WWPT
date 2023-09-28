# Add parent directory to path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import unittest
from datetime import datetime
from user_interface import UserInterface
from datetime import timedelta

class TestInterfaceInputs(unittest.TestCase):
    def setUp(self):
        self.ui = UserInterface()

    def test_invalid_route(self):
        # Test that an invalid route raises a ValueError

        with self.assertRaises(ValueError):
            self.ui.transform_inputs([109023, 'Redfern', 'Wynyard', datetime.now()])

    
    def test_departure(self):
        # Test that an invalid departure raises a ValueError

        with self.assertRaises(ValueError):
            self.ui.transform_inputs([502, 'Blackfern', 'Wynyard', datetime.now()])
    

    def test_arrival(self):
        # Test that an invalid arrival raises a ValueError

        with self.assertRaises(ValueError):
            self.ui.transform_inputs([502, 'Redfern', 'Wyngarden', datetime.now()])



class TestInterfaceOutputs(unittest.TestCase):
    def setUp(self):
        self.ui = UserInterface()

    def test_output_format(self):
        # Test output format is in hours and minutes

        inputs = [502, 'Redfern', 'Wynyard', datetime.now()]
        output_time = self.ui.get_arrival(inputs)
        if bool(datetime.strptime(output_time, '%H-%M')):
            self.assertTrue(True)
        else:
            self.assertTrue(False)


    def test_delay_format(self):
        # Test delay outputted by retrieve_output method is in a timedelta format
        inputs = [502, 'Redfern', 'Wynyard', datetime.now()]
        transformed_inputs = self.ui.transform_inputs(inputs)
        delay = self.ui.retrieve_output(transformed_inputs)

        self.assertTrue(delay, timedelta)


    def test_output_value(self):
        # Test output value consistent with delay outputted by model
        inputs = [502, 'Redfern', 'Wynyard', datetime.now()]

        transformed_inputs = self.ui.transform_inputs(inputs)
        delay = self.ui.retrieve_output(transformed_inputs)
        output_time = self.ui.get_arrival(inputs)

        # Check:
        self.assertEqual(inputs[3] + delay, output_time)
    


if __name__ == '__main__':    
    unittest.main()
