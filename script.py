import re
from datetime import datetime

from dataEngineering.token_selection import simplify_content

# s = '[com.apple.calendar.store.log.caldav.coredav] [Refusing to parse response to PROPPATCH because of content-type: [text/html; charset=UTF-<*>].]'
# res = simplify_content(s)
# print(re.split('\W+', res))

print(datetime.now().microsecond)
