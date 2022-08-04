from validate_values.supported_types import PHONE
from validate_values.abstractType import Type
from os.path import join, realpath
import pandas as pd
import phonenumbers


class Phone(Type):
    def get_type(self, input_str):
        try:
            if self.__valid_phone(input_str):
                return PHONE
            return False
        except Exception as e:
            print(e)
            return False

    def __valid_phone(self, txt):
        df = pd.read_csv(join(realpath('.'), 'validate_values', 'assets', 'country-iso.csv'), header=0, names=['Country', 'Code'])
        iso_lst = df['Code'].tolist()

        for country in iso_lst:
            try:
                z = phonenumbers.parse(txt, country)
                # print(country)
                return True
            except phonenumbers.NumberParseException:
                continue

        return False


if __name__ == '__main__':

    txts = ["+1 (650) 123-4567", "+12001230101", "+49 176 1234 5678", "+442083661177", "123", "49 176 1234 5678"]

    for txt in txts:
        obj = Phone()
        print(obj.get_type(txt))
