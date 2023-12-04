import os

import eave.stdlib.ctracing
import eave.stdlib.pytracing

os.environ["EAVE_ENV"] = "development"
os.environ["EAVE_APPS_BASE_PUBLIC"] = "https://apps.eave.tests"
os.environ["EAVE_API_BASE_PUBLIC"] = "https://api.eave.tests"
os.environ["EAVE_WWW_BASE_PUBLIC"] = "https://www.eave.tests"
os.environ["EAVE_ANALYTICS_DISABLED"] = "1"
os.environ["EAVE_MONITORING_DISABLED"] = "1"

# eave.stdlib.ctracing.start_profiling()
# eave.stdlib.pytracing.start_profiling()

# eave.stdlib.ctracing.start_tracing()
# eave.stdlib.pytracing.start_tracing()
