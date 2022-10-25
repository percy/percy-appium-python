import json


_android_capability_fp = open('./tests/mocks/android_capabilities.json', 'r')
android_capabilities = json.load(_android_capability_fp)
_android_capability_fp.close()

_ios_capability_fp = open('./tests/mocks/ios_capabilities.json', 'r')
ios_capabilities = json.load(_ios_capability_fp)
_ios_capability_fp.close()
