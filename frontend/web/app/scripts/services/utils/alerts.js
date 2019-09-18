(function () {
  angular
    .module('irma')
    .factory('alerts', Alerts);

  function Alerts($timeout) {
    const alerts = [];

    // Exports
    return {
      add,
      list,
      remove,
      removeAll,
    };


    // Functions
    function add(message, type) {
      // Type can be one from [success, danger, warning, info] as in Bootstrap
      // predefined colors.
      const alert = {
        message,
        type,
      };

      alerts.push(alert);
      $timeout(() => {
        remove(alert);
      }, 4000);
    }

    function remove(alert) {
      const index = alerts.indexOf(alert);
      if (index !== -1) {
        alerts.splice(index, 1);
      }
    }

    function removeAll() {
      /**
       * We should not mutate the Array when deleting the elements otherwise
       * the reference of the object will be loose in the view part.
       * Lodash `remove` method don't mutate the array.
       */
      _.remove(alerts);
    }

    function list() {
      return alerts;
    }
  }
}());
