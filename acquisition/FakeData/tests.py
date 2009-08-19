"""Test code for data acquisition."""

from pyfusion.test.tests import BasePyfusionTestCase

# channel names in pyfusion test config file
Timeseries_test_channel_name = "test_Timeseries_channel"
multichannel_name = "test_multichannel_timeseries"


class TestFakeDataAcquisition(BasePyfusionTestCase):
    """Test the fake data acquisition used for testing."""

    def testBaseClasses(self):
        """Make sure FakeDataAcquisition is subclass of Acquisition."""
        from pyfusion.acquisition.FakeData.acq import FakeDataAcquisition
        from pyfusion.acquisition.base import BaseAcquisition
        self.assertTrue(BaseAcquisition in FakeDataAcquisition.__bases__)

    def testGetDataReturnObject(self):
        """Make sure correct data object type is returned"""
        from pyfusion.acquisition.FakeData.acq import FakeDataAcquisition
        from pyfusion import conf

        # make sure the requested data type is returned using config reference
        test_acq = FakeDataAcquisition('test_fakedata')
        from pyfusion.data.timeseries import TimeseriesData
        data_instance_1 = test_acq.getdata(self.shot_number, Timeseries_test_channel_name)
        self.assertTrue(isinstance(data_instance_1, TimeseriesData))
        
        # ...and for kwargs
        # read config as dict and pass as kwargs
        config_dict = conf.utils.get_config_as_dict('Diagnostic', Timeseries_test_channel_name)
        data_instance_2 = test_acq.getdata(self.shot_number, **config_dict)
        self.assertTrue(isinstance(data_instance_2, TimeseriesData))

        # check that the two signals are the same
        from numpy.testing import assert_array_almost_equal
        assert_array_almost_equal(data_instance_1.signal,  data_instance_2.signal) 
        assert_array_almost_equal(data_instance_1.timebase.timebase,  data_instance_2.timebase.timebase) 
        
    def testDeviceConnection(self):
        """Check that using config loads the correct acquisition."""
        from pyfusion.devices.base import Device
        test_device = Device('TestDevice')
        from pyfusion import conf, config
        acq_name = config.pf_get('Device', 'TestDevice', 'acq_name')
        test_acq = conf.utils.import_setting('Acquisition', acq_name, 'acq_class')
        self.assertTrue(isinstance(test_device.acquisition, test_acq))
        # test that device.acq shortcut works
        self.assertEqual(test_device.acquisition, test_device.acq)
        

    def test_get_data(self):
        """Check that we end up with the correct data class starting from Device"""
        from pyfusion import getDevice
        test_device = getDevice(self.listed_device)
        test_data = test_device.acquisition.getdata(self.shot_number, Timeseries_test_channel_name)
        from pyfusion.data.timeseries import TimeseriesData
        self.assertTrue(isinstance(test_data, TimeseriesData))


class TestFakeDataFetchers(BasePyfusionTestCase):
    """test DataFetcher subclasses for fake data acquisition."""

    def test_base_classes(self):
        from pyfusion.acquisition.base import BaseDataFetcher
        from pyfusion.acquisition.FakeData.fetch import SingleChannelSineDF
        self.assertTrue(BaseDataFetcher in SingleChannelSineDF.__bases__)

    def test_singlechannelsinedf(self):
        from pyfusion.acquisition.FakeData.fetch import SingleChannelSineDF
        n_samples = 1000
        sample_freq=1.e6
        amplitude = 1.0
        frequency = 3.e4
        t0 = 0.0
        test_shot = -1
        output_data_fetcher = SingleChannelSineDF(test_shot, sample_freq=sample_freq,
                                                  n_samples=n_samples,
                                                  amplitude=amplitude,
                                                  frequency=frequency,
                                                  t0 = t0)
        output_data = output_data_fetcher.fetch()
        from pyfusion.data.timeseries import TimeseriesData
        self.assertTrue(isinstance(output_data, TimeseriesData))
        from numpy import arange, sin, pi
        from numpy.testing import assert_array_almost_equal
        test_timebase = arange(t0, t0+float(n_samples)/sample_freq, 1./sample_freq)
        assert_array_almost_equal(output_data.timebase.timebase, test_timebase)
        test_signal = amplitude*sin(2*pi*frequency*test_timebase)
        assert_array_almost_equal(output_data.signal, test_signal)

class TestMultiChannel(BasePyfusionTestCase):
    """Would prefer this to be in acquisition/tests.py...."""

    def test_multichannel(self):
        from pyfusion.acquisition.FakeData.acq import FakeDataAcquisition

        test_acq = FakeDataAcquisition('test_fakedata')
        multichannel_data = test_acq.getdata(self.shot_number, multichannel_name)
        
