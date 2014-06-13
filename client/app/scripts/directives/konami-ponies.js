'use strict';

(function () {

  var dependencies = ['$document', '$window'];
  var Konami = function ($document, $window) {

    return {
      link: function (scope, element, attrs) {
        var konami_keys = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65];
        var konami_index = 0;

        function down(e){
          if (e.keyCode === konami_keys[konami_index++]) {
            if (konami_index === konami_keys.length) {
              angular.element($document).unbind('keydown', down);
              /* jshint ignore:start */
              angular.element('body').append('<script type="text/javascript" src="http://panzi.github.io/Browser-Ponies/basecfg.js" id="browser-ponies-config"></script><script type="text/javascript" src="http://panzi.github.io/Browser-Ponies/browserponies.js" id="browser-ponies-script"></script><script type="text/javascript">/* <![CDATA[ */ setTimeout(function(){ (function (cfg) {BrowserPonies.setBaseUrl(cfg.baseurl);BrowserPonies.loadConfig(BrowserPoniesBaseConfig);BrowserPonies.loadConfig(cfg);})({"baseurl":"http://panzi.github.io/Browser-Ponies/","fadeDuration":500,"volume":1,"fps":25,"speed":3,"audioEnabled":false,"showFps":false,"showLoadProgress":false,"speakProbability":0.01,"spawn":{"applejack":1,"fluttershy":1,"pinkie pie":1,"rainbow dash":1,"rarity":1,"twilight sparkle":1},"autostart":true}); },1000); /* ]]> */</script>');
              /* jshint ignore:end */
            }
          } else {
            konami_index = 0;
          }
        }

        angular.element($document).keydown(down);
      }
    };
  };

  Konami.$inject = dependencies;
  angular.module('irma').directive('konami', Konami);
}());
