var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var CustomScrollbarVertical = /** @class */ (function () {
    function CustomScrollbarVertical(scrollbarContainerEl, contentEl) {
        this.dragging = false;
        this.dragStartContentScrollTop = 0;
        this.dragStartY = 0;
        this.dragOffsetY = 0;
        this.scrollbarContainerEl = scrollbarContainerEl;
        this.contentEl = contentEl;
        this.initDOM();
        this.registerEvents();
        this.updateScrollbarEl();
    }
    CustomScrollbarVertical.prototype.initDOM = function () {
        this.scrollbarEl = document.createElement('div');
        this.scrollbarEl.classList.add('scrollbar', 'scrollbar-vertical');
        this.scrollbarContainerEl.appendChild(this.scrollbarEl);
    };
    CustomScrollbarVertical.prototype.registerEvents = function () {
        var _this = this;
        // scroll to click pos when clicking the scrollbar track
        this.scrollbarContainerEl.addEventListener('mousedown', function (e) {
            e.preventDefault();
            e.stopPropagation();
            var clickPosScrollTop = (e.clientY - _this.scrollbarEl.clientHeight / 2) /
                _this.scrollbarContainerEl.scrollHeight;
            _this.scrollContent(_this.contentEl.scrollHeight * clickPosScrollTop, 'instant');
        });
        this.contentEl.addEventListener('scroll', function () { return _this.updateScrollbarEl(); });
        // register scrollbarEl.mousedown event, start handling dragging
        this.scrollbarEl.addEventListener('mousedown', function (e) {
            e.preventDefault();
            e.stopPropagation();
            _this.dragStart();
            _this.dragStartContentScrollTop = _this.contentEl.scrollTop;
            _this.dragStartY = parseInt(_this.scrollbarEl.style.top) || 0;
            _this.dragOffsetY = e.clientY;
        });
        document.addEventListener('mousemove', function (e) {
            return _this.handleDocumentMouseMove(e);
        });
        document.addEventListener('mouseup', function () { return _this.dragStop(); });
        document.addEventListener('mouseleave', function () { return _this.dragStop(); });
    };
    CustomScrollbarVertical.prototype.updateScrollbarEl = function () {
        var _this = this;
        window.requestAnimationFrame(function () {
            if (_this.contentEl.scrollHeight > _this.contentEl.clientHeight) {
                var scrollbarHeight = _this.scrollbarContainerEl.scrollHeight *
                    (_this.contentEl.clientHeight / _this.contentEl.scrollHeight);
                var scrollbarTop = (_this.scrollbarContainerEl.scrollHeight * _this.contentEl.scrollTop) /
                    _this.contentEl.scrollHeight;
                _this.scrollbarEl.style.transform = "translateY(".concat(scrollbarTop, "px)");
                _this.scrollbarEl.style.height = "".concat(scrollbarHeight, "px");
            }
            else {
                _this.scrollbarContainerEl.style.visibility = 'hidden';
            }
        });
    };
    CustomScrollbarVertical.prototype.dragStart = function () {
        this.dragging = true;
        this.scrollbarEl.classList.add('scrollbar-active');
    };
    CustomScrollbarVertical.prototype.dragStop = function () {
        this.dragging = false;
        this.scrollbarEl.classList.remove('scrollbar-active');
    };
    /** for document.addEventListener('mousemove', (e) => handleDrag(e)) */
    CustomScrollbarVertical.prototype.handleDocumentMouseMove = function (e) {
        var _this = this;
        if (this.dragging) {
            window.requestAnimationFrame(function () {
                var clickPosRatio = (_this.dragOffsetY - _this.dragStartY) / _this.scrollbarEl.clientHeight;
                var scrollBarScrollDistance = e.clientY - _this.dragStartY;
                var contentScrollDistance = (scrollBarScrollDistance / _this.scrollbarContainerEl.scrollHeight) *
                    _this.contentEl.scrollHeight;
                var contentScrollTop = _this.dragStartContentScrollTop -
                    clickPosRatio * _this.contentEl.clientHeight +
                    contentScrollDistance;
                _this.scrollContent(
                // 0 <= scrollToWhere <= contentBottom
                Math.max(Math.min(contentScrollTop, _this.contentEl.scrollHeight - _this.contentEl.clientHeight), 0));
            });
        }
    };
    CustomScrollbarVertical.prototype.scrollContent = function (scrollTop, behavior) {
        if (behavior === void 0) { behavior = 'auto'; }
        this.contentEl.scrollTo({
            top: scrollTop,
            // @ts-ignore
            behavior: behavior,
        });
    };
    return CustomScrollbarVertical;
}());
var CustomScrollbarHorizontal = /** @class */ (function (_super) {
    __extends(CustomScrollbarHorizontal, _super);
    function CustomScrollbarHorizontal() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.dragStartX = 0;
        _this.dragOffsetX = 0;
        return _this;
    }
    CustomScrollbarHorizontal.prototype.initDOM = function () {
        this.scrollbarEl = document.createElement('div');
        this.scrollbarEl.classList.add('scrollbar', 'scrollbar-horizontal');
        this.scrollbarContainerEl.appendChild(this.scrollbarEl);
    };
    CustomScrollbarHorizontal.prototype.registerEvents = function () {
        var _this = this;
        // scroll to click pos when clicking the scrollbar track
        this.scrollbarContainerEl.addEventListener('mousedown', function (e) {
            e.preventDefault();
            e.stopPropagation();
            var clickPosScrollTop = (e.clientY - _this.scrollbarEl.clientHeight / 2) /
                _this.scrollbarContainerEl.scrollHeight;
            _this.scrollContent(_this.contentEl.scrollHeight * clickPosScrollTop, 'instant');
        });
        this.contentEl.addEventListener('scroll', function () { return _this.updateScrollbarEl(); });
        // register scrollbarEl.mousedown event, start handling dragging
        this.scrollbarEl.addEventListener('mousedown', function (e) {
            e.preventDefault();
            e.stopPropagation();
            _this.dragStart();
            _this.dragStartContentScrollTop = _this.contentEl.scrollTop;
            _this.dragStartX = parseInt(_this.scrollbarEl.style.top) || 0;
            _this.dragOffsetX = e.clientX;
        });
        document.addEventListener('mousemove', function (e) {
            return _this.handleDocumentMouseMove(e);
        });
        document.addEventListener('mouseup', function () { return _this.dragStop(); });
        document.addEventListener('mouseleave', function () { return _this.dragStop(); });
    };
    CustomScrollbarHorizontal.prototype.updateScrollbarEl = function () {
        var _this = this;
        window.requestAnimationFrame(function () {
            if (_this.contentEl.scrollWidth > _this.contentEl.clientWidth) {
                var scrollbarWidth = _this.scrollbarContainerEl.scrollWidth *
                    (_this.contentEl.clientWidth / _this.contentEl.scrollWidth);
                var scrollbarTop = (_this.scrollbarContainerEl.scrollWidth * _this.contentEl.scrollTop) /
                    _this.contentEl.scrollWidth;
                _this.scrollbarEl.style.transform = "translateY(".concat(scrollbarTop, "px)");
                _this.scrollbarEl.style.height = "".concat(scrollbarWidth, "px");
            }
            else {
                _this.scrollbarContainerEl.style.visibility = 'hidden';
            }
        });
    };
    CustomScrollbarHorizontal.prototype.handleDocumentMouseMove = function (e) {
        var _this = this;
        if (this.dragging) {
            window.requestAnimationFrame(function () {
                var clickPosRatio = (_this.dragOffsetX - _this.dragStartX) / _this.scrollbarEl.clientWidth;
                var scrollBarScrollDistance = e.clientX - _this.dragStartX;
                var contentScrollDistance = (scrollBarScrollDistance / _this.scrollbarContainerEl.scrollWidth) *
                    _this.contentEl.scrollWidth;
                var contentScrollTop = _this.dragStartContentScrollTop -
                    clickPosRatio * _this.contentEl.clientWidth +
                    contentScrollDistance;
                _this.scrollContent(
                // 0 <= scrollToWhere <= contentBottom
                Math.max(Math.min(contentScrollTop, _this.contentEl.scrollWidth - _this.contentEl.clientWidth), 0));
            });
        }
    };
    CustomScrollbarHorizontal.prototype.scrollContent = function (scrollLeft, behavior) {
        if (behavior === void 0) { behavior = 'auto'; }
        this.contentEl.scrollTo({
            left: scrollLeft,
            // @ts-ignore
            behavior: behavior,
        });
    };
    return CustomScrollbarHorizontal;
}(CustomScrollbarVertical));
var CustomScrollbarWrap = /** @class */ (function () {
    function CustomScrollbarWrap(contentEl, options) {
        if (options === void 0) { options = {
            wrapContent: true,
            wrapEl: 'div',
        }; }
        var scrollbarWrapView;
        if (options.wrapContent) {
            scrollbarWrapView = document.createElement(options.wrapEl);
            Array.from(contentEl.children).forEach(function (child) {
                return scrollbarWrapView.appendChild(child);
            });
        }
        else {
            scrollbarWrapView = contentEl;
        }
        scrollbarWrapView.classList.add('scrollbar-wrap');
        var vScrollbarContainer = document.createElement('div');
        vScrollbarContainer.classList.add('scrollbar-container', 'scrollbar-vertical-container');
        var hScrollbarContainer = document.createElement('div');
        hScrollbarContainer.classList.add('scrollbar-container', 'scrollbar-horizontal-container');
        contentEl.appendChild(scrollbarWrapView);
        contentEl.appendChild(vScrollbarContainer);
        contentEl.appendChild(hScrollbarContainer);
        this.vScrollbar = new CustomScrollbarVertical(vScrollbarContainer, scrollbarWrapView);
        this.hScrollbar = new CustomScrollbarHorizontal(hScrollbarContainer, scrollbarWrapView);
    }
    return CustomScrollbarWrap;
}());
