'use strict';

/* jasmine specs for controllers go here */
describe('Ivy Controllers', function() {

  beforeEach(function(){
    this.addMatchers({
      toEqualData: function(expected) {
        return angular.equals(this.actual, expected);
      }
    });
  });

  beforeEach(module('irma'));

  describe('SelectionCtrl', function(){
    var scope, ctrl, $httpBackend;

    beforeEach(inject(function(_$httpBackend_, $rootScope, $controller) {
      $httpBackend = _$httpBackend_;
      scope = $rootScope.$new();
      ctrl = $controller('SelectionCtrl', {$scope: scope});
    }));

    it('should create the scope', function() {
      expect(scope.scan).toBeDefined();
    });
  });
});
