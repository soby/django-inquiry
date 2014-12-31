
app.config(['$provide', function($provide) {
	$provide.factory('User',['$http','$q', function($http,$q) {
		var srvs = create_basic_services('/api/v1/core/user/', $http, $q);
	    return angular.extend(srvs,{
		      login:function(username,password) {
		    	var deferred = $q.defer();
		        $http({method:'GET',url:'/api/v1/core/user/login/',
		        	   params:{'username':username,'password':password}})
		        .success(function(data,status,headers,config) {
		            deferred.resolve(data);
		          })
		        .error(function(data,status,headers,config) {
		            deferred.reject(data);
		          });
		        return deferred.promise;
		      }, // login
		      my:function() {
			        var deferred = $q.defer();
			        $http.get('/api/v1/core/user/my/')
			          .success(function(data,status,headers,config) {
			            deferred.resolve(data);
			          })
			          .error(function(data,status,headers,config) {
			            deferred.reject(data);
			          });
			        return deferred.promise;
		      }, // my
		      logout:function(user) {
		          var deferred = $q.defer();
		          $http({method:'PATCH',url:'/api/v1/core/user/'+user.id+'/logout/'})
		            .success(function(data,status,headers,config) {
		              deferred.resolve(data);
		            })
		            .error(function(data,status,headers,config) {
		              deferred.reject(data);
		            });
		          return deferred.promise;
		       } // logout
		    }); // return angular.extend
	}]); // provide.factory
	
	$provide.factory('Survey',['$http','$q', function($http,$q) { 
	    var srvs = create_basic_services('/api/v1/survey/survey/', $http, $q);
	    return angular.extend(srvs,{
		      launch:function(survey, user) {
		    	var deferred = $q.defer();
		        $http({method:'POST',url:'/api/v1/survey/survey/'+
		        						survey.id+'/launch/',
		        	   data:{user: user.id}})
		        .success(function(data,status,headers,config) {
		            deferred.resolve(data);
		          })
		        .error(function(data,status,headers,config) {
		            deferred.reject(data);
		          });
		        return deferred.promise;
		      } // launch
	    });
	}]); // provide.factory
	
	$provide.factory('Type',['$http','$q', function($http, $q) { 
		return create_basic_services('/api/v1/survey/type/', $http, $q);
	}]); // provide.factory
	
	$provide.factory('Section',['$http','$q', function($http, $q) { 
		return create_basic_services('/api/v1/survey/section/', $http, $q);
	}]); // provide.factory
	
	$provide.factory('Question',['$http','$q', function($http, $q) { 
		return create_basic_services('/api/v1/survey/question/', $http, $q);
	}]); // provide.factory
	
	$provide.factory('Response',['$http','$q', function($http, $q) { 
		return create_basic_services('/api/v1/survey/response/', $http, $q);
	}]); // provide.factory
	
	$provide.factory('Status',['$http','$q', function($http, $q) { 
		return create_basic_services('/api/v1/survey/status/', $http, $q);
	}]); // provide.factory
	
	$provide.factory('ResponseSection',['$http','$q', function($http, $q) { 
		return create_basic_services('/api/v1/survey/responsesection/', 
									 $http, 
									 $q);
	}]); // provide.factory
	
	$provide.factory('QuestionResponse',['$http','$q', function($http, $q) { 
		return create_basic_services('/api/v1/survey/questionresponse/', 
				     				 $http,
									 $q);
	}]); // provide.factory
	
}]); // app.config