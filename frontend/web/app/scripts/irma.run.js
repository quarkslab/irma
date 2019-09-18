(function () {
  angular
    .module('irma')
    .run(run);

  function run($anchorScroll, $location, $rootScope, alerts, api, state) {
    $rootScope.$on('$routeChangeStart', (event) => {
      alerts.removeAll();

      if (state.settings.maintenance) { event.preventDefault(); }
    });

    $rootScope.$on('$routeChangeSuccess', (event, newOne) => {
      angular.extend(state, { location: newOne.location });
      state.updateTitle();

      if ($location.hash()) { $anchorScroll(); }
    });

    $rootScope.$on('maintenance', () => {
      state.goTo('maintenance');
    });
  }
}());
