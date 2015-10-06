test_routes = {
    "/files/<sha256>/tags/<tagid>/add": ["GET"],
    "/files/<sha256>/tags/<tagid>/remove": ["GET"],
    "/probes": ["GET"],
    "/search/files": ["GET"],
    "/scans": ["GET", "POST"],
    "/scans/<scanid>": ["GET"],
    "/scans/<scanid>/files": ["POST"],
    "/scans/<scanid>/launch": ["POST"],
    "/scans/<scanid>/cancel": ["POST"],
    "/scans/<scanid>/results": ["GET"],
    "/scans/<scanid>/results/<resultid:int>": ["GET"],
    "/tags": ["GET"]
}
