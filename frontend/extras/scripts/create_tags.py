import sys

from frontend.models.sqlobjects import Tag

from api.common.sessions import session_transaction
from irma.common.utils import decode_utf8

if len(sys.argv) != 2:
    print("usage: {0} <tag_list> (comma separated)".format(sys.argv[0]))
    sys.exit(1)

# get tag list as argument
tag_list = sys.argv[1]

# split comma separated list
tags = tag_list.split(",")

# force all tags to lowercase
tags = map(lambda x: decode_utf8(x.lower()), tags)

with session_transaction() as session:
    # get all existing tags
    existing_tags = Tag.query_find_all(session)
    existing_text = [t.text for t in existing_tags]
    # filter only the one needed to be created
    to_create_tags = filter(lambda x: x not in existing_text, tags)
    print u"[+] Tags already existing: {0}".format(",".join(existing_text))
    for tag in to_create_tags:
        t = Tag(tag)
        print u"[+] creating Tag: {0}".format(tag)
        session.add(t)
