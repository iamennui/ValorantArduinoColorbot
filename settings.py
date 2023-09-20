import configparser

class Settings:
    def __init__(self, config_file='settings.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def get(self, section, key):
        return self.config.get(section, key)

    def get_int(self, section, key):
        return self.config.getint(section, key)

    def get_float(self, section, key):
        return self.config.getfloat(section, key)

    def get_boolean(self, section, key):
        return self.config.getboolean(section, key)

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))

    def get_float_list(self, section, key):
        string_value = self.config.get(section, key)
        values_as_strings = string_value.strip('[]').split(',')
        return [float(value) for value in values_as_strings]

    def save(self, config_file='settings.ini'):
        with open(config_file, 'w') as f:
            self.config.write(f)
