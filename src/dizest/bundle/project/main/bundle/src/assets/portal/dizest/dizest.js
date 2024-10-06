window.dizest = (() => {
    let Style = {
        base: [
            "color: #fff",
            "background-color: #444",
            "padding: 2px 4px",
            "border-radius: 2px"
        ],
        warning: [
            "color: #eee",
            "background-color: red"
        ],
        success: [
            "background-color: green"
        ]
    };

    let obj = {};

    obj.log = function () {
        let style = Style.base.join(';') + ';';
        style += Style.base.join(';');
        console.log(`%cdizest.js`, style, ...arguments);
    }

    obj.url = (fnname) => "{url}/" + fnname;

    obj.async = obj.function = obj.call = async (fnname, data, opts = {}) => {
        let _url = obj.url(fnname);

        let ajax = {
            url: _url,
            type: "POST",
            data: data,
            ...opts
        };

        return new Promise((resolve) => {
            $.ajax(ajax).always(function (a, b, c) {
                resolve(a, b, c);
            });
        });
    };
    return obj;
})();