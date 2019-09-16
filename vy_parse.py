#!/usr/bin/python3
from pathlib import Path
import re
import subprocess
import ast
import json

class CodeFile:
    """
        The class to define contract
        @warning this need to run with vyper compiler already install and running on your terminal
    """
    def __init__(self, file_path):
        """
        file_path: the path to the file
        file_code: the code of the file in string and remove newline
        by replace \n to \\n so we just only deal with a long 1 line string
        file_name: the name of file
        """
        self.file_path = file_path
        # replace string so that we can work on 1 line instead of 2
        self.file_code = Path(file_path).open().read().replace('\n', '\\n')
        self.file_name = Path(file_path).stem


    def __get_method_id(self):
        """
            @dev get all the function method from the contract
            @return the list of function method
        """
        my_cmd = f'vyper -f method_identifiers {self.file_path}'
        method_id = subprocess.run(my_cmd.split(), capture_output=True).stdout.decode('utf-8')
        method_id = method_id.replace("\n", "")
        method_dict = ast.literal_eval(method_id)

        return list(method_dict.keys())


    def __find_def(self):
        """
            @dev Find the function name
            @return the list of function_name appear in the contract
        """
        code_file = self.file_code
        # The first group is the function name and the second group is the function body
        p = re.compile(r'def (.+?)\(.+?\\n(.+?)\\n([a-zA-Z@#0-9]|$)')
        result = p.findall(code_file)

        return result


    def __find_comment_in_def(self):
        """
            @dev find the comment doc in each function
            @return the dictionary where key is the function method
            and the value is the comment of that function
        """
        code_body = self.__find_def()

        result = code_body
        function_name = [result[i][0] for i in range(len(result))]
        function_body = [result[i][1] for i in range(len(result))]
        p = re.compile(r'\"\"\"(.*?)\"\"\"')
        method_list = self.__get_method_id()

        result_dict = {}

        for pos, corpus in enumerate(function_body):
            function_document = p.findall(corpus)

            if function_document:
                for each_func in method_list:
                    if function_name[pos] in each_func:
                        result_dict[each_func] = function_document[0].replace('\\n', '')
                        result_dict[each_func] = ' '.join(result_dict[each_func].split())
                        break

        return result_dict


    def get_user_doc_in_json(self):
        """
        @dev Find inside the comment of each function the @notice
        and then after that find the context of it
        @return the dictionary in the form:

        {
            'methods':
            {
                'function_name(type, type)':
                {
                    'notice': 'The context of @notice'
                }
            }
        }
        """
        file_document_dict = self.__find_comment_in_def()
        regex_notice = re.compile(r'@notice (.*?)(?= @|$)')
        result_dict = {'methods': {}}

        for each_func in file_document_dict:
            result_dict['methods'][each_func] = {}
            # In each function's document find @notice and its context
            result = regex_notice.findall(file_document_dict[each_func])

            for each_result in result:
                result_dict['methods'][each_func] = {'notice': f'{each_result}'}

        return result_dict


    def get_dev_doc_in_json(self):
        """
        @dev Find inside the comment of each function the @notice
        and then after that find the context of it
        @return the dictionary in the form:

        {
            'methods':
            {
                'function_name(type, type)':
                {
                    'author': 'the author of the function'
                    'dev': 'The context of @dev'
                    'param':
                    {
                        'first_param': 'context of first param'
                        'second_param': 'context of second param'
                    }
                }
            }
        }
        """
        file_document_dict = self.__find_comment_in_def()
        regex_notice = re.compile(r'@(\w+) (.*?)(?= @|$)')
        result_dict = {'methods': {}}

        for each_func in file_document_dict:
            result_dict['methods'][each_func] = {}
            # In each function's document find @dev, @param, @author, @returns, @notice
            regex_result = regex_notice.findall(file_document_dict[each_func])

            # if the result is @notice remove it
            dev_doc_dict = []
            for each_comment in regex_result:
                if each_comment[0] != 'notice':
                    dev_doc_dict.append(each_comment)

            # find in each_func turn tag content into dict in order: @author, @dev, @param
            for each_comment in dev_doc_dict:
                # If the tag is @author
                if each_comment[0] == 'author':
                    result_dict['methods'][each_func]['author'] = each_comment[1]

                # If the tag is @dev
                if each_comment[0] == 'dev':
                    result_dict['methods'][each_func]['dev'] = each_comment[1]

                # If the tag is @params
                if each_comment[0] == 'param':
                    # Check if params dict have exists if not create one
                    if 'params' not in result_dict['methods'][each_func]:
                        result_dict['methods'][each_func]['params'] = {}

                    param_regex = re.compile(r'^(\w+) (.*)$')
                    result_param = param_regex.findall(each_comment[1])
                    param_name = result_param[0][0]
                    param_body = result_param[0][1]

                    param_dict = {param_name: param_body}
                    result_dict['methods'][each_func]['params'].update(param_dict)

                # If the tag is @return
                if each_comment[0] == 'return':
                    result_dict['methods'][each_func]['return'] = each_comment[1]

        return result_dict


    def save(self, file_name):
        """
            @dev Save the dictionary of dev/user doc into json file
            if the file_name is empty then use the input file's name
        """
        if file_name is None:
            file_name = f'{self.file_name}.json'

        data = self.get_user_doc_in_json()

        with open(file_name, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)


    def print_json_user(self):
        """
        @dev print out the user document for code in json like solidity
        """
        print(json.dumps(self.get_user_doc_in_json(), indent=4, sort_keys=True))


    def print_json_dev(self):
        """
        @dev print out the dev document for code in json like solidity
        """
        print(json.dumps(self.get_dev_doc_in_json(), indent=4, sort_keys=True))
