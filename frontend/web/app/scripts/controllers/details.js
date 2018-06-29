(function () {
  'use strict';

  angular
    .module('irma')
    .controller('DetailsCtrl', Details);

  Details.$inject = ['$routeParams', 'state', 'resultsManager', 'api'];

  function Details($routeParams, state, resultManager, api) {
    var vm = this;
    var availableTags = [];

    angular.extend(vm, {
      // variables
      results: undefined, // set in the activate function
      timeline: undefined,

      // methods
      goTo: state.goTo,

      searchTags: function(query) {
        var results = [];

        for(var i=0; i < availableTags.length; i++) {
          if(availableTags[i].text.toLowerCase().indexOf(query.toLowerCase()) > -1) {
            results.push(availableTags[i]);
          }
        }

        return results;
      },

      tagAdded: function(tag) {
        api.tag.addTag(vm.results.file_infos.sha256, tag.id);
      },

      tagRemoved: function(tag) {
        api.tag.removeTag(vm.results.file_infos.sha256, tag.id);
      },
    });

    activate();

    function activate() {
      if(!state.scan) {
        state.newScan($routeParams.scanId);
      }

      resultManager.getResult($routeParams.resultId).then(function(results) {
        vm.results = results;
        calculateTimelineVariables(results);
      });

      resultManager.getAvailableTags().then(function(results) {
        availableTags = results.items;
      });
    }

    function calculateTimelineVariables(results) {
      var startDate = moment(results.file_infos.timestamp_first_scan * 1000) // * 1000 is used to convert from a unix timestmap
        .startOf('year');
      var startDateUnix = startDate.unix();
      var endDate = moment(results.file_infos.timestamp_last_scan * 1000).endOf('year');
      var nbOfYears = endDate.year() - startDate.year() + 1;
      var diffStartEndDatesUnix = endDate.diff(startDate, 'seconds'); // seconds is similar to the Unix timestamp
      var indexResultId = _.findIndex(results.other_results, function(o) { return o.external_id === results.result_id; });

      var labels = [];
      _.forOwn(_.range(startDate.year(), endDate.year() + 1), function(year, key) {
        labels.push({
          'year': year,
          // Calculate the left shift used in the timeline in percentage
          'leftShiftPercentage': key / nbOfYears * 100,
        });
      });


      vm.timeline = {
        // vars
        labels: labels,
        nextResultId: ((indexResultId + 1) < results.other_results.length) ? results.other_results[indexResultId + 1].external_id : false,
        previousResultId: (indexResultId > 0) ? results.other_results[indexResultId - 1].external_id : false,

        // functions
        getMarkerLeftShiftPercentage: function(scanDateTs) {
          return (scanDateTs - startDateUnix) / diffStartEndDatesUnix * 100;
        },
      };
    }
  }
}) ();
