window.resize = (function () {
	function Resize(){
		
	}
	
	Resize.prototype = {
		init: function(outputQuality) {
			this.outputQuality = (outputQuality === 'undefined' ? 1 : outputQuality);
		},
		photo: function(file, maxSize, outputType, callback) {
			var _this = this;
			var reader = new FileReader();
			reader.onload = function (readerEvent) {
				_this.resize(readerEvent.target.result, maxSize, outputType, callback);
			};
			reader.readAsDataURL(file);
		},
		resize: function(dataURL, maxSize, outputType, callback) {
			var _this = this;
			var image = new Image();

			image.onload = function () {

				// Resize image
				var canvas = document.createElement('canvas'),
					width = image.width,
					height = image.height;
				if (width > height) {//가로모드
					if (width > maxSize) {
						height *= maxSize / width;
						width = maxSize;
					}
				} else {//세로모드
					if (height > maxSize) {
						width *= maxSize / height;
						height = maxSize;
					}
				}
				canvas.width = width;
				canvas.height = height;
					
				canvas.getContext('2d').drawImage(image, 0, 0, width, height);
					
				_this.output(canvas, outputType, callback);
			};
			image.onerror=function(){
				return;
			};
			image.src = dataURL;
		},
		output: function(canvas, outputType, callback) {
			switch (outputType) {

				case 'file':
					canvas.toBlob(function (blob) {
						callback(blob);
					}, 'image/png', 0.8);
					break;

				case 'dataURL':
					callback(canvas.toDataURL('image/png', 0.8));
					break;

			}
		}
	};//prototype end
	
	return Resize;
}());