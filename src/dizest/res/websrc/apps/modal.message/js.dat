let wiz_controller = ($sce, $scope, $timeout) => {
    $scope.event = {};

    $scope.event.submit = async () => {
        $scope.response = true;
        $('#' + wiz.render_id).modal("hide");
    }

    $scope.event.close = async () => {
        $('#' + wiz.render_id).modal("hide");
    }

    $('#' + wiz.render_id).on("hidden.bs.modal", async () => {
        wiz.response("modal-show", $scope.response);
    });

    wiz.bind("modal-show", (data) => {
        $scope.data = data;
        $('#' + wiz.render_id).modal("show");
        $scope.response = false;
        $timeout();
    });
}