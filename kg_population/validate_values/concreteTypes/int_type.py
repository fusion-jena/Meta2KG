from validate_values.supported_types import INT
from validate_values.abstractType import Type


class Int(Type):

    def get_type(self, input_str):
        try:
            x = int(input_str)
            if x:
                return INT
            return False
        except:
            return False
