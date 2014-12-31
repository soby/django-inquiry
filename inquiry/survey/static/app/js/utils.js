function create_basic_services(url_base, $http, $q) {
	return {
	      get: function(oid) {
	    	    var deferred = $q.defer();
		        $http.get(url_base+oid+'/')
		          .success(function(data,status,headers,config) {
		            deferred.resolve(data);
		          })
		          .error(function(data,status,headers,config) {
		            deferred.reject(data);
		          });
		        return deferred.promise;
	      }, // get
	      list:function(filters) {
		        var deferred = $q.defer();
		        $http.get(url_base,{params:filters})
		          .success(function(data,status,headers,config) {
		            deferred.resolve(data);
		          })
		          .error(function(data,status,headers,config) {
		            deferred.reject(data);
		          });
		        return deferred.promise;
	      }, // list
	      create: function(data) {
		        var deferred = $q.defer();
		        $http.post(url_base,data)
		          .success(function(data,status,headers,config) {
		            deferred.resolve(data);
		          })
		          .error(function(data,status,headers,config) {
		            deferred.reject(data);
		          });
		        return deferred.promise;
	      }, // create
	      update: function(obj, data) {
		        var deferred = $q.defer();
		        $http.patch(url_base+obj.id+'/',data)
		          .success(function(data,status,headers,config) {
		            deferred.resolve(data);
		          })
		          .error(function(data,status,headers,config) {
		            deferred.reject(data);
		          });
		        return deferred.promise;
	      }, // update
	      delete: function(obj) {
		        var deferred = $q.defer();
		        $http.delete(url_base+obj.id+'/',data)
		          .success(function(data,status,headers,config) {
		            deferred.resolve(data);
		          })
		          .error(function(data,status,headers,config) {
		            deferred.reject(data);
		          });
		        return deferred.promise;
	      }, // delete
	      count: function(filters) {
	    	    var deferred = $q.defer();
		        $http.get(url_base+'count/',{params:filters})
		          .success(function(data,status,headers,config) {
		            deferred.resolve(data['count']);
		          })
		          .error(function(data,status,headers,config) {
		            deferred.reject(data);
		          });
		        return deferred.promise;
	      }, // count
	      include: function(configList) {
	    	  // config should look like:
	    	  // [{'field':'someField','service':Srv}]
	    	  // TODO {'many': false <optional}
	    	  function record_setter(record, field) {
	    		  return function(obj) {
	    			  record[field] = obj;
	    		  }
	    	  }
	    	  
	    	  function f(record) {
	    		  var deferred = $q.defer();
	    		  var proms = []
	    		  var prom;
		    	  for (i in configList) {
		    		  var config = configList[i];
		    		  var srv = config['service'];
		    		  var field = config['field'];
		    		  var val = record[field];
		    		  if (!val) {
		    			  continue;
		    		  }
		    		  prom = srv.get(val).then(record_setter(record,field));
		    		  proms.push(prom);
		    	  }
		    	  $q.all(proms).then(
		    	      function() {
		    	    	  deferred.resolve(record);
		    	      },
		    	      function(err) {
		    	    	  deferred.reject(err);
		    	      }
		    	  );
		    	  return deferred.promise;
	    	  }
	    	  return f
	      }, // include
	      list_include: function(configList) {
	    	  // Same as above but works on lists of records
	    	  // TODO: Make efficient
	    	  function record_setter(record, field) {
	    		  return function(obj) {
	    			  record[field] = obj;
	    		  }
	    	  }
	    	  
	    	  function f(records) {
	    		  var deferred = $q.defer();
	    		  var proms = []
	    		  var prom;
		    	  for (i in configList) {
		    		  var config = configList[i];
		    		  var srv = config['service'];
		    		  var field = config['field'];
		    		  
		    		  for (i in records) {
		    			  var val = records[i][field];
			    		  if (!val) {
			    			  continue;
			    		  }
		    			  prom = srv.get(val).then(
		    					    record_setter(records[i],field)
		    					  );
		    			  proms.push(prom);
		    		  }
		    	  }
		    	  $q.all(proms).then(
		    	      function() {
		    	    	  deferred.resolve(records);
		    	      },
		    	      function(err) {
		    	    	  deferred.reject(err);
		    	      }
		    	  );
		    	  return deferred.promise;
	    	  }
	    	  return f
	      }, // include
	} // return
} // create_basic_services