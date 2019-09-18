(function () {
  angular
    .module('irma')
    .constant('constants', {
      fakeDelay: 0,
      baseApi: '/api/v2',
      speed: 1500,
      refresh: 1000,
      forceScanDefault: true,
      scanStatusCodes: {
        STOPPED: 0,
        RUNNING: 1,
        FINISHED: 2,
        ERROR: 3,
      },
    })
    .constant('angularMomentConfig', {
      preprocess(value) {
        return moment.unix(value);
      },
    });
}());
