'use strict';

/* http://docs.angularjs.org/guide/dev_guide.e2e-testing */

describe('Ivy', function() {

  it('should redirect index.html to index.html#/dashboard', function() {
    browser.get('/appgit');
    browser.getLocationAbsUrl().then(function(url) {
      expect(url.split('#')[1]).toBe('/selection');
    });
  });
  
});
