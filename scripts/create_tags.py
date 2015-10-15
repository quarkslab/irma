import sys

from frontend.models.sqlobjects import Tag
from frontend.helpers.sessions import session_transaction


if len(sys.argv) != 2:
    print("usage: {0} <tag_list> (comma separated)".format(sys.argv[0]))
    sys.exit(1)

# get tag list as argument
tag_list = sys.argv[1]

# split comma separated list
tags = tag_list.split(",")

# force all tags to lowercase
tags = map(lambda x: x.lower(), tags)

with session_transaction() as session:
    # get all existing tags
    existing_tags = Tag.query_find_all(session)
    existing_text = [t.text for t in existing_tags]
    # filter only the one needed to be created
    to_create_tags = filter(lambda x: x not in existing_text, tags)
    print "[+] Tags already existing: {0}".format(",".join(existing_text))
    for tag in to_create_tags:
        t = Tag(tag)
        print "[+] creating Tag: {0}".format(tag)
        session.add(t)
