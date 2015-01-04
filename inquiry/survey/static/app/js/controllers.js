var inquiryControllers = angular.module('inquiryControllers', []);

inquiryControllers
.controller('MainController', ['$scope', '$http', '$browser', '$location', 
                               '$mdSidenav', '$sanitize', '$mdToast', 'User',
  function ($scope, $http, $browser, $location, $mdSidenav, $sanitize,
		    $mdToast, User) {
    $scope.menu = {};
    $scope.user = null;
    $scope.toggle_nav = function() { $mdSidenav('main-nav').toggle(); }
    $scope.close_nav = function() { $mdSidenav('main-nav').close(); }

    $scope.survey = null;
    $scope.response = null;
    $scope.sections = null;
    $scope.active_record = null; // overview
    
    $scope.setSection = function(section) {
    	$scope.menu['currentSection'] = section;
    }
    
    $scope._selected = null;
    $scope.select = function(item) {
    	$scope._selected = item;
    }
    $scope.is_selected = function(label) {
    	if (!$scope._selected) {
    		return false;
    	}
    	return $scope._selected.indexOf(label) == 0;
    }
    
    $scope.is_login = function() {
        return $location.path().lastIndexOf('/login', 0) === 0;
    }
    
    $scope.logout = function() {
    	User.logout($scope.user).then(
    			function() {
    				$scope.go_login();
    			},
    			function() {
    				$scope.go_login();
    			}
    	);
    	
    }
    
    $scope.go_login = function() {
	    if (!$scope.is_login()) {
	        if (!$location.search().next) {
	        $location.search('next',$location.url());
	      }
	      $location.path('/login');
	    }
    }
    
    if (!$scope.is_login()) {
        $scope.go_login();
    }

    $scope.go_home = function() {
    	var next = $location.search()['next'];
        if (next !== undefined) {
          $location.search('next',null);
          if (next != null) {
            $location.path(next);
            return;
          }
        } else {
        	$location.path('/surveys/saved/');
        }
    }
    
    $scope.setup_http = function(loginResponse) {
        $http.defaults.headers.common['Content-type'] = 'application/json;charset=UTF-8';
        // don't use $cookies here, it doesn't update itself when they change
        if (loginResponse === undefined) {
          if (($browser.cookies().sessionid === undefined) || (!$browser.cookies().sessionid)) {
            return false;
          } else {
            // If it's undefined then the HTTP_ONLY flag is set
            $http.defaults.headers.common['Authorization'] = 'session '+$browser.cookies().sessionid;
          }
        } else {
          $http.defaults.headers.common['Authorization'] = 'session '+loginResponse.session.id;
        }
        return true;
    } 
    
    $scope.toast = function(msg) {
    	if (!msg) {
    		msg = 'Unknown error';
    	}
    	$mdToast.show({
			template:
				'<md-toast>'+
				'  <span flex>'+$sanitize(msg)+'</span>'+
				'</md-toast>',
			position: 'top right'
		});
    }
    
    $scope.take_survey = function(response) {
    	$location.path('/survey/'+response.id+'/');
    }
}])

.controller('LoginController', ['$scope', '$http', '$location', 'User', 
                                '$mdToast',
  function ($scope, $http, $location, User, $mdToast) {
	$scope.showLogin = false;
	$scope.$parent.close_nav();
	
	if ($location.search().error) {
		$scope.$parent.toast('Unable to login. Wrong Google user?');
	}
	
	User.my().then(
		function(success) {
			$scope.$parent.user = success;
			$scope.$parent.setup_http();
			$scope.$parent.go_home();
		},
		function(error) {
			$scope.showLogin = true;
		}
	);
	
    
    $scope.go_social_login = function() {
    	document.location.href= '/auth/social/login/login/google-oauth2-inquiry/';
    }
}])

.controller('SurveysController', 
  ['$scope', '$routeParams', '$location', 'Survey', 'Response',
  function ($scope, $routeParams, $location, Survey, Response) {
	$scope.status = $routeParams.status;
	$scope.$parent.select('surveys.'+$scope.status);
	
	$scope.go_response = function(status, record) {
		$location.path('/survey/response/overview/'+status+'/'+record.id+'/');
	}
	$scope.go_survey = function(status, record) {
		$location.path('/survey/overview/'+status+'/'+record.id+'/');
	}
	
	$scope.records = [];
	$scope.name = null;
	if ($scope.status == 'saved') {
		Response.list({status__closed_state: 'False'})
			.then(
				Response.list_include([{field:'survey', 'service': Survey}])
			).then(
				function(data) {
					$scope.records = data;
					$scope.name = 'Saved Training';
					$scope.surveyMode = false;
				},
				function(err) {
					$scope.$parent.toast(err.detail);
				}
		);
	} else if ($scope.status == 'available') {
		Survey.list({no_responses_for: $scope.$parent.user.id}).then(
				function(data) {
					$scope.records = data;
					$scope.name = 'Available Training';
					$scope.surveyMode = true;
				},
				function(err) {
					$scope.$parent.toast(err.detail);
				}
		);
	} else if ($scope.status == 'completed') {
		Response.list({status__closed_state: 'True'})
			.then(
				Response.list_include([{field:'survey', 'service': Survey}])
			).then(
				function(data) {
					$scope.records = data;
					$scope.name = 'Completed Training';
					$scope.surveyMode = false;
				},
				function(err) {
					$scope.$parent.toast(err.detail);
				}
		);
	} else {
		$location.path('/surveys/saved/');
	}
}])

.controller('SurveyOverviewController', 
		['$scope', '$routeParams', '$filter', 'Survey', 
		 'User', 'Type', 'Section', 'Question',
	function ($scope, $routeParams, $filter, Survey, User, 
			  Type, Section, Question) {
		$scope.oid = $routeParams.oid;
		$scope.status = $routeParams.status;
		$scope.record = null;
		$scope.section_count = null;
		$scope.question_count = null;
		// since our fields need a bind field currently
		$scope.modified_date = null;

		Survey.get($scope.oid)
			.then(Survey.include([{field: 'survey_type',
				                   service: Type},
				                  {field: 'owner',
				                   service: User},
				                 ])
				 )
			.then(
				function(record) {
					$scope.record = $scope.$parent.active_record = record;
					$scope.modified_date = $filter('date')
											($scope.record.modified)
					$scope.$parent.select('surveys.'+$scope.status+
										  '.'+$scope.record.id);
				},
				function(error) {
					$scope.$parent.toast(error.detail);
				}
			);
	
		Section.count({parent:$scope.oid}).then(function(count){
			$scope.section_count = count;
		});
		Question.count({parent:$scope.oid}).then(function(count){
			$scope.question_count = count;
		});
		
		$scope.launch_survey = function() {
			Survey.launch($scope.record, $scope.$parent.user).then(
				function(response) {
					$scope.$parent.take_survey(response);
				},
				function(error) {
					$scope.$parent.toast(error.detail);
				}
			);
			
		}
}])

.controller('ResponseOverviewController', 
		['$scope', '$http', '$routeParams', '$filter', '$q',
		 '$mdDialog', 'Survey', 'User', 'Type', 'Response', 'ResponseSection', 
		 'QuestionResponse', 'Status',
		function ($scope, $http, $routeParams, $filter, $q,
				  $mdDialog, Survey, User, Type, Response, ResponseSection,
				  QuestionResponse, Status) {
			$scope.status = $routeParams.status;
			$scope.oid = $routeParams.oid;
			$scope.status = $routeParams.status;
			$scope.record = null;
			$scope.section_count = null;
			$scope.question_count = null;
			// since our fields need a bind field currently
			$scope._date = null;
			$scope.due_date = null;
			$scope.meta = null;
			Response.meta($scope.oid).then(
				function(data) {
					$scope.meta = data;
				},
				function(err) {
					$scope.$parent.toast(err.detail || 
										 'Unable to get metadata');
				}
			);
			Response.get($scope.oid)
				.then(Response.include([{field: 'survey',
					                     service: Survey},
					                    {field: 'user',
					                     service: User},
					                    {field: 'status',
					                     service: Status}
					                   ])
					 )
				.then(function(record) {
					Type.get(record.survey.survey_type)
						.then(function(type_record) {
							record.survey.survey_type = type_record;
					});
					var deferred = $q.defer();
					deferred.resolve(record);
					return deferred.promise;
				})
				.then(
					function(record) {
						$scope.record = $scope.$parent.active_record = record;
						if ($scope.status == 'completed') {
							$scope._date = $filter('date')
							($scope.record.completed_date);
						} else {
							$scope._date = $filter('date')
												($scope.record.modified);
							$scope.due_date = $filter('date')
							($scope.record.due_date);
												
												
						}
						$scope.$parent.select('surveys.'+$scope.status+
											  '.'+$scope.record.id);
					},
					function(error) {
						$scope.$parent.toast(error.detail);
					}
				);
		
			ResponseSection.count({response:$scope.oid}).then(function(count){
				$scope.section_count = count;
				ResponseSection.count(
						{response: $scope.oid, 							
							questionresponse__null_answer: 'False'}).then(
					function(cnt){
						$scope.section_count += '  ('+cnt.toString()+')';
					});
			});
			QuestionResponse.count({response:$scope.oid}).then(function(count){
				$scope.question_count = count;
				QuestionResponse.count({response: $scope.oid, 
										null_answer: 'False'}).then(
						function(cnt){
							$scope.question_count += '  ('+cnt.toString()+')';
						});
			});
			
			$scope.launch_response = function() {
				$scope.$parent.take_survey($scope.record);
			}
			
			$scope.delete_response = function() {
				var confirm = $mdDialog.confirm()
			      .content('Delete '+$scope.record.survey.name+' response?')
			      .ariaLabel('Confirm delete')
			      .ok('Confirm')
			      .cancel('Cancel');
				$mdDialog.show(confirm).then(
					function() {
						Response.delete($scope.record).then(
							function() {
								$scope.$parent.go_home();
							},
							function(err) {
								$scope.$parent.toast(err.detail 
													|| 'Unable to delete');
							}
						);
					}, 
					function() {
						// cancel
					}
				);
			}
}])

.controller('ResponseController', 
		['$scope', '$routeParams', 'Survey', 'Response', 'ResponseSection', 
		 'QuestionResponse', 'Section', 'Question',
		function ($scope, $routeParams, Survey, Response, 
				  ResponseSection, QuestionResponse, Section, Question) {
			$scope.record = null;
			$scope.oid = $routeParams.oid;
			$scope.$parent.select('progress.'+$scope.oid);
			$scope.sections = null;
			$scope.section_lookup = {};
			
			Response.get($scope.oid)
				.then(Response.include([{field: 'survey',
				                         service: Survey},
				                   ]))
				.then(
					function(record) {
						$scope.record = record;
						$scope.$parent.active_record = record;
					},
					function(error) {
		   				$scope.$parent.toast(error.detail);
					}
				);
			
			ResponseSection.list({response: $scope.oid})
			.then(ResponseSection.list_include([{field: 'survey_section',
											service: Section},
				                   ]))
			.then(
				function(records) {
					for (var i in records) {
						records[i]._questions = [];
						var id = records[i].id.toString();
						$scope.section_lookup[id] = records[i];
					}
					$scope.sections = records;
					$scope.sections = $scope.sections.sort(function(a,b){
							return (a.order || 1) - (b.order || 1);
						});
					$scope.$parent.sections = $scope.sections;
				},
				function(error) {
	   				$scope.$parent.toast(error.detail);
				}
			).then(
				function() {
					QuestionResponse.list({response: $scope.oid})
					.then(QuestionResponse.list_include([{field: 'question',
														service: Question},
				                   ]))
					.then(
						function(records) {
							for (var i in records) {
								var id = records[i].section.toString();
								if (!$scope.section_lookup[id]._questions) {
									$scope.section_lookup[id]._questions = [];
								}
								$scope.section_lookup[id]
									._questions.push(records[i]);
							}
							for (var id in $scope.section_lookup) {
								$scope.section_lookup[id]._questions.sort(
									function(a,b){
										return (a.order || 1) - (b.order || 1);
									}
								);
								var partial = false;
								var missing = false;
								for (var i in $scope.section_lookup[id]
												._questions) {
									var q = $scope.section_lookup[id]
												._questions[i];
									if (q.answer) {
										partial = true;
									} else 
										missing = true;
									}
								}
								if (partial && !missing) {
									$scope.section_lookup[id]
													._completed = true;
									$scope.section_lookup[id]
													._partial = true;
								} else if (partial && missing) {
									$scope.section_lookup[id]
													._completed = false;
									$scope.section_lookup[id]
													._partial = true;
								} else if (partial && missing) {
									$scope.section_lookup[id]
												._completed = false;
									$scope.section_lookup[id]
												._partial = false;
								}
				}
								
							}
						},
						function(error) {
			   				$scope.$parent.toast(error.detail);
						}
					);
				}
			);
}]);