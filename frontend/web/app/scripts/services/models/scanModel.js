(function () {
  angular
    .module('irma')
    .factory('ScanModel', Scan);

  function Scan($rootScope, $timeout, api, alerts, constants) {
    function ScanModel(id) {
      this.id = id;
      this.task = undefined;
      this.base = undefined;
      this.status = constants.scanStatusCodes.STOPPED;
      this.results = undefined;
      this.scanProgress = {
        progress: 0,
        total: 0,
        successful: 0,
        finished: 0,
      };
    }

    angular.extend(ScanModel.prototype, {
      getPopover,
      launch,
      stopUpdate,
      cancelScan,
      updateScan,
      setProgress,
      getResults,
      getResult,
    });

    return ScanModel;

    // ******************************************************* //

    function getPopover(probe, results) {
      if (results.status === 0 || results.status === '0') {
        return {
          title: probe,
          content: 'File clean',
        };
      } if (results.status === 1 || results.status === '1') {
        return {
          title: probe,
          content: 'File compromised',
        };
      } if (results.status === 'loading') {
        return {
          title: probe,
          content: 'Waiting for response',
        };
      }
      return {
        title: probe,
        content: 'An error occured',
      };
    }

    // ******************************************************* //
    // Function associate to the Scan
    function launch(params) {
      this.status = constants.scanStatusCodes.STARTED;
      return api.scan.launch(params).then((response) => {
        this.id = response.id;
        return response;
      });
    }

    function cancelScan() {
      this.stopUpdate();
      if (this.id) {
        api.scan.cancel(this);
      }
    }

    function stopUpdate() {
      $timeout.cancel(this.task);
    }

    function updateScan() {
      api.scan.getInfos(this).then((data) => {
        this.setProgress(data.probes_total, data.probes_finished);
        this.arborescence = buildParents(data.results, this.results);
        this.results = data.results;

        if (data.status === 1020) {
          this.status = constants.scanStatusCodes.ERROR;
          alerts.add('<strong>Error:</strong> An FTP error occured.', 'danger');
        } else if (data.status === 110) {
          this.status = constants.scanStatusCodes.STOPPED;
        } else if (data.status !== 50) {
          this.status = constants.scanStatusCodes.RUNNING;
          this.task = $timeout(this.updateScan.bind(this), constants.refresh);
        } else {
          this.status = constants.scanStatusCodes.FINISHED;
        }
      }, () => {
        this.task = $timeout(this.updateScan.bind(this), constants.refresh);
      });
    }

    function setProgress(total, finished) {
      this.scanProgress = {
        progress: Math.round(100 * finished / total),
        total,
        successful: finished,
        finished,
      };
    }

    // ******************************************************* //

    function getResults() {
      return api.scan.getResults(this).then((data) => {
        this.results = data;
        this.arborescence = buildParents(data);
      }, (data) => {
        $rootScope.$broadcast('errorResults', data);
      });
    }

    function getResult(resultid) {
      return api.scan.getResult(this, resultid);
    }

    function buildParents(list, existing) {
      let result = [];

      result = _.sortBy(_.filter(list, item => !item.parent_file_sha256), 'name');

      _.forEach(result, (item) => { populateArbo(item, list, existing); });

      return result;
    }

    function populateArbo(root, items, existing) {
      let result = [];

      result = _.sortBy(_.filter(items, item => item.parent_file_sha256 === root.file_sha256), 'name');

      if (!_.isEmpty(result)) {
        _.forEach(result, (item) => { populateArbo(item, items, existing); });
        angular.extend(root, { children: result });

        const oldOne = _.find(existing, { file_sha256: root.file_sha256 });

        angular.extend(root, {
          displayChildren: _.isUndefined(oldOne) || !_.has(oldOne, 'displayChildren') || oldOne.displayChildren,
        });
      }
    }
  }
}());
