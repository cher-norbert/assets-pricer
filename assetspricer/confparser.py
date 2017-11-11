# standard libraries imports
import configparser
import sys


class ConfParser(object):

    def __init__(self, conf_path):
        self.db_host = ''
        self.db_port = 0
        self.db_name = ''
        self.db_user = ''
        self.db_pass = ''
        self.main(conf_path)

    def main(self, conf_path):
        config = configparser.ConfigParser()

        try:
            with open(conf_path) as conf_file:
                config.read_file(conf_file)

                section = 'database'
                if config.has_section(section):
                    self.db_host = config.get(section, 'db_host')
                    self.db_port = int(config.get(section, 'db_port'))
                    self.db_name = config.get(section, 'db_name')
                    self.db_user = config.get(section, 'db_user')
                    self.db_pass = config.get(section, 'db_pass')

        except (configparser.Error, IOError, OSError) as err:
            sys.exit(err)

    @property
    def conf_values(self):
        return {'db_host': self.db_host,
                'db_port': self.db_port,
                'db_name': self.db_name,
                'db_user': self.db_user,
                'db_pass': self.db_pass}

# if __name__ == '__main__':
#     cp = ConfParser('./assets-pricer.ini')
#     print(cp.conf_values)
