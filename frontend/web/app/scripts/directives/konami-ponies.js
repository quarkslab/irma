(function () {
  angular
    .module('irma')
    .directive('konami', Konami);

  function Konami($document) {
    return {
      link() {
        const konamiKeys = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65];
        let konamiIndex = 0;

        function down(e) {
          if (e.keyCode === konamiKeys[konamiIndex]) {
            konamiIndex += 1;

            if (konamiIndex === konamiKeys.length) {
              angular.element($document).unbind('keydown', down);
              angular
                .element('body')
                .append('<script src="resources/ponies.js" id="browser-ponies-script"></script><script type="text/javascript">/* <![CDATA[ */ setTimeout(function(){ (function (cfg) {BrowserPonies.setBaseUrl(cfg.baseurl);BrowserPonies.loadConfig(BrowserPoniesBaseConfig);BrowserPonies.loadConfig(cfg);})({"baseurl":"http://panzi.github.io/Browser-Ponies/","fadeDuration":500,"volume":1,"fps":25,"speed":3,"audioEnabled":false,"showFps":false,"showLoadProgress":true,"dontSpeak":true,"spawn":{"applejack":1,"fluttershy":1,"pinkie pie":1,"rainbow dash":1,"rarity":1,"twilight sparkle":1},"autostart":true}); },1000); /* ]]> */</script>');
            }
          } else {
            konamiIndex = 0;
          }
        }

        angular.element($document).keydown(down);
      },
    };
  }
}());
