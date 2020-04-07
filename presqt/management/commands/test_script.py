from django.core.management import BaseCommand

from presqt.api_v1.utilities import get_target_data
from presqt.utilities import read_file


class Command(BaseCommand):
    targets_json = read_file('presqt/specs/targets.json', True)
    target = None
    target_data = None
    target_index = None
    action_index = None
    action = None
    tokens = {}

    def handle(self, *args, **kwargs):
        self.target_index = self.index_generator([target['name'] for target in self.targets_json])
        self.target = self.get_target()
        self.action_index = self.index_generator([action for action in self.target['supported_actions'] if action])
        self.action = self.get_action()
        func = getattr(self, self.action)

        try:
            self.tokens[self.target['name']]
        except KeyError:
            self.tokens[self.target['name']] = self.get_token()

        print('Target: {}'.format(self.target['readable_name']))
        print('Action: {}'.format(self.action))
        print('Tokens: {}'.format(self.tokens))

    def get_target(self):
        valid_target = False
        target_name = None
        while not valid_target:
            print('Select target name: ')
            self.print_index_dict(self.target_index)
            selection = int(input())

            if selection in self.target_index.keys():
                valid_target = True
                target_name = self.target_index[selection]
            else:
                print('{} is not a valid selection'.format(selection))

        return get_target_data(target_name)

    def get_action(self):
        valid_action = False
        action = None
        while not valid_action:
            print('Select the action you would like to take: ')
            for key, value in self.action_index.items():
                print('{}: {}'.format(key, value))
            selection = int(input())

            if selection in self.action_index.keys():
                valid_action = True
                action =  self.action_index[selection]
            else:
                print('{} is not a valid selection.'.format(selection))

        return action

    def resource_collection(self):
        return 'resource_collection'

    def resource_detail(self):
        return 'resource_detail'

    def resource_download(self):
        return 'resource_download'

    def resource_upload(self):
        return 'resource_upload'

    def resource_transfer_out(self):
        return 'resource_transfer_out'

    def index_generator(self, items):
        index_dict = {}
        for index, item in enumerate(items):
            index_dict[index+1] = item
        return index_dict

    def print_index_dict(self, index_dict):
        for key, value in index_dict.items():
            print('{}: {}'.format(key, value))

    def get_token(self):
        token = input('Enter your {} token: '.format(self.target['readable_name']))

        # Validation

        return token

    # def validate_osf_token(self):
