'use strict';

/* http://docs.angularjs.org/guide/dev_guide.e2e-testing */

describe('Ivy', function() {

  it('should redirect index.html to index.html#/dashboard', function() {
    browser.get('/dist');
    browser.getLocationAbsUrl().then(function(url) {
      expect(url.split('#')[1]).toBe('/dashboard');
    });
    expect(element(by.binding('data')).getText()).toBe('coucou');
  });
  
});
