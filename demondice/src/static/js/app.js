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

    //calc
    $scope.calcData = '';

    //enhance
    $scope.enhanceData = '';


    $scope.dec = function(item) {
        // decrement with a floor of 0
        return Math.max(item-1, 0);
    };

    Object.defineProperty($scope, 'totalPool', {
        get: function() {
            return $scope.pool + $scope.item;
        }
    });

    $scope.roll = function(diff, pool, torment, charmed) {
        // roll a dice pool.  Arguments could be pulled from
        // $scope.  It was done this way under a thought that
        // they could be altered while the dice are being rolled
        // A bit of an overthink for the problem space.
        $scope.show = 'roll';
        data = roll(diff, pool, torment, charmed);
        data.iPool = $scope.item;
        data.bPool = $scope.pool;
        data.id = $scope.id;
        $scope.id++;
        $scope.rolls.unshift(data);
        if ($scope.rolls.length > 30) {
            $scope.rolls.length = 30
        };
    };

/*

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
*/

    $scope.reroll = function(data) {
        // re-roll a previoiusly rolled dice pool
        $scope.pool = data.bPool;
        $scope.item = data.iPool;
        $scope.diff = data.diff;
        $scope.charmed = data.charmed;
        $scope.torment = data.torment;
        $scope.roll($scope.diff, $scope.pool+$scope.item, $scope.torment, $scope.charmed);
    };

    $scope.isShade = function (data) {
        // done here instead of ng-even so each roll will will
        // retain the same shading as new rolls are added
        // rather than changing depending on it's place in the array
        if ((data.id % 2) == 0) {
            return "shade";
        }
    };

    $scope.calc = function(diff, pool, torment, charmed) {
        // calculate statistics for  a dice pool
        $scope.show = 'calc';
        data = calc(pool, diff, torment, charmed);
        data.iPool = $scope.item;
        data.bPool = $scope.pool;
        $scope.calcData = data;
    };

    $scope.enhance = function() {
        // Calculate the most advantage and legal use of
        // enhance for each success level
        $scope.show = 'enhance';
        data = enhance($scope.diff, $scope.pool, $scope.item, $scope.charmed);
        $scope.enhanceData = data;
    };

    $scope.enhRoll = function(enh) {
        // Roll the passed in enhancement level
        $scope.diff = enh[0].diff;
        $scope.item = enh[0].tool;
        $scope.roll($scope.diff, $scope.pool+$scope.item, $scope.torment, $scope.charmed);
    }
}]);
