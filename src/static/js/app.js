var demonDiceApp = angular.module('demonDiceApp', ['ui.bootstrap']);

demonDiceApp.controller('DemonDiceCtrl',
    ['$scope', '$http', function ($scope, $http) {
    $scope.pool = 5;
    $scope.item = 0;
    $scope.diff = 6;
    $scope.torment = 5;
    $scope.charmed = 1;
    $scope.status = {
        'charOpen': false,
        'torOpen': false
    };
    $scope.show = '';

    //roll
    $scope.rolls = [];

    //sim
    $scope.simData = '';


    $scope.dec = function(item) {
        return Math.max(item-1, 0);
    };

    Object.defineProperty($scope, 'totalPool', {
        get: function() {
            return $scope.pool + $scope.item;
        }
    });

    $scope.roll = function(diff, pool, torment, charmed) {
        $scope.show = 'roll';
        console.log([diff, pool, torment, charmed])
        $http.get('/api/roll/' +
                            diff + '/' +
                            pool + '/' +
                            torment + '/' +
                            charmed + '/').
        success(function(data) {
            data.iPool = $scope.item;
            data.bPool = $scope.pool;
            $scope.rolls.unshift(data);
        });
    };

    $scope.sim = function(diff, pool, torment, charmed) {
        $scope.show = 'sim';
        console.log([diff, pool, torment, charmed])
        $http.get('/api/sim/' +
                            diff + '/' +
                            pool + '/' +
                            torment + '/' +
                            charmed + '/').
        success(function(data) {
            data.iPool = $scope.item;
            data.bPool = $scope.pool;
            $scope.simData = data;
        });
    };

    $scope.enhance = function(diff, pool, torment, charmed) {
        $scope.show = 'enhance';
        console.log([diff, pool, torment, charmed])
        $http.get('/api/roll/' +
                            diff + '/' +
                            pool + '/' +
                            torment + '/' +
                            charmed + '/').
        success(function(data) {
            data.iPool = $scope.item;
            data.bPool = $scope.pool;
            $scope.rolls.unshift(data);
        });
    };
}]);
