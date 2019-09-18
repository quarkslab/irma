(function () {
  angular
    .module('irma')
    .factory('Result', Result);

  function Result() {
    function ResultModel(resultData) {
      if (resultData) {
        this.setData(resultData);
      }
    }

    angular.extend(ResultModel.prototype, { setData });

    return ResultModel;

    function setData(resultData) {
      angular.extend(this, resultData);
    }
  }
}());
