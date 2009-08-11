"""Tests for pyfusion configuration files and parser."""

from pyfusion.test.tests import BasePyfusionTestCase

class TestConfigFileSectionNames(BasePyfusionTestCase):
    """Check section name conformity in configuration files.

    Allowed config section names must correspond to those
    described in the documentation (which should be the same
    list as pyfusion.conf.allowed_section_types).

    """
    def testSectionNames(self):
        from pyfusion.conf import allowed_section_types
        from pyfusion import config
        from pyfusion.conf.exceptions import DisallowedSectionType, ConfigSectionSyntaxError
        config.check_section_types(allowed_section_types)
        self.assertFalse(
            self.unlisted_config_section_type in allowed_section_types)
        config.add_section(
            "%s:%s" %(self.unlisted_config_section_type, 'dummy'))
        self.assertRaises(DisallowedSectionType,
                          config.check_section_types,
                          allowed_section_types)
        config.check_section_syntax()
        config.add_section("xxx")
        self.assertRaises(
            ConfigSectionSyntaxError, config.check_section_syntax)

class TestPyfusionConfigParser(BasePyfusionTestCase):
    """Test pyfusion customised config file parser."""

    def testBaseClass(self):
        from pyfusion.conf import PyfusionConfigParser
        from ConfigParser import ConfigParser
        self.assertTrue(ConfigParser in PyfusionConfigParser.__bases__)
        
    def test_pf_has_section(self):
        from pyfusion import config
        self.assertTrue(config.pf_has_section('Device', self.listed_device))
        self.assertFalse(config.pf_has_section('Device', self.unlisted_device))


class TestImportSetting(BasePyfusionTestCase):
    """Test import_setting function."""

    def test_import_setting_with_fakedata_acquisition(self):
        from pyfusion.conf.utils import import_setting
        acq_from_config = import_setting('Acquisition',
                                         'test_fakedata', 'acq_class')
        from pyfusion.acquisition.FakeData.acq import FakeDataAcquisition
        self.assertEqual(acq_from_config, FakeDataAcquisition)

class TestImportFromString(BasePyfusionTestCase):
    """Test import_from_str fuction."""

    def test_import_from_str(self):
        from pyfusion.conf.utils import import_from_str
        string_value = "pyfusion.acquisition.FakeData.acq.FakeDataAcquisition"
        from pyfusion.acquisition.FakeData.acq import FakeDataAcquisition
        self.assertEqual(import_from_str(string_value), FakeDataAcquisition)

class TestKeywordArgConfigHandler(BasePyfusionTestCase):
    """Test the function which chooses from kwargs oor config vars."""

    def test_kwarg_config_handler(self):
        from pyfusion.conf.utils import kwarg_config_handler
        from pyfusion import config
        # config values should be overridden by kwargs
        # test against [Device:TestDevice]
        # take acquisition from config, and database from kwarsg
        # give an additional kwarg not in config

        test_kwargs = {'database': 'dummy_database',
                       'other_var': 'other_val'}
        output_vars = kwarg_config_handler('Device',
                                           'TestDevice', **test_kwargs)
        #make sure test_kwargs are returned
        for kwarg_item in test_kwargs.items():
            self.assertTrue(kwarg_item in output_vars.items())
        # make sure that config vars not in test_kwargs are included in kwargs
        for config_var in config.pf_options('Device', 'TestDevice'):
            if not config_var in test_kwargs.keys():
                self.assertEqual(output_vars[config_var],
                                 config.pf_get('Device',
                                               'TestDevice', config_var))


class TestVariableTypes(BasePyfusionTestCase):
    """Check that config parser returns correct types for settings."""
    def test_return_correct_type(self):
        from pyfusion import config
        # a setting of type float:
        sample_freq = config.pf_get('Diagnostic', 'test_types', 'sample_freq')
        self.assertTrue(type(sample_freq) == float)
        # a setting of type int:
        n_samples = config.pf_get('Diagnostic', 'test_types', 'n_samples')
        self.assertTrue(type(n_samples) == int)
        # a setting of type boolean:
        test_bool = config.pf_get('Diagnostic', 'test_types', 'testboolean')
        self.assertTrue(type(test_bool) == bool)
        # test unknown type raises exception
        from pyfusion.conf.exceptions import UnknownVariableTypeError
        self.assertRaises(UnknownVariableTypeError,
                          config.pf_get,
                          'Diagnostic',
                          'test_types',
                          'unknowntype')
        
