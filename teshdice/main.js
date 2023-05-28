window.onload = function () {

    var roll_die = function rollDice(min, max) {
        return min + Math.floor(Math.random() * (max - min + 1))
    }

    var stats = [
        { 'name': 'Strength', 'value': 12 },
        { 'name': 'Dexterity', 'value': 20 },
        { 'name': 'Constitution', 'value': 21 },
        { 'name': 'Intelligence', 'value': 15 },
        { 'name': 'Tech', 'value': 15 },
        { 'name': 'Charisma', 'value': 16 },
        { 'name': 'Luck', 'value': 4 },
        { 'name': 'Psi', 'value': 18 },
        { 'name': 'Daemon Stat', 'value': 5},
        { 'name': 'None', 'value': 0 },
    ]

    var stats_map = stats.reduce(function (map, obj) {
        map[obj.name] = obj.value;
        return map;
    }, {});

    var skills = [
        { 'name': 'Technomancy', 'value': 10 },
        { 'name': 'Creation Domain', 'value': 10 },
        { 'name': 'Daemon Domain', 'value': 10 },
        { 'name': 'Metaphysics Domain', 'value': 10 },
        { 'name': 'None', 'value': 0 },
        { "name": "AV Tech", "value": 1 },
        { "name": "Aero Tech", "value": 1 },
        { "name": "Basic Tech[8]", "value": 6 },
        { "name": "Capital Ship Repair[8]", "value": 7 },
        { "name": "Computer Science[8]", "value": 9 },
        { "name": "Electronics[8]", "value": 7 },
        { "name": "Electronic Security[8]", "value": 7 },
        { "name": "Power Systems[8+2/4]", "value": 6 },
        { "name": "Robot Repair [8]", "value": 7 },
        { "name": "Starship Repair [8]", "value": 6 },
        { "name": "Weaponsmith [8]", "value": 6 },
        { "name": "Communications[8]", "value": 1 },
        { "name": "Starship Pilot", "value": 1 },
        { "name": "Sensors", "value": 3 },
        { "name": "Starship Shields", "value": 1 },
        { "name": "Capital Starship Shields[8|BB]", "value": 7 },
        { "name": "Athletics", "value": 4 },
        { "name": "Awareness/Notice", "value": 6 },
        { "name": "Brawling", "value": 2 },
        { "name": "Handgun", "value": 2 },
        { "name": "Hide/Evade", "value": 2 },
        { "name": "Rifle", "value": 2 },
        { "name": "Stealth", "value": 5 },
        { "name": "Streetwise", "value": 3 },
        { "name": "Zero G Maneuver", "value": 2 },
        { "name": "Education/General Knowledge[8]", "value": 7 },
        { "name": "History", "value": 6 },
        { "name": "Lang: Angelic", "value": 8 },
        { "name": "Lang: Nivelian", "value": 4 },
        { "name": "Physics", "value": 4 },
        { "name": "Math", "value": 6 },
        { "name": "Teach", "value": 2 },
        { "name": "Chipped Skill", "value": 5 },
        { "name": "Borrowed Daemon Skill", "value": 5 },
    ]

    var skills_map = skills.reduce(function (map, obj) {
        map[obj.name] = obj.value;
        return map;
    }, {});

    var bonuses = [
        { 'name': 'Techlore', 'value': 3, 'var': 'techlore', 'selected': false },
        { 'name': 'Group Mind', 'value': 2, 'var': 'group_mind', 'selected': false },
        { 'name': 'Half Domain', 'value': 5, 'var': 'half_domain', 'selected': false },
        { 'name': 'Drone Mod Bonus', 'value': 5, 'var': 'mod_bonus', 'selected': false },
    ]

    var bonuses_map = skills.reduce(function (map, obj) {
        map[obj.name] = obj
        return map;
    }, {});

    var app = new Vue({
        el: '#app',
        data: {
            stats: stats,
            stats_map: stats_map,
            skills: skills,
            skills_map: skills_map,
            bonuses: bonuses,
            bonuses_map: bonuses_map,

            selected_stat: "None",
            selected_skill: "None",

            total_bonus: 0,

            die: 0,
            result: 0



        },
        methods: {
            roll: function (event) {
                this.calculate_bonuses()
                stat = this.stats_map[this.selected_stat]
                skill = this.skills_map[this.selected_skill]
                this.die = roll_die(1, 10)
                this.result = stat + skill + this.die + this.total_bonus
                // this.result = stat + skill
            },
            calculate_bonuses: function () {
                this.total_bonus = 0;
                const selected = this.bonuses.filter(bonus => bonus.selected)
                const reducer = (accumulator, currentValue) => accumulator + currentValue.value
                this.total_bonus = selected.reduce(reducer, 0)
                console.log(this.total_bonus)

            }

        }
    })
}
