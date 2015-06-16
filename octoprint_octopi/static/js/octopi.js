$(function() {
    function OctoPiViewModel(parameters) {
        var self = this;

        self.octopi_version = ko.observable();
        self.octopi_commit = ko.observable();
        self.octopi_ips = ko.observableArray();

        self.requestData = function() {
            $.ajax({
                url: API_BASEURL + "plugin/octopi",
                type: "GET",
                dataType: "json",
                success: self.fromResponse
            });
        };

        self.fromResponse = function(response) {
            self.octopi_version(response.version);
            self.octopi_commit(response.commit);
            self.octopi_ips(response.ips);
        };

        self.onUserLoggedIn = function(user) {
            if (user.admin) {
                self.requestData();
            }
        };

    }

    // view model class, parameters for constructor, container to bind to
    ADDITIONAL_VIEWMODELS.push([OctoPiViewModel, [], ["#settings_plugin_octopi"]]);
});
