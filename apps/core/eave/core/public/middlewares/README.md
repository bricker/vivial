## middleware check bypass

To bypass the signature and auth verification middlewares in development mode, the following conditions must be met:

1. Python "dev_mode" must be enabled. You can set `PYTHONDEVMODE=1` in your `.env` file to enable it.
1. The `GOOGLE_CLOUD_PROJECT` must not be set to `eave-production`.
1. A header `X-Google-EAVEDEV` exists on the request, and is set to the string you get from the following Python command:

```
$ python
>>> import os
>>> str(os.uname())
```

You'll get a string that looks something like this:

```
posix.uname_result(sysname='Linux', nodename='your computer name', release='OS release identifier', version='OS version identifier', machine='x86_64')
```

Copy that string into the `X-Google-EAVEDEV` header. It will be verified when requesting development bypass.

### Auth Bypass

When bypassing auth, the `Authorization` header should contain the ID of the account you want to act as.