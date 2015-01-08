var inquiryControllers = angular.module('inquiryControllers', []);

inquiryControllers
.controller('MainController', ['$scope', '$http', '$browser', '$location', 
                               '$mdSidenav', '$sanitize', '$mdToast', 
                               'User',
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
    
    // Used to hold selected items in menu after broadcast
    $scope.selected_question = null;
    $scope.selected_section = null;
    
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
    
    $scope.do_select_question = function(question) {
    	// used to notify children
    	$scope.selected_question = question;
    	$scope.$broadcast('menu.question_selected');
    	
    }
    $scope.do_select_section = function(section) {
    	// used to notify children
    	$scope.selected_section = section;
    	$scope.$broadcast('menu.section_selected');
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
		['$scope', '$routeParams', '$q', '$upload', '$mdDialog', 'Survey',
		 'Response', 'ResponseSection', 'QuestionResponse', 'Section',
		 'Question', 'QuestionChoice', 'QuestionResponseResource',
		function ($scope, $routeParams, $q, $upload, $mdDialog, Survey, 
				  Response, ResponseSection, QuestionResponse, Section,
				  Question, QuestionChoice, QuestionResponseResource) {
			$scope.record = null;
			$scope.oid = $routeParams.oid;
			$scope.$parent.select('progress.'+$scope.oid);
			$scope.sections = null;
			$scope.questions = null;
			$scope.section_lookup = {};
			$scope.response_lookup = {};
			$scope.active_section = null;
			$scope.active_question = null;
			// for nav
			$scope.next_question_obj = null;
			$scope.previous_question_obj = null;
			
			// set by our drop directive
			$scope.dropSupported = true;
			
			$scope.create_attachment = function($files, $event, $rejectedFiles) {
				function create(f, aq) {
					var data = {name: f.name, content_type: f.type, 
							resource: f, resource_type: 'file',
							question_response: aq.id};

					QuestionResponseResource.create(data)
					 .then(
							function(record) {
								delete f.$$hashKey; // screws with extend()
								// f is the original file and what's in
								// _resources for this question. Update it in 
								// place
								angular.extend(f, record.data);
							},
							function(err) {
								aq._resources.splice(aq._resources.indexOf(f), 1);
								$scope.$parent.toast(err.detail);
							}
					);
				}
				
				for (var i=0;i<$files.length;i++) {
					create($files[i], $scope.active_question);
				}
			}
			
			$scope.delete_attachment = function(attachment) {
				function del(aq, attachment) {
					return function() {
						QuestionResponseResource.delete(attachment).then(
								function() {
									aq._resources.splice(aq._resources.indexOf(attachment), 1);
								},
								function(err) {
									$scope.$parent.toast(err.detail 
														|| 'Unable to delete');
								}
						);
					}
				}
				var confirm = $mdDialog.confirm()
			      .content('Delete attachment "'+attachment.name+'"?')
			      .ariaLabel('Confirm delete')
			      .ok('Confirm')
			      .cancel('Cancel');
				$mdDialog.show(confirm).then(
					del($scope.active_question, attachment), 
					function() {
						// cancel
					}
				);
			}
			
			$scope.$on('menu.question_selected', function(e) {
				// $scope.selected_question is inherited
				if ($scope.selected_question == $scope.active_question) {
					return;
				}
				$scope.select_question($scope.selected_question);
				$scope.select_section(
					$scope.section_lookup[$scope.selected_question.section.toString()]
					);
			});
			$scope.$on('menu.section_selected', function(e) {
				// $scope.selected_section is inherited
				if ($scope.selected_section == $scope.active_section) {
					return;
				}
				$scope.select_section($scope.selected_section);
				$scope.next_question_obj=null;
				$scope.active_question=null;
				$scope.next_question();
			});
			
			$scope.mark_section_completeness = function(section) {
				var partial = false;
				var missing = false;
				for (var i=0; i<section._questions.length;i++) {
					var q = section._questions[i];
					if (q.answer) {
						partial = true;
					} else {
						missing = true;
					}
				}
				if (partial && !missing) {
					section._completed = true;
					section._partial = true;
					section._not_started = false;
				} else if (partial && missing) {
					section._completed = false;
					section._partial = true;
					section._not_started = false;
				} else if (!partial && missing) {
					section._completed = false;
					section._partial = false;
					section._not_started = true;
				}
			}
		
			$scope.show_complete = function() {
				debugger;
			}
			
			$scope.select_section = function(section) {
				$scope.active_section = section;
				for (var i=0; i<$scope.sections.length;i++) {
					$scope.sections[i]._selected = false;
				}
				section._selected = true;
			}
			
			$scope.select_question = function(question) {
		    	$scope.active_question = question;
		    	if ($scope.active_question.section !=
	    			$scope.active_section.id) {
		    			$scope.select_section($scope.section_lookup[
	    		               $scope.active_question.section.toString()                      
	    		               		  ]);
		    	}
		    	$scope.next_question_obj = $scope.find_next_question(
		    									$scope.active_section,
		    									$scope.active_question
		    							);
		    	$scope.previous_question_obj = $scope.find_previous_question(
						$scope.active_section,
						$scope.active_question
				);
		    	
		    	for (var i=0; i<$scope.questions.length;i++) {
		    		$scope.questions[i]._selected = false;
		    	}
		    	question._selected = true;
		    }
			
			$scope.find_next_section = function(section) {
				if (!section) {
					if ($scope.sections.length) {
						return $scope.sections[0];
					} else {
						return null;
					}
					
		    	} 
				
	    		for (var i=0; i<$scope.sections.length; i++) {
	    			if ($scope.sections[i] == section) {
	    				if (i == ($scope.sections.length - 1) ) {
	    					return null;
	    				} else {
	    					return $scope.sections[i + 1];
	    				}
	    			} 
		    	}
	    		debugger;
			}
			
			$scope.find_previous_section = function(section) {
				if (!section) {
					if ($scope.sections.length) {
						return $scope.select_section($scope.sections[0]);
					} else {
						return null;
					}
					
		    	} 
				
	    		for (var i=0; i<$scope.sections.length; i++) {
	    			if ($scope.sections[i] == section) {
	    				if (i == 0) {
	    					return null;
	    				} else {
	    					return $scope.sections[i - 1];
	    				}
	    			} 
		    	}
			}
			
		    $scope.next_section = function() {
		    	var next = $scope.find_next_section($scope.active_section);
		    	if (next) {
		    		$scope.select_section(next);
		    	}
		    }
		    
		    $scope.previous_section = function() {
		    	var next = $scope.find_previous_section($scope.active_section);
		    	if (next) {
		    		$scope.select_section(next);
		    	}
		    }
		    
		    $scope.find_next_question = function(section, question) {
		    	if (section == null) {
		    		return null;
		    	}
		    	
		    	if (!section._questions.length) {
		    		// No questions in this section. Skip
		    		return $scope.find_next_question(
		    				$scope.find_next_section(section),
		    				null
		    				);
		    	} else if (question == null) {
		    		// grab the first question
		    		return section._questions[0];
		    	}
		    	
		    	for (var i=0;i<section._questions.length;i++) {
		    		if (section._questions[i] == 
		    				question) {
		    			if (i >= (section._questions.length - 1)){
		    				// no more questions in this section
		    				return $scope.find_next_question(
		    						  $scope.find_next_section(section),
		    						  null
		    					   );
		    			} else {
		    				return section._questions[i+1]; 
		    			}
		    		}
		    	}
		    	// The active question isn't in this section
		    	debugger;
		    }
		    
		    $scope.find_previous_question = function(section, question) {
		    	if (section == null) {
		    		return null;
		    	}
		    	
		    	if (!section._questions.length) {
		    		// No questions in this section. Skip
		    		return $scope.find_previous_question(
		    				$scope.find_previous_section(section),
		    				null
		    				);
		    	} else if (question == null) {
		    		// grab the last question
		    		return section._questions[section._questions.length-1];
		    	}
		    	
		    	for (var i=0;i<section._questions.length;i++) {
		    		if (section._questions[i] == 
		    				question) {
		    			if (i == 0){
		    				// no earlier questions in this section
		    				return $scope.find_previous_question(
		    						  $scope.find_previous_section(section),
		    						  null
		    					   );
		    			} else {
		    				return section._questions[i-1]; 
		    			}
		    		}
		    	}
		    }
	    	
		    $scope.next_question = function() {
		    	if ($scope.next_question_obj) {
		    		$scope.select_question($scope.next_question_obj);
		    	} else {
		    		var next = $scope.find_next_question($scope.active_section,
							  							$scope.active_question
					 									)
					if (next) {
						$scope.select_question(next);
					} else {
						$scope.show_complete();
					}
		    			
		    	}
		    }
		    
		    $scope.previous_question = function() {
		    	if ($scope.previous_question_obj) {
		    		$scope.select_question($scope.previous_question_obj);
		    	} else {
		    		$scope.select_question(
		    			$scope.find_previous_question($scope.active_section,
		    									  $scope.active_question
		    									 )
		    							  );
		    	}
		    }
		    
		    $scope.process_answer = function(direction) {
		    	var prom = null;
		    	var t = $scope.active_question.question.question_type;
		    	if (t == 'multiple choice'){
		    		var selected = [];
		    		for (var i in $scope.active_question.question._choices) {
		    			var c = $scope.active_question.question._choices[i];
		    			if (c._selected) {
		    				selected.push(c.value);
		    			}
		    		}
		    		selected = selected.sort().join(';');
		    		if (selected == $scope.active_question._old_answer) {
		    			var d = $q.defer();
			    		d.resolve();
			    		prom = d.promise;
		    		} else {
			    		prom = QuestionResponse.update($scope.active_question,
			    				  {answer: selected}
	    					   );
			    		var q = $scope.active_question;
			    		prom.then(
						   		function(data) {
						   			// we overwrite this with question objects
						   			delete data.question;
						   			angular.extend(q, data);
						   		}
	    				);
		    		}
		    	} else if (t == 'file') {
		    		// the server handles this one by setting a token
		    		// text value in the answer field
		    		var d = $q.defer();
		    		d.resolve();
		    		prom = d.promise;
		    	}	
		    	else {
		    		if ($scope.active_question.answer == 
		    					$scope.active_question._old_answer) {
		    			var d = $q.defer();
			    		d.resolve();
			    		prom = d.promise;
		    		} else {
			    		prom = QuestionResponse.update($scope.active_question,
			    						{answer: $scope.active_question.answer}
					    		);
			    		var q = $scope.active_question;
			    		prom.then(
						   		function(data) {
						   			//we overwrite this with question objects
						   			delete data.question;
						   			angular.extend(q, data);
						   		}
	    				);
		    		}
		    	} 
		    	prom.then(
		    			function() {
		    				if (direction == 'next') {
		    					$scope.next_question();
		    				} else {
		    					$scope.previous_question();
		    				}
		    			},
		    			function(err) {
		    				$scope.$parent.toast(err.detail);
		    			}
		    	);
		    	
		    	
		    }
		    
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
					for (var i=0; i<records.length;i++) {
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
							$scope.questions = records;
							
							for (var i=0; i<records.length;i++) {
								records[i]._old_answer = records[i].answer;
								// we use this when adding attachments and
								// loading files later
								records[i]._resources = [];
								$scope.response_lookup[records[i].id.toString()] = records[i];
								
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
								$scope.mark_section_completeness(
										$scope.section_lookup[id]
								);
								
							}
							

							$scope.next_section();
							$scope.next_question($scope.active_section, null);
							
							return records;
						},
						function(error) {
			   				$scope.$parent.toast(error.detail);
						}
					).then(
						function(records) {
							var question_ids = [];
							for (var i=0; i<records.length;i++) {
							    if (question_ids.indexOf(
							    		records[i].question.id) == -1) {
							    	question_ids.push(records[i].question.id);
							    }
							}
							// angular will send the same param multiple times
							var qquery = '['+question_ids.toString()+']';
							QuestionChoice.list({question__in:qquery})
							    .then(
							  	    function(choices) {
							  	    	for (var y=0;y<records.length;y++){
						  	    			var rec = records[y];
						  	    			
						  	    			// only used for multiple choice
						  	    			var selected = [];
						  	    			if (rec.answer) {
						  	    				selected = rec.answer.split(';');
						  	    			}
						  	    			
								  	    	for (var i=0;i<choices.length;i++) {
								  	    		var choice = choices[i];
							  	    			if (choice.question ==
							  	    				rec.question.id) {
							  	    				if (!rec.question._choices){
							  	    					rec.question._choices=[];
							  	    				}
							  	    				rec.question._choices.push(choice);
							  	    				if (rec.question.question_type == 'multiple choice') {
							  	    					for (var j=0;j<selected.length;j++) {
							  	    						if (selected[j] == choice.value) {
							  	    							choice._selected = true;
							  	    						}
							  	    					}
							  	    				}
							  	    			}
							  	    		}
							  	    	}
							  	    	for (var y=0;y<records.length;y++){
							  	    		var rec = records[y];
							  	    		if (rec.question._choices) {
							  	    			rec.question._choices =
							  	    				rec.question._choices.sort(function(a,b) { a.order - b.order});
							  	    		}
							  	    	}
							  	    	return choices;
							  	    }); // QuestionChoice.list().then()
							return records;
						}) // QuestionResponse.list().then()
						.then(
							function(records) {
								var response_ids = [];
								for (var i=0; i<records.length;i++) {
								    response_ids.push(records[i].id);
								}
								var qquery = '['+response_ids.toString()+']';
								QuestionResponseResource.list({question_response__in: qquery})
									.then(
										function(records) {
											for (var i=0;i<records.length;i++) {
												$scope.response_lookup[
												     records[i].question_response.toString()
												   ]._resources.push(records[i]);
											}
										},
										function(err) {
											$scope.$parent.toast(err.detail);
										}
											
									);
							}	
						); // QuestionResponse.list().then()
					
				}); // ResponseSection.list().then()
}]);