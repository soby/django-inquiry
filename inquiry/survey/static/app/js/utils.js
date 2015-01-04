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
		        $http.delete(url_base+obj.id+'/')
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
	      meta: function(oid) {
	    	    var deferred = $q.defer();
		        $http.get(url_base+oid+'/meta/')
		          .success(function(data,status,headers,config) {
		            deferred.resolve(data);
		          })
		          .error(function(data,status,headers,config) {
		            deferred.reject(data);
		          });
		        return deferred.promise;
	      }, // meta
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
		    		  prom = srv.get(val).then(
		    					  record_setter(record, field)
		    					 );
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
	    	  function record_list_setter(records, field) {
	    		  return function(objs) {
	    			  for (var i in objs) {
	    				  for (var y in records) {
	    					  if (objs[i].id.toString() == 
	    						  records[y][field].toString()) {
	    						  	records[y][field] = objs[i];
	    					  }
	    				  }
	    			  }
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
		    		  
		    		  var pks = [];
		    		  for (i in records) {
		    			  var val = records[i][field];
			    		  if (!val) {
			    			  continue;
			    		  }
			    		  if (pks.indexOf(val) == -1) {
			    			  pks.push(val);
			    		  }
		    		  }
		    		  // angular will break lists up into multiple qs
		    		  // params
		    		  var pkquery = '['+pks.toString()+']';
		    		  prom = srv.list({pk__in: pkquery}).then(
		    				  record_list_setter(records, field)
		    		  );
		    		  proms.push(prom);
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
	      } // list_include
	} // return
} // create_basic_services