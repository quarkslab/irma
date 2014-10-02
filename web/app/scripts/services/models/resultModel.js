'use strict';

angular
  .module('irma')
  .factory('Result', Result);

Result.$inject = ['$http'];

function Result($http) {
  function ResultModel(resultData) {
    if (resultData) {
      this.setData(resultData);
    }
  }

  ResultModel.prototype = {
    setData: setData
  };

  return ResultModel;

  function setData(resultData) {
    angular.extend(this, resultData);
  }
}
