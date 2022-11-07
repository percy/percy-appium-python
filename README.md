# percy-appium-python
![Test](https://github.com/percy/percy-appium-python/workflows/Test/badge.svg)

[Percy](https://percy.io) visual testing for Python Appium.

## Installation

npm install `@percy/cli`:

```sh-session
$ npm install --save-dev @percy/cli
```

pip install Percy appium package:

```ssh-session
$ pip install percy-appium
```

## Usage

This is an example test using the `percy_screenshot` function.

``` python
from appium import webdriver
from percy import percy_screenshot

driver = webdriver.Remote("https://" + userName + ":" + accessKey + "@hub-cloud.browserstack.com/wd/hub", desired_caps)

# take a screenshot
response = percy_screenshot(driver, 'here is some name')
```

Running the test above normally will result in the following log:

```sh-session
[percy] Percy is not running, disabling screenshots
```

When running with [`percy
app:exec`](https://github.com/percy/cli/tree/master/packages/cli-exec#app-exec), and your project's
`PERCY_TOKEN`, a new Percy build will be created and screenshots will be uploaded to your project.

```sh-session
$ export PERCY_TOKEN=[your-project-token]
$ percy app:exec -- [python test command]
[percy] Percy has started!
[percy] Created build #1: https://percy.io/[your-project]
[percy] Screenshot taken "Python example"
[percy] Stopping percy...
[percy] Finalized build #1: https://percy.io/[your-project]
[percy] Done!
```

## Configuration

`percy_screenshot(driver, name[, **kwargs])`

- `driver` (**required**) - A appium driver instance
- `name` (**required**) - The screenshot name; must be unique to each screenshot
- `device_name` (**optional**) - The device name used for capturing screenshot
- `orientation` (**optional**) - Orientation of device while capturing screeenshot; Allowed values [`portrait` | `landscape`]
- `status_bar_height` (**optional**) - Height of status bar; number
- `nav_bar_height` (**optional**) - Height of navigation bar; number
- `full_screen` (**optional**) - Indicate whether app is full screen; boolean

### Migrating Config

If you have a previous Percy configuration file, migrate it to the newest version with the
[`config:migrate`](https://github.com/percy/cli/tree/master/packages/cli-config#percy-configmigrate-filepath-output) command:

```sh-session
$ percy config:migrate
```
