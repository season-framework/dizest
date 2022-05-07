(function (dragger) {
    dragger.directive('ngDrag', function ($compile, $parse) {
        return function (scope, element, attrs) {
            var config = scope.$eval(attrs.ngDrag);
            if (!config) config = {};
            if (!config.onmove)
                config.onmove = function (self, move) {
                    self.target().css('left', (self.pos.left + move.x) + 'px');
                    self.target().css('top', (self.pos.top + move.y) + 'px');
                };

            var _dragger = draggerjs(element, config);
            _dragger.attrs = attrs;
            _dragger.scope = scope;

            if (!config.draggers) config.draggers = [];
            config.draggers.push(_dragger);
        };
    }).directive('ngDrop', function ($compile, $parse) {
        return function (scope, element, attrs) {
            var config = scope.$eval(attrs.ngDrop);
            if (!config) config = {};
            if (!config.text) config.text = "Drop File"

            $(element).css("position", "relative");

            var onstage = $("<div></div>")
            onstage.css("align-items", "center");
            onstage.css("position", "absolute");
            onstage.css("left", 0);
            onstage.css("top", 0);
            onstage.css("width", "100%");
            onstage.css("height", "100%");
            onstage.css("background", "rgba(0,0,0,.7)");
            onstage.css("display", "none");
            onstage.css("color", "#fff");
            onstage.css("text-align", "center");
            onstage.css("font-size", "32px");
            onstage.html("<div style='width: 100%; text-align: center;'>" + config.text + "</div>");
            $(element).append(onstage);

            $(element).on("dragenter", function (e) {
                e.preventDefault();
                onstage.css("display", "flex");
            });

            $(element).on("dragenter", function (e) {
                e.stopPropagation();
                e.preventDefault();
            });

            $(onstage).on("dragover", function (e) {
                e.stopPropagation();
                e.preventDefault();
            });

            $(onstage).on("dragleave", function (e) {
                e.stopPropagation();
                e.preventDefault();
                onstage.css("display", "none");
            });

            function getFilesWebkitDataTransferItems(dataTransferItems) {
                let files = [];

                function traverseFileTreePromise(item, path = '') {
                    return new Promise(resolve => {
                        if (item.isFile) {
                            item.file(file => {
                                file.filepath = path + file.name //save full path
                                files.push(file)
                                resolve(file)
                            })
                        } else if (item.isDirectory) {
                            let dirReader = item.createReader()
                            dirReader.readEntries(entries => {
                                let entriesPromises = []
                                for (let entr of entries)
                                    entriesPromises.push(traverseFileTreePromise(entr, path + item.name + "/"))
                                resolve(Promise.all(entriesPromises))
                            })
                        }
                    })
                }


                return new Promise((resolve, reject) => {
                    let entriesPromises = []
                    for (let it of dataTransferItems)
                        entriesPromises.push(traverseFileTreePromise(it.webkitGetAsEntry()));

                    Promise.all(entriesPromises)
                        .then(entries => {
                            resolve(files);
                        })
                })
            }

            $(onstage).on("drop", function (e) {
                e.preventDefault();
                getFilesWebkitDataTransferItems(e.originalEvent.dataTransfer.items).then(function (files) {
                    if (config.ondrop) config.ondrop(e, files);
                    onstage.css("display", "none");
                });
            });

        };
    });
})(angular.module('season.dragger', []));