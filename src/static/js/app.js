var demonDiceApp = angular.module('demonDiceApp', ['ui.bootstrap']);

demonDiceApp.controller('DemonDiceCtrl',
    ['$scope', '$http', function ($scope, $http) {
    $scope.id = 0;
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

    //enhance
    $scope.enhanceData = '';


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
            data.id = $scope.id;
            $scope.id++;
            $scope.rolls.unshift(data);
            if ($scope.rolls.length > 30) {
                $scope.rolls.length = 30
            };
        });
    };

    $scope.reroll = function(data) {
        $scope.pool = data.bPool;
        $scope.item = data.iPool;
        $scope.diff = data.diff;
        $scope.charmed = data.charmed;
        $scope.torment = data.torment;
        $scope.roll($scope.diff, $scope.pool+$scope.item, $scope.torment, $scope.charmed);
    };

    $scope.isShade = function (data) {
        if ((data.id % 2) == 0) {
            return "shade";
        }
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

    $scope.enhance = function() {
        $scope.show = 'enhance';
        $http.get('/api/enhance/' +
                            $scope.diff + '/' +
                            $scope.pool + '/' +
                            $scope.item + '/' +
                            $scope.charmed + '/').
        success(function(data) {
            $scope.enhanceData = data.results;
        });
    };

    $scope.enhRoll = function(enh) {
        console.log(enh)
        $scope.diff = enh[0].diff;
        $scope.item = enh[0].tool;
        $scope.roll($scope.diff, $scope.pool+$scope.item, $scope.torment, $scope.charmed);
    }
}]);
