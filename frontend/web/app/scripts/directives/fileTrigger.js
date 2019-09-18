(function () {
  angular
    .module('irma')
    .directive('fileTrigger', fileTrigger);

  function fileTrigger() {
    return {
      link(scope, element) {
        element.click(() => {
          angular.element('#file-container').click();
        });
      },
    };
  }
}());
