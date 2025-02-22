# -*- coding: utf-8 -*-
"""
Copyright 2016 Telefónica Investigación y Desarrollo, S.A.U.
This file is part of Toolium.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os

import mock
import pytest
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from toolium.config_driver import ConfigDriver
from toolium.config_parser import ExtendedConfigParser


@pytest.fixture
def config():
    config_parser = ExtendedConfigParser()
    config_parser.add_section('Server')
    config_parser.add_section('Driver')
    return config_parser


@pytest.fixture
def utils():
    utils = mock.MagicMock()
    utils.get_driver_name.return_value = 'firefox'
    return utils


def test_create_driver_local_not_configured(config, utils):
    config.set('Driver', 'type', 'firefox')
    utils.get_driver_name.return_value = 'firefox'
    config_driver = ConfigDriver(config, utils)
    config_driver._create_local_driver = lambda: 'local driver mock'
    config_driver._create_remote_driver = lambda: 'remote driver mock'

    driver = config_driver.create_driver()

    assert driver == 'local driver mock'


def test_create_driver_local(config, utils):
    config.set('Server', 'enabled', 'false')
    config.set('Driver', 'type', 'firefox')
    utils.get_driver_name.return_value = 'firefox'
    config_driver = ConfigDriver(config, utils)
    config_driver._create_local_driver = lambda: 'local driver mock'
    config_driver._create_remote_driver = lambda: 'remote driver mock'

    driver = config_driver.create_driver()

    assert driver == 'local driver mock'


def test_create_driver_remote(config, utils):
    config.set('Server', 'enabled', 'true')
    config.set('Driver', 'type', 'firefox')
    utils.get_driver_name.return_value = 'firefox'
    config_driver = ConfigDriver(config, utils)
    config_driver._create_local_driver = lambda: 'local driver mock'
    config_driver._create_remote_driver = lambda: 'remote driver mock'

    driver = config_driver.create_driver()

    assert driver == 'remote driver mock'


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_local_driver_chrome(webdriver_mock, config, utils):
    config.set('Driver', 'type', 'chrome')
    config.set('Driver', 'chrome_driver_path', '/tmp/driver')
    utils.get_driver_name.return_value = 'chrome'
    config_driver = ConfigDriver(config, utils)
    config_driver._create_chrome_options = lambda: 'chrome options'
    config_driver._add_chrome_options_to_capabilities = lambda x: None

    config_driver._create_local_driver()
    webdriver_mock.Chrome.assert_called_once_with('/tmp/driver', desired_capabilities=DesiredCapabilities.CHROME)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_local_driver_chrome_multiple_options(webdriver_mock, config, utils):
    # From goog:chromeOptions in Capabilities section
    options_from_capabilities = {
        'excludeSwitches': ['enable-automation'], 'useAutomationExtension': False,
        'prefs': {'download.default_directory': '/this_value_will_be_overwritten',
                  'download.prompt_for_download': False}
    }
    # From ChromePreferences, ChromeMobileEmulation, ChromeArguments and Chrome sections
    options_from_sections = {
        'prefs': {'download.default_directory': '/tmp'},
        'mobileEmulation': {'deviceName': 'Google Nexus 5'},
        'args': ['user-data-dir=C:\\Users\\USERNAME\\AppData\\Local\\Google\\Chrome\\User Data'],
        'binary': '/usr/local/chrome_beta/chrome'
    }
    # Merged chrome options
    final_chrome_options = {
        'excludeSwitches': ['enable-automation'], 'useAutomationExtension': False,
        'prefs': {'download.default_directory': '/tmp', 'download.prompt_for_download': False},
        'mobileEmulation': {'deviceName': 'Google Nexus 5'},
        'args': ['user-data-dir=C:\\Users\\USERNAME\\AppData\\Local\\Google\\Chrome\\User Data'],
        'binary': '/usr/local/chrome_beta/chrome'
    }

    config.set('Driver', 'type', 'chrome')
    config.set('Driver', 'chrome_driver_path', '/tmp/driver')
    config.add_section('Capabilities')
    config.set('Capabilities', 'goog:chromeOptions', str(options_from_capabilities))
    utils.get_driver_name.return_value = 'chrome'
    config_driver = ConfigDriver(config, utils)

    # Chrome options mock
    chrome_options = mock.MagicMock()
    chrome_options.to_capabilities.return_value = {'goog:chromeOptions': options_from_sections}
    config_driver._create_chrome_options = mock.MagicMock(return_value=chrome_options)

    config_driver._create_local_driver()
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['goog:chromeOptions'] = final_chrome_options
    webdriver_mock.Chrome.assert_called_once_with('/tmp/driver', desired_capabilities=capabilities)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_local_driver_safari(webdriver_mock, config, utils):
    config.set('Driver', 'type', 'safari')
    utils.get_driver_name.return_value = 'safari'
    config_driver = ConfigDriver(config, utils)

    config_driver._create_local_driver()
    webdriver_mock.Safari.assert_called_once_with(desired_capabilities=DesiredCapabilities.SAFARI)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_local_driver_iexplore(webdriver_mock, config, utils):
    config.set('Driver', 'type', 'iexplore')
    config.set('Driver', 'explorer_driver_path', '/tmp/driver')
    utils.get_driver_name.return_value = 'iexplore'
    config_driver = ConfigDriver(config, utils)

    config_driver._create_local_driver()
    webdriver_mock.Ie.assert_called_once_with('/tmp/driver', capabilities=DesiredCapabilities.INTERNETEXPLORER)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_local_driver_edge(webdriver_mock, config, utils):
    config.set('Driver', 'type', 'edge')
    config.set('Driver', 'edge_driver_path', '/tmp/driver')
    utils.get_driver_name.return_value = 'edge'
    config_driver = ConfigDriver(config, utils)

    config_driver._create_local_driver()
    webdriver_mock.Edge.assert_called_once_with('/tmp/driver', capabilities=DesiredCapabilities.EDGE)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
def test_create_local_driver_android(config, utils):
    config.set('Driver', 'type', 'android')
    utils.get_driver_name.return_value = 'android'
    config_driver = ConfigDriver(config, utils)
    config_driver._create_remote_driver = lambda: 'remote driver mock'

    driver = config_driver._create_local_driver()
    assert driver == 'remote driver mock'


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
def test_create_local_driver_ios(config, utils):
    config.set('Driver', 'type', 'ios')
    utils.get_driver_name.return_value = 'ios'
    config_driver = ConfigDriver(config, utils)
    config_driver._create_remote_driver = lambda: 'remote driver mock'

    driver = config_driver._create_local_driver()
    assert driver == 'remote driver mock'


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
def test_create_local_driver_iphone(config, utils):
    config.set('Driver', 'type', 'iphone')
    utils.get_driver_name.return_value = 'iphone'
    config_driver = ConfigDriver(config, utils)
    config_driver._create_remote_driver = lambda: 'remote driver mock'

    driver = config_driver._create_local_driver()
    assert driver == 'remote driver mock'


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
def test_create_local_driver_unknown_driver(config, utils):
    config.set('Driver', 'type', 'unknown')
    utils.get_driver_name.return_value = 'unknown'
    config_driver = ConfigDriver(config, utils)

    with pytest.raises(Exception) as excinfo:
        config_driver._create_local_driver()
    assert 'Unknown driver unknown' == str(excinfo.value)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_remote_driver_firefox(webdriver_mock, config, utils):
    config.set('Driver', 'type', 'firefox')
    server_url = 'http://10.20.30.40:5555'
    utils.get_server_url.return_value = server_url
    utils.get_driver_name.return_value = 'firefox'
    config_driver = ConfigDriver(config, utils)

    # Firefox profile mock
    class ProfileMock(object):
        encoded = 'encoded profile'

    config_driver._create_firefox_profile = mock.MagicMock(return_value=ProfileMock())

    config_driver._create_remote_driver()
    capabilities = DesiredCapabilities.FIREFOX.copy()
    capabilities['firefox_profile'] = 'encoded profile'
    webdriver_mock.Remote.assert_called_once_with(command_executor='%s/wd/hub' % server_url,
                                                  desired_capabilities=capabilities)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_remote_driver_chrome(webdriver_mock, config, utils):
    config.set('Driver', 'type', 'chrome')
    server_url = 'http://10.20.30.40:5555'
    utils.get_server_url.return_value = server_url
    utils.get_driver_name.return_value = 'chrome'
    config_driver = ConfigDriver(config, utils)

    # Chrome options mock
    chrome_options = mock.MagicMock()
    chrome_options.to_capabilities.return_value = {'goog:chromeOptions': 'chrome options'}
    config_driver._create_chrome_options = mock.MagicMock(return_value=chrome_options)

    config_driver._create_remote_driver()
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['goog:chromeOptions'] = 'chrome options'
    webdriver_mock.Remote.assert_called_once_with(command_executor='%s/wd/hub' % server_url,
                                                  desired_capabilities=capabilities)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_remote_driver_chrome_multiple_options(webdriver_mock, config, utils):
    # From goog:chromeOptions in Capabilities section
    options_from_capabilities = {
        'excludeSwitches': ['enable-automation'], 'useAutomationExtension': False,
        'prefs': {'download.default_directory': '/this_value_will_be_overwritten',
                  'download.prompt_for_download': False}
    }
    # From ChromePreferences, ChromeMobileEmulation, ChromeArguments and Chrome sections
    options_from_sections = {
        'prefs': {'download.default_directory': '/tmp'},
        'mobileEmulation': {'deviceName': 'Google Nexus 5'},
        'args': ['user-data-dir=C:\\Users\\USERNAME\\AppData\\Local\\Google\\Chrome\\User Data'],
        'binary': '/usr/local/chrome_beta/chrome'
    }
    # Merged chrome options
    final_chrome_options = {
        'excludeSwitches': ['enable-automation'], 'useAutomationExtension': False,
        'prefs': {'download.default_directory': '/tmp', 'download.prompt_for_download': False},
        'mobileEmulation': {'deviceName': 'Google Nexus 5'},
        'args': ['user-data-dir=C:\\Users\\USERNAME\\AppData\\Local\\Google\\Chrome\\User Data'],
        'binary': '/usr/local/chrome_beta/chrome'
    }

    config.set('Driver', 'type', 'chrome')
    config.add_section('Capabilities')
    config.set('Capabilities', 'goog:chromeOptions', str(options_from_capabilities))
    server_url = 'http://10.20.30.40:5555'
    utils.get_server_url.return_value = server_url
    utils.get_driver_name.return_value = 'chrome'
    config_driver = ConfigDriver(config, utils)

    # Chrome options mock
    chrome_options = mock.MagicMock()
    chrome_options.to_capabilities.return_value = {'goog:chromeOptions': options_from_sections}
    config_driver._create_chrome_options = mock.MagicMock(return_value=chrome_options)

    config_driver._create_remote_driver()
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['goog:chromeOptions'] = final_chrome_options
    webdriver_mock.Remote.assert_called_once_with(command_executor='%s/wd/hub' % server_url,
                                                  desired_capabilities=capabilities)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_remote_driver_chrome_old_selenium(webdriver_mock, config, utils):
    config.set('Driver', 'type', 'chrome')
    server_url = 'http://10.20.30.40:5555'
    utils.get_server_url.return_value = server_url
    utils.get_driver_name.return_value = 'chrome'
    config_driver = ConfigDriver(config, utils)

    # Chrome options mock
    chrome_options = mock.MagicMock()
    chrome_options.to_capabilities.return_value = {'chromeOptions': 'chrome options'}
    config_driver._create_chrome_options = mock.MagicMock(return_value=chrome_options)

    config_driver._create_remote_driver()
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['chromeOptions'] = 'chrome options'
    webdriver_mock.Remote.assert_called_once_with(command_executor='%s/wd/hub' % server_url,
                                                  desired_capabilities=capabilities)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_remote_driver_safari(webdriver_mock, config, utils):
    config.set('Driver', 'type', 'safari')
    server_url = 'http://10.20.30.40:5555'
    utils.get_server_url.return_value = server_url
    utils.get_driver_name.return_value = 'safari'
    config_driver = ConfigDriver(config, utils)

    config_driver._create_remote_driver()
    webdriver_mock.Remote.assert_called_once_with(command_executor='%s/wd/hub' % server_url,
                                                  desired_capabilities=DesiredCapabilities.SAFARI)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_remote_driver_iexplore(webdriver_mock, config, utils):
    config.set('Driver', 'type', 'iexplore')
    server_url = 'http://10.20.30.40:5555'
    utils.get_server_url.return_value = server_url
    utils.get_driver_name.return_value = 'iexplore'
    config_driver = ConfigDriver(config, utils)

    config_driver._create_remote_driver()
    webdriver_mock.Remote.assert_called_once_with(command_executor='%s/wd/hub' % server_url,
                                                  desired_capabilities=DesiredCapabilities.INTERNETEXPLORER)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_remote_driver_edge(webdriver_mock, config, utils):
    config.set('Driver', 'type', 'edge')
    server_url = 'http://10.20.30.40:5555'
    utils.get_server_url.return_value = server_url
    utils.get_driver_name.return_value = 'edge'
    config_driver = ConfigDriver(config, utils)

    config_driver._create_remote_driver()
    webdriver_mock.Remote.assert_called_once_with(command_executor='%s/wd/hub' % server_url,
                                                  desired_capabilities=DesiredCapabilities.EDGE)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.appiumdriver')
def test_create_remote_driver_android(appiumdriver_mock, config, utils):
    config.set('Driver', 'type', 'android')
    config.add_section('AppiumCapabilities')
    config.set('AppiumCapabilities', 'automationName', 'Appium')
    config.set('AppiumCapabilities', 'platformName', 'Android')
    server_url = 'http://10.20.30.40:5555'
    utils.get_server_url.return_value = server_url
    utils.get_driver_name.return_value = 'android'
    config_driver = ConfigDriver(config, utils)

    config_driver._create_remote_driver()
    capabilities = {'automationName': 'Appium', 'platformName': 'Android'}
    appiumdriver_mock.Remote.assert_called_once_with(command_executor='%s/wd/hub' % server_url,
                                                     desired_capabilities=capabilities)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.appiumdriver')
def test_create_remote_driver_ios(appiumdriver_mock, config, utils):
    config.set('Driver', 'type', 'ios')
    config.add_section('AppiumCapabilities')
    config.set('AppiumCapabilities', 'automationName', 'Appium')
    config.set('AppiumCapabilities', 'platformName', 'iOS')
    server_url = 'http://10.20.30.40:5555'
    utils.get_server_url.return_value = server_url
    utils.get_driver_name.return_value = 'ios'
    config_driver = ConfigDriver(config, utils)

    config_driver._create_remote_driver()
    capabilities = {'automationName': 'Appium', 'platformName': 'iOS'}
    appiumdriver_mock.Remote.assert_called_once_with(command_executor='%s/wd/hub' % server_url,
                                                     desired_capabilities=capabilities)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.appiumdriver')
def test_create_remote_driver_iphone(appiumdriver_mock, config):
    config.set('Driver', 'type', 'iphone')
    config.add_section('AppiumCapabilities')
    config.set('AppiumCapabilities', 'automationName', 'Appium')
    config.set('AppiumCapabilities', 'platformName', 'iOS')
    server_url = 'http://10.20.30.40:5555'
    utils = mock.MagicMock()
    utils.get_server_url.return_value = server_url
    utils.get_driver_name.return_value = 'iphone'
    config_driver = ConfigDriver(config, utils)

    config_driver._create_remote_driver()
    capabilities = {'automationName': 'Appium', 'platformName': 'iOS'}
    appiumdriver_mock.Remote.assert_called_once_with(command_executor='%s/wd/hub' % server_url,
                                                     desired_capabilities=capabilities)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_remote_driver_version_platform(webdriver_mock, config, utils):
    config.set('Driver', 'type', 'iexplore-11-on-WIN10')
    server_url = 'http://10.20.30.40:5555'
    utils.get_server_url.return_value = server_url
    utils.get_driver_name.return_value = 'iexplore'
    config_driver = ConfigDriver(config, utils)

    config_driver._create_remote_driver()
    capabilities = DesiredCapabilities.INTERNETEXPLORER
    capabilities['browserVersion'] = '11'
    capabilities['platformName'] = 'WIN10'
    webdriver_mock.Remote.assert_called_once_with(command_executor='%s/wd/hub' % server_url,
                                                  desired_capabilities=capabilities)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_remote_driver_version(webdriver_mock, config, utils):
    config.set('Driver', 'type', 'iexplore-11')
    server_url = 'http://10.20.30.40:5555'
    utils.get_server_url.return_value = server_url
    utils.get_driver_name.return_value = 'iexplore'
    config_driver = ConfigDriver(config, utils)

    config_driver._create_remote_driver()
    capabilities = DesiredCapabilities.INTERNETEXPLORER.copy()
    capabilities['browserVersion'] = '11'
    webdriver_mock.Remote.assert_called_once_with(command_executor='%s/wd/hub' % server_url,
                                                  desired_capabilities=capabilities)


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_remote_driver_capabilities(webdriver_mock, config, utils):
    config.set('Driver', 'type', 'iexplore-11')
    config.add_section('Capabilities')
    config.set('Capabilities', 'browserVersion', '11')
    server_url = 'http://10.20.30.40:5555'
    utils.get_server_url.return_value = server_url
    utils.get_driver_name.return_value = 'iexplore'
    config_driver = ConfigDriver(config, utils)

    config_driver._create_remote_driver()
    capabilities = DesiredCapabilities.INTERNETEXPLORER.copy()
    capabilities['browserVersion'] = '11'
    webdriver_mock.Remote.assert_called_once_with(command_executor='%s/wd/hub' % server_url,
                                                  desired_capabilities=capabilities)


def test_convert_property_type_true(config, utils):
    config_driver = ConfigDriver(config, utils)
    value = 'True'
    assert config_driver._convert_property_type(value) is True


def test_convert_property_type_false(config, utils):
    config_driver = ConfigDriver(config, utils)
    value = 'False'
    assert config_driver._convert_property_type(value) is False


def test_convert_property_type_dict(config, utils):
    config_driver = ConfigDriver(config, utils)
    value = "{'a': 5}"
    assert config_driver._convert_property_type(value) == {'a': 5}


def test_convert_property_type_int(config, utils):
    config_driver = ConfigDriver(config, utils)
    value = '5'
    assert config_driver._convert_property_type(value) == 5


def test_convert_property_type_str(config, utils):
    config_driver = ConfigDriver(config, utils)
    value = 'string'
    assert config_driver._convert_property_type(value) == value


def test_convert_property_type_list(config, utils):
    config_driver = ConfigDriver(config, utils)
    value = "[1, 2, 3]"
    assert config_driver._convert_property_type(value) == [1, 2, 3]


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_chrome_options(webdriver_mock, config, utils):
    config.add_section('ChromePreferences')
    config.set('ChromePreferences', 'download.default_directory', '/tmp')
    config.add_section('ChromeMobileEmulation')
    config.set('ChromeMobileEmulation', 'deviceName', 'Google Nexus 5')
    config.add_section('ChromeArguments')
    config.set('ChromeArguments', 'lang', 'es')
    config.add_section('ChromeExtensions')
    config.set('ChromeExtensions', 'firebug', 'resources/firebug-lite.crx')
    config_driver = ConfigDriver(config, utils)

    config_driver._create_chrome_options()
    webdriver_mock.ChromeOptions.assert_called_once_with()
    webdriver_mock.ChromeOptions().add_experimental_option.assert_has_calls(
        [mock.call('prefs', {'download.default_directory': '/tmp'}),
         mock.call('mobileEmulation', {'deviceName': 'Google Nexus 5'})]
    )
    webdriver_mock.ChromeOptions().add_argument.assert_called_once_with('lang=es')
    webdriver_mock.ChromeOptions().add_extension.assert_called_once_with('resources/firebug-lite.crx')


@pytest.mark.skip("DesiredCapabilities must be updated to be compatible with Selenium 4")
@mock.patch('toolium.config_driver.webdriver')
def test_create_chrome_options_headless(webdriver_mock, config, utils):
    config.set('Driver', 'headless', 'true')
    config_driver = ConfigDriver(config, utils)

    config_driver._create_chrome_options()
    webdriver_mock.ChromeOptions.assert_called_once_with()
    if os.name == 'nt':
        webdriver_mock.ChromeOptions().add_argument.assert_has_calls([mock.call('--headless=new'),
                                                                      mock.call('--disable-gpu')])
    else:
        webdriver_mock.ChromeOptions().add_argument.assert_called_once_with('--headless=new')
