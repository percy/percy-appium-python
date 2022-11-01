# pylint: disable=[consider-using-with]

import json


_android_capability_fp = open('./tests/mocks/android_capabilities.json', 'r', encoding='utf-8')
android_capabilities = json.load(_android_capability_fp)
_android_capability_fp.close()

_ios_capability_fp = open('./tests/mocks/ios_capabilities.json', 'r', encoding='utf-8')
ios_capabilities = json.load(_ios_capability_fp)
_ios_capability_fp.close()
