(function () {
  angular
    .module('irma')
    .controller('SearchCtrl', Search);

  function Search($scope, NgTableParams, dataservice, alerts, $routeParams, $location,
    tagPrepService) {
    // Exports
    const vm = this;
    angular.extend(vm, {
      searchedStr: $routeParams.value || '',
      searchedType: $routeParams.type || 'name',
      searchedTags: getTagsByIds($routeParams.tags),
      tableParams: new NgTableParams({
        page: $routeParams.page || 1, // show first page
        count: $routeParams.offset || 25, // count per page
      }, {
        total: 0,
        getData,
      }),

      // Functions
      loadAvailableTags,
      doSearch,
    });

    // IIFE when entering the controller
    (function run() {
      $scope.$on('$routeUpdate', () => {
        /**
         * This will update current scope values regarding HTTP GET query params.
         *
         * `$routeUpdate` event is trigger when `reloadOnSearch` is set to
         * `false` and when staying on the same Controller.
         * In our situation, it happens when using history back/forward or
         * `$location.search` as in the `doSearch` function.
         */
        vm.searchedStr = $routeParams.value;
        vm.searchedType = $routeParams.type;
        vm.searchedTags = getTagsByIds($routeParams.tags);
        vm.tableParams.page($routeParams.page);
        vm.tableParams.count($routeParams.offset);
        vm.tableParams.reload();
      });
    }());

    // Functions
    function getData(params) {
      alerts.removeAll();

      return dataservice
        .searchFiles(vm.searchedTags, vm.searchedType, vm.searchedStr,
          (params.page() - 1) * params.count(), params.count())
        .then((data) => {
          params.total(data.total);
          return data.items;
        });
    }


    function getTagsByIds(ids) {
      if (!ids) {
        return [];
      }

      if (Array.isArray(ids)) {
        return _.filter(tagPrepService.items, e => ids.indexOf(e.id.toString()) > -1);
      }

      /**
       * In case there is only one tag selected, and there is the case where
       * `tag=123`, which, using the method before will use ids as an
       * `Array('1', '2', '3')`.
       */
      return _.filter(tagPrepService.items, e => e.id === ids);
    }


    function loadAvailableTags(query) {
      const results = [];

      for (let i = 0; i < tagPrepService.items.length; i += 1) {
        if (tagPrepService.items[i].text.toLowerCase().indexOf(query.toLowerCase()) > -1) {
          results.push(tagPrepService.items[i]);
        }
      }

      return results;
    }


    function doSearch() {
      /**
       * Persist data to the url to allow history navigation.
       *
       * Using $location.search normally reload the page, but in as we've set
       * `reloadOnSearch: false` in the $routeProvider function, there will be
       * no page change, and we will gain bandwidth by not having to resolve
       * `tagPrepService` data (at each page change).
       *
       * At the end of this function, a `$routeUpdate` event will be triggered.
       */
      $location.search('value', vm.searchedStr);
      $location.search('type', vm.searchedType);
      $location.search('page', 1);
      $location.search('tags', _.map(vm.searchedTags, 'id'));
      $location.search('offset', vm.tableParams.count());
    }
  }
}());
