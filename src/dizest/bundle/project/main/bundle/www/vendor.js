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

Array.prototype.up = function (item) {
    let i = this.indexOf(item);
    if (i < 1) return;
    tmp = this[i];
    this.splice(i, 1);
    this.splice(i - 1, 0, tmp);
}

Array.prototype.down = function (item) {
    let i = this.indexOf(item);
    tmp = this[i];
    this.splice(i, 1);
    this.splice(i + 1, 0, tmp);
}

Date.prototype.format = function (f) {
    if (!this.valueOf()) return " ";

    let weekName = ["일요일", "월요일", "화요일", "수요일", "목요일", "금요일", "토요일"];
    let d = this;

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

Function.prototype.proceed = async (fn, obj) => {
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

Number.prototype.zf = function (len) {
    return this.toString().zf(len);
};

String.prototype.number_format = function () {
    let num = parseFloat(this);
    if (isNaN(num)) return "0";
    return num.format();
};

String.prototype.string = function (len) {
    let s = '', i = 0;
    while (i++ < len) { s += this; }
    return s;
};

String.prototype.zf = function (len) {
    return "0".string(len - this.length) + this;
};