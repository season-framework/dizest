toastr.options = {
    "closeButton": false,
    "debug": false,
    "newestOnTop": false,
    "progressBar": false,
    "positionClass": "toast-bottom-right",
    "preventDuplicates": false,
    "onclick": null,
    "showDuration": 300,
    "hideDuration": 1000,
    "timeOut": 5000,
    "extendedTimeOut": 1000,
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
};

Function.prototype.proceed = async (fn, obj)=> {
    let args = fn.getParamNames();
    let params = [];
    for (let i = 0; i < args.length; i++) {
        let key = args[i];
        if (obj[key]) {
            params.push('obj["' + key + '"]');
        } else {
            params.push('null');
        }
    }

    let execstr = "let __wizformproc = async () => { await fn(" + params.join() + ")}; __wizformproc();";
    eval(execstr);
}

Function.prototype.getParamNames = function () {
    var STRIP_COMMENTS = /((\/\/.*$)|(\/\*[\s\S]*?\*\/))/mg;
    var ARGUMENT_NAMES = /([^\s,]+)/g;
    function getParamNames(func) {
        var fnStr = func.toString().replace(STRIP_COMMENTS, '');
        var result = fnStr.slice(fnStr.indexOf('(') + 1, fnStr.indexOf(')')).match(ARGUMENT_NAMES);
        if (result === null)
            result = [];
        return result;
    }
    return getParamNames(this);
}

Number.prototype.format = function () {
    if (this == 0) return 0;
    var reg = /(^[+-]?\d+)(\d{3})/;
    var n = (this + '');
    while (reg.test(n)) n = n.replace(reg, '$1' + ',' + '$2');
    return n;
};

String.prototype.number_format = function () {
    var num = parseFloat(this);
    if (isNaN(num)) return "0";

    return num.format();
};

Array.prototype.remove = function () {
    var what, a = arguments,
        L = a.length,
        ax;
    while (L && this.length) {
        what = a[--L];
        while ((ax = this.indexOf(what)) !== -1) {
            this.splice(ax, 1);
        }
    }
    return this;
};

String.prototype.string = function (len) {
    var s = '',
        i = 0;
    while (i++ < len) { s += this; }
    return s;
};
String.prototype.zf = function (len) { return "0".string(len - this.length) + this; };
Number.prototype.zf = function (len) { return this.toString().zf(len); };

Date.prototype.format = function (f) {
    if (!this.valueOf()) return " ";

    var weekName = ["일요일", "월요일", "화요일", "수요일", "목요일", "금요일", "토요일"];
    var d = this;

    return f.replace(/(yyyy|yy|MM|dd|E|hh|mm|ss|a\/p)/gi, function ($1) {
        switch ($1) {
            case "yyyy":
                return d.getFullYear();
            case "yy":
                return (d.getFullYear() % 1000).zf(2);
            case "MM":
                return (d.getMonth() + 1).zf(2);
            case "dd":
                return d.getDate().zf(2);
            case "E":
                return weekName[d.getDay()];
            case "HH":
                return d.getHours().zf(2);
            case "hh":
                return ((h = d.getHours() % 12) ? h : 12).zf(2);
            case "mm":
                return d.getMinutes().zf(2);
            case "ss":
                return d.getSeconds().zf(2);
            case "a/p":
                return d.getHours() < 12 ? "AM" : "PM";
            default:
                return $1;
        }
    });
};

if (!window.season_wiz) {
    window.season_wiz = (() => {
        let obj = {};
        obj.__cache__ = {};

        obj.load = (app_id, namespace, app_namespace, render_id) => {
            let wiz = {};
            wiz.id = app_id;
            wiz.namespace = namespace;
            wiz.app_namespace = app_namespace;
            wiz.render_id = render_id;

            wiz.socket = {};
            wiz.socket.active = false;

            if (window.io) {
                wiz.socket.active = true;
                wiz.socket.get = (socketnamespace) => {
                    let socketns = "/wiz/api/" + app_namespace;
                    if (socketnamespace) socketns = "/wiz/api/" + socketnamespace;
                    if (wiz.branch != 'master') socketns = socketns + "/" + wiz.branch;

                    wiz.socket_instance = window.io(socketns);
                    return wiz.socket_instance;
                }
            }

            wiz.API = {
                url: (fnname) => '/wiz/api/' + app_id + '/' + fnname,
                function: (fnname, data, cb, opts) => {
                    let _url = wiz.API.url(fnname);
                    let ajax = {
                        url: _url,
                        type: 'POST',
                        data: data
                    };

                    if (opts) {
                        for (let key in opts) {
                            ajax[key] = opts[key];
                        }
                    }

                    $.ajax(ajax).always((a, b, c) => {
                        cb(a, b, c);
                    });
                },
                async: (fnname, data, opts = {}) => {
                    const _url = wiz.API.url(fnname);
                    let ajax = {
                        url: _url,
                        type: "POST",
                        data: data,
                        ...opts,
                    };

                    return new Promise((resolve) => {
                        $.ajax(ajax).always(function (a, b, c) {
                            resolve(a, b, c);
                        });
                    });
                }
            };

            wiz.timeout = (timestamp) => new Promise((resolve) => {
                setTimeout(resolve, timestamp);
            });

            wiz._event = {};
            wiz._response = {};
            wiz._response_activator = {};

            wiz.bind = (name, fn, err = true) => {
                wiz._event[name] = (data) => new Promise(async (resolve, reject) => {
                    let res = await fn(data);
                    if (res) {
                        return resolve(res);
                    }

                    wiz._response_activator[name] = true;

                    let response_handler = () => {
                        // if not activate, stop loop
                        if (!wiz._response_activator[name]) {
                            if (err) reject("deprecated event `" + name + "` of `" + wiz.namespace + "`");
                            return;
                        }

                        // if activate 
                        if (name in wiz._response) {
                            let resp = wiz._response[name];
                            delete wiz._response[name];
                            delete wiz._response_activator[name];
                            resolve(resp);
                            return;
                        }

                        setTimeout(response_handler, 100);
                    }
                    response_handler();
                });
                return wiz;
            };

            wiz.response = (name, data) => {
                if (!wiz._response_activator[name]) return;
                wiz._response[name] = data;
                return wiz;
            }

            wiz.connect = (id) => {
                if (!obj.__cache__[id]) return null;
                let connected_wiz = obj.__cache__[id];
                let _obj = {};

                _obj.event = async (name) => {
                    delete connected_wiz._response_activator[name];
                    await wiz.timeout(200);

                    if (connected_wiz._event[name]) {
                        let res = await connected_wiz._event[name](_obj._data);
                        return res;
                    }
                    return null;
                };

                _obj._data = null;
                _obj.data = (data) => {
                    _obj._data = data;
                    return _obj;
                }
                return _obj;
            }

            obj.__cache__[namespace] = wiz;
            obj.__cache__[app_id] = wiz;

            return wiz;
        }

        return obj;
    })();
}
