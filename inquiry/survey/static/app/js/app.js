'use strict';

// Declare app level module which depends on views, and components
var app = angular.module('inquiry', [
  'ngRoute', 'inquiryControllers', 'ngAnimate', 'ngMaterial', 'ngSanitize',
  'truncate'
]);

app.config(['$routeProvider', '$mdThemingProvider', 
            function($routeProvider, $mdThemingProvider) {
	$routeProvider
		.when('/login', {
			templateUrl: '/static/app/partials/login.html',
			controller: 'LoginController'
		})
		
		.when('/surveys/:status/', {
			templateUrl: '/static/app/partials/surveys.html',
			controller: 'SurveysController'
		})
		
		.when('/survey/overview/:status/:oid/', {
			templateUrl: '/static/app/partials/survey_overview.html',
			controller: 'SurveyOverviewController'
		})
		
		.when('/survey/response/overview/:status/:oid/', {
			templateUrl: '/static/app/partials/response_overview.html',
			controller: 'ResponseOverviewController'
		})
		
		.when('/survey/:oid/', {
			templateUrl: '/static/app/partials/response.html',
			controller: 'ResponseController'
		})
		
		.otherwise({redirectTo: '/login'});
	
	$mdThemingProvider.theme('app-dark','default').dark();
}]);

app.directive('multiline', ['$timeout', function($timeout) {
    return {
        restrict: 'A',
        compile: function(wrappedElement) {
            var element = wrappedElement[0],
                input = element.querySelector('input');

                element.innerHTML += '<textarea ng-model="value" class="ng-touched"></textarea>';

            $timeout(function() {
                element.querySelector('input').style.display = 'none';

                element.querySelector('textarea').addEventListener('blur', function() {
                    element.classList.remove('md-input-focused');
                });

                element.querySelector('textarea').addEventListener('focus', function() {
                    element.classList.add('md-input-focused');
                });
            }, 0)
        }
    }
}]);