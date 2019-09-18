(function () {
  angular
    .module('irma')
    .controller('DetailsCtrl', Details);

  function Details($routeParams, state, resultsManager, api) {
    const vm = this;
    let availableTags = [];

    // Exports
    angular.extend(vm, {
      // variables
      results: undefined, // set in the activate function
      timeline: undefined,

      // methods
      goTo: state.goTo,
      searchTags,
      tagAdded,
      tagRemoved,
    });

    // IIFE when entering the controller
    (function run() {
      if (!state.scan) {
        state.newScan($routeParams.scanId);
      }

      resultsManager.getResult($routeParams.resultId).then((results) => {
        vm.results = results;
        calculateTimelineVariables(results);
      });

      resultsManager.getAvailableTags().then((results) => {
        availableTags = results.items;
      });
    }());

    // Functions
    function calculateTimelineVariables(results) {
      // * 1000 is used to convert from a unix timestmap
      const startDate = moment(results.file_infos.timestamp_first_scan * 1000)
        .startOf('year');
      const startDateUnix = startDate.unix();
      const endDate = moment(results.file_infos.timestamp_last_scan * 1000).endOf('year');
      const nbOfYears = endDate.year() - startDate.year() + 1;
      // seconds is similar to the Unix timestamp
      const diffStartEndDatesUnix = endDate.diff(startDate, 'seconds');
      const indexResultId = _.findIndex(results.other_results,
        o => o.result_id === results.result_id);
      const labels = [];

      _.forOwn(_.range(startDate.year(), endDate.year() + 1), (year, key) => {
        labels.push({
          year,
          // Calculate the left shift used in the timeline in percentage
          leftShiftPercentage: key / nbOfYears * 100,
        });
      });

      vm.timeline = {
        // vars
        labels,
        nextResultId: ((indexResultId + 1) < results.other_results.length)
          ? results.other_results[indexResultId + 1].result_id : false,
        previousResultId: (indexResultId > 0)
          ? results.other_results[indexResultId - 1].result_id : false,

        // functions
        getMarkerLeftShiftPercentage(scanDateTs) {
          return (scanDateTs - startDateUnix) / diffStartEndDatesUnix * 100;
        },
      };
    }

    function searchTags(query) {
      const results = [];

      for (let i = 0; i < availableTags.length; i += 1) {
        if (availableTags[i].text.toLowerCase().indexOf(query.toLowerCase()) > -1) {
          results.push(availableTags[i]);
        }
      }

      return results;
    }

    function tagAdded(tag) {
      api.tag.addTag(vm.results.file_infos.sha256, tag.id);
    }

    function tagRemoved(tag) {
      api.tag.removeTag(vm.results.file_infos.sha256, tag.id);
    }
  }
}());
