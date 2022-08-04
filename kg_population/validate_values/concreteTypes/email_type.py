from validate_values.supported_types import EMAIl
from validate_values.abstractType import Type

import re
from email_validator import validate_email, EmailNotValidError



class Email(Type):
    def get_type(self, input_str):
        try:
            if self.__valid_email(input_str):
                return EMAIl
            return False
        except:
            return False

    def __valid_email(self, email):
        # # res = re.match(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email)
        # res = re.match('^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email)
        # if res:
        #     print('Valid Email {}'.format(email))
        # else:
        #     print('INValid Email {}'.format(email))
        # return res
        try:
            # Validating the `testEmail`
            emailObject = validate_email(email)

            # If the `testEmail` is valid
            # it is updated with its normalized form
            testEmail = emailObject.email
            # print('valid {}'.format(email))
            return True
        except EmailNotValidError as errorMsg:
            # If `testEmail` is not valid
            # we print a human readable error message
            # print('INValid {}'.format(email))
            return False