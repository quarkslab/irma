
def file_exists(sha256):
    """ return results for file with given sha256 value

    :rtype: boolean
    :return:
        if exists returns True else False
    :raise: IrmaTaskError
    """
    try:
        File.load_from_sha256(sha256=sha256)
        return True
    except IrmaDatabaseResultNotFound:
        return False
    except IrmaDatabaseError as e:
        raise IrmaTaskError(str(e))


def file_result(sha256, filter_type=None):
    """ return results for file with given sha256 value

    :rtype: dict of sha256 value: dict of ['filename':str,
        'results':dict of [str probename: dict of [probe_type: str,
        status: int , duration: int, result: int, results of probe]]]]
    :return:
        if exists returns all available scan results
        for file with given sha256 value
    """
    # TODO handle file dont exists here
    f = File.load_from_sha256(sha256=sha256)
    ref_res = {}
    probe_results = {}
    for rr in f.ref_results:
        probe_results[rr.probe_name] = ProbeRealResult(
            id=rr.nosql_id
        ).get_results()
    ref_res[f.sha256] = {
        'filename': f.get_file_names(),
        'results': format_results(probe_results, filter_type)
    }

    return ref_res


def file_infected(sha256):
    """ return antivirus score for file with given sha256 value

    :rtype: dict of ['infected':boolean,
        'nb_scan':int, 'nb_detected': int ]
    :return:
        returns detection score for
        file with given sha256 value
    """
    f = File.load_from_sha256(sha256=sha256)
    # FIXME old code here
    ref_res = ScanRefResults(id=f.id)
    nb_scan = nb_detected = 0

    av_results = file_result(sha256, filter_type=["antivirus"])
    probe_res = av_results[sha256]['results']
    for res in probe_res.values():
        nb_scan += 1
        if res['result'] == IrmaScanResults.isMalicious:
            nb_detected += 1

    return {'infected': (nb_detected > 0),
            'nb_detected': nb_detected,
            'nb_scan': nb_scan}
