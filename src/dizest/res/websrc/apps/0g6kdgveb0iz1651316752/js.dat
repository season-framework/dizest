let wiz_controller = async ($sce, $scope, $timeout) => {
    let _$timeout = $timeout;
    $timeout = (timestamp) => new Promise((resolve) => _$timeout(resolve, timestamp));

    $scope.link = async (link) => {
        location.href = link;
    }

    let DEFAULT_QUERY = {
        page: 1,
        dump: 20,
        text: ''
    };

    $scope.workflow = {};
    $scope.workflow.list = [];
    $scope.workflow.loading = false;
    $scope.workflow.tab = 'private';

    $scope.workflow.lastpage = 0;
    $scope.workflow.query = angular.copy(DEFAULT_QUERY);

    $scope.workflow.pagination = async () => {
        let lastpage = $scope.workflow.lastpage * 1;
        let startpage = Math.floor(($scope.workflow.query.page - 1) / 10) * 10 + 1;
        $scope.workflow.pages = [];
        for (var i = 0; i < 10; i++) {
            if (startpage + i > lastpage) break;
            $scope.workflow.pages.push(startpage + i);
        }
        await $timeout();
    }

    $scope.workflow.load = {};
    $scope.workflow.load.current = async (init) => {
        if (init) {
            $scope.workflow.query.page = 1;
        }

        if ($scope.workflow.tab == 'private') {
            await $scope.workflow.load.private();
        } else {
            await $scope.workflow.load.hub();
        }
    }

    $scope.workflow.load.page = async (page) => {
        if (page < 1) {
            toastr.error('첫 페이지 입니다');
            return;
        }
        if (page > $scope.workflow.lastpage) {
            toastr.error('마지막 페이지 입니다');
            return;
        }

        if ($scope.workflow.query.page == page) {
            return;
        }

        $scope.workflow.query.page = page;
        await $scope.workflow.load.current();
    }

    $scope.workflow.load.private = async (init) => {
        if (init) {
            $scope.workflow.query = angular.copy(DEFAULT_QUERY);
        }

        let q = angular.copy($scope.workflow.query);
        let res = await wiz.API.async("myworkflow", q);
        $scope.workflow.list = res.data.result;

        $scope.workflow.lastpage = res.data.lastpage;
        $scope.workflow.tab = 'private';
        $scope.workflow.loading = true;

        await $scope.workflow.pagination();
        await $timeout();
    }

    $scope.workflow.load.hub = async (init) => {
        if (init) {
            $scope.workflow.query = angular.copy(DEFAULT_QUERY);
        }

        let q = angular.copy($scope.workflow.query);
        let res = await wiz.API.async("hubworkflow", q);
        $scope.workflow.list = res.data.result;
        $scope.workflow.lastpage = res.data.lastpage;
        $scope.workflow.tab = 'hub';
        $scope.workflow.loading = true;

        await $scope.workflow.pagination();
        await $timeout();
    }

    $scope.workflow.gen = async () => {
        let wpdata = angular.copy($scope.workflow.data);
        let transform = angular.copy($scope.workflow.transform);
        await wiz.API.async('create', {data: JSON.stringify(wpdata), transform: JSON.stringify(transform)})
        await $scope.workflow.load.current();
        $('#import-modal').modal("hide");
    }

    $scope.workflow.import = function () {
        $('#import-file').click();
    }

    $scope.apps = await wiz.API.async("myapps");
    $scope.apps = $scope.apps.data;
    $scope.appsmap = {};
    for (let i = 0; i < $scope.apps.length; i++) {
        $scope.appsmap[$scope.apps[i].id] = $scope.apps[i];
    }

    $('#import-file').change(async () => {
        let fr = new FileReader();
        fr.onload = async () => {
            let data = fr.result;
            data = JSON.parse(data);
            delete data.id;
            data.visibility = 'private';
            data.updatepolicy = 'auto';

            $scope.workflow.transform = {};
            for (let key in data.apps) {
                $scope.workflow.transform[key] = { mode: 'new' };
                if ($scope.appsmap[key]) {
                    $scope.workflow.transform[key].mode = 'link';
                    $scope.workflow.transform[key].id = key;
                }
            }

            $scope.workflow.data = data;
            await $timeout();
            $('#import-modal').modal("show");
        };
        fr.readAsText($('#import-file').prop('files')[0]);
    });

    await $scope.workflow.load.private();
}
