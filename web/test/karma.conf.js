module.exports = function(config){
  config.set({

    basePath : '../',

    files : [
      'app/components/lodash/dist/lodash.js',
      'app/components/jquery/jquery.js',
      'app/components/moment/min/moment-with-langs.js',
      'app/components/angular/angular.js',
      'app/components/angular-resource/angular-resource.js',
      'app/components/angular-sanitize/angular-sanitize.js',
      'app/components/angular-route/angular-route.js',
      'app/components/angular-animate/angular-animate.js',
      'app/components/angular-bootstrap/ui-bootstrap.js',
      'app/components/angular-bootstrap/ui-bootstrap-tpls.js',
      'app/components/angular-ui-utils/ui-utils.js',
      'app/components/d3/d3.js',
      'app/components/nvd3/nv.d3.js',
      'app/components/angularjs-nvd3-directives/dist/angularjs-nvd3-directives.js',
      'app/components/angular-file-upload/angular-file-upload.js',
      'app/components/angular-mocks/angular-mocks.js',
      'app/scripts/*.js',
      'app/scripts/**/*.js',
      'test/unit/**/*.js'
    ],

    frameworks: ['jasmine'],

    browsers : ['Chrome'],

    singleRun: true,

    plugins : [
      'karma-chrome-launcher',
      'karma-firefox-launcher',
      'karma-jasmine'
    ]

  });
};