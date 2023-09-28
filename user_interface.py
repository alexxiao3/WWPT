# User Interface 

class UserInterface():
    def __init__(self):
        self.stops = ['Wynyard', 'Redfern']

    def transform_inputs(self, inputs):
        if inputs[1] not in self.stops or inputs[2] not in self.stops:
            raise(ValueError('Invalid destination or departure location.'))

    def retrieve_output(self, inputs):
        pass

    def get_arrival(self, inputs):
        '''
        Expecting inputs to currently be of the form [route, departure, destination, current time, ...]
        
        Note: Yet to think about how to encode departure and destination - thinking data will probably have a stop number, etc

        '''

        # Transform inputs into usable format for model
        transformed_inputs = self.transform_inputs(inputs)

        # Get model output
        model_output = self.retrieve_output(transformed_inputs)

        # Return output in specfic format

        ##### yet to complete 

        
