(function () {
  angular
    .module('irma')
    .controller('MaintenanceCtrl', Maintenance);

  function Maintenance(state) {
    // It should be a getter/setter system instead of accessing directly to state variables.
    // eslint-disable-next-line no-param-reassign
    state.settings.maintenance = true;
  }
}());
