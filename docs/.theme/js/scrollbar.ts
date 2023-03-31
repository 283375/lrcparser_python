class CustomScrollbarVertical {
  scrollbarContainerEl: HTMLElement
  scrollbarEl: HTMLElement
  contentEl: HTMLElement

  protected dragging: boolean = false
  protected dragStartContentScrollTop = 0
  private dragStartY = 0
  private dragOffsetY = 0

  constructor(scrollbarContainerEl: HTMLElement, contentEl: HTMLElement) {
    this.scrollbarContainerEl = scrollbarContainerEl
    this.contentEl = contentEl

    this.initDOM()
    this.registerEvents()
    this.updateScrollbarEl()
  }

  initDOM() {
    this.scrollbarEl = document.createElement('div')
    this.scrollbarEl.classList.add('scrollbar', 'scrollbar-vertical')
    this.scrollbarContainerEl.appendChild(this.scrollbarEl)
  }

  registerEvents() {
    // scroll to click pos when clicking the scrollbar track
    this.scrollbarContainerEl.addEventListener('mousedown', (e) => {
      e.preventDefault()
      e.stopPropagation()

      const clickPosScrollTop =
        (e.clientY - this.scrollbarEl.clientHeight / 2) /
        this.scrollbarContainerEl.scrollHeight

      this.scrollContent(
        this.contentEl.scrollHeight * clickPosScrollTop,
        'instant'
      )
    })

    this.contentEl.addEventListener('scroll', () => this.updateScrollbarEl())

    // register scrollbarEl.mousedown event, start handling dragging
    this.scrollbarEl.addEventListener('mousedown', (e) => {
      e.preventDefault()
      e.stopPropagation()

      this.dragStart()

      this.dragStartContentScrollTop = this.contentEl.scrollTop
      this.dragStartY = parseInt(this.scrollbarEl.style.top) || 0
      this.dragOffsetY = e.clientY
    })

    document.addEventListener('mousemove', (e) =>
      this.handleDocumentMouseMove(e)
    )

    document.addEventListener('mouseup', () => this.dragStop())
    document.addEventListener('mouseleave', () => this.dragStop())
  }

  updateScrollbarEl() {
    window.requestAnimationFrame(() => {
      if (this.contentEl.scrollHeight > this.contentEl.clientHeight) {
        const scrollbarHeight =
          this.scrollbarContainerEl.scrollHeight *
          (this.contentEl.clientHeight / this.contentEl.scrollHeight)
        const scrollbarTop =
          (this.scrollbarContainerEl.scrollHeight * this.contentEl.scrollTop) /
          this.contentEl.scrollHeight

        this.scrollbarEl.style.transform = `translateY(${scrollbarTop}px)`
        this.scrollbarEl.style.height = `${scrollbarHeight}px`
      } else {
        this.scrollbarContainerEl.style.visibility = 'hidden'
      }
    })
  }

  dragStart() {
    this.dragging = true
    this.scrollbarEl.classList.add('scrollbar-active')
  }

  dragStop() {
    this.dragging = false
    this.scrollbarEl.classList.remove('scrollbar-active')
  }

  /** for document.addEventListener('mousemove', (e) => handleDrag(e)) */
  handleDocumentMouseMove(e: MouseEvent) {
    if (this.dragging) {
      window.requestAnimationFrame(() => {
        const clickPosRatio =
          (this.dragOffsetY - this.dragStartY) / this.scrollbarEl.clientHeight

        const scrollBarScrollDistance = e.clientY - this.dragStartY

        const contentScrollDistance =
          (scrollBarScrollDistance / this.scrollbarContainerEl.scrollHeight) *
          this.contentEl.scrollHeight

        const contentScrollTop =
          this.dragStartContentScrollTop -
          clickPosRatio * this.contentEl.clientHeight +
          contentScrollDistance

        this.scrollContent(
          // 0 <= scrollToWhere <= contentBottom
          Math.max(
            Math.min(
              contentScrollTop,
              this.contentEl.scrollHeight - this.contentEl.clientHeight
            ),
            0
          )
        )
      })
    }
  }

  scrollContent(
    scrollTop: number,
    behavior: 'auto' | 'smooth' | 'instant' = 'auto'
  ) {
    this.contentEl.scrollTo({
      top: scrollTop,
      // @ts-ignore
      behavior: behavior,
    })
  }
}

class CustomScrollbarHorizontal extends CustomScrollbarVertical {
  private dragStartX = 0
  private dragOffsetX = 0

  initDOM() {
    this.scrollbarEl = document.createElement('div')
    this.scrollbarEl.classList.add('scrollbar', 'scrollbar-horizontal')
    this.scrollbarContainerEl.appendChild(this.scrollbarEl)
  }

  registerEvents() {
    // scroll to click pos when clicking the scrollbar track
    this.scrollbarContainerEl.addEventListener('mousedown', (e) => {
      e.preventDefault()
      e.stopPropagation()

      const clickPosScrollTop =
        (e.clientY - this.scrollbarEl.clientHeight / 2) /
        this.scrollbarContainerEl.scrollHeight

      this.scrollContent(
        this.contentEl.scrollHeight * clickPosScrollTop,
        'instant'
      )
    })

    this.contentEl.addEventListener('scroll', () => this.updateScrollbarEl())

    // register scrollbarEl.mousedown event, start handling dragging
    this.scrollbarEl.addEventListener('mousedown', (e) => {
      e.preventDefault()
      e.stopPropagation()

      this.dragStart()

      this.dragStartContentScrollTop = this.contentEl.scrollTop
      this.dragStartX = parseInt(this.scrollbarEl.style.top) || 0
      this.dragOffsetX = e.clientX
    })

    document.addEventListener('mousemove', (e) =>
      this.handleDocumentMouseMove(e)
    )

    document.addEventListener('mouseup', () => this.dragStop())
    document.addEventListener('mouseleave', () => this.dragStop())
  }

  updateScrollbarEl() {
    window.requestAnimationFrame(() => {
      if (this.contentEl.scrollWidth > this.contentEl.clientWidth) {
        const scrollbarWidth =
          this.scrollbarContainerEl.scrollWidth *
          (this.contentEl.clientWidth / this.contentEl.scrollWidth)
        const scrollbarTop =
          (this.scrollbarContainerEl.scrollWidth * this.contentEl.scrollTop) /
          this.contentEl.scrollWidth

        this.scrollbarEl.style.transform = `translateY(${scrollbarTop}px)`
        this.scrollbarEl.style.height = `${scrollbarWidth}px`
      } else {
        this.scrollbarContainerEl.style.visibility = 'hidden'
      }
    })
  }

  handleDocumentMouseMove(e: MouseEvent) {
    if (this.dragging) {
      window.requestAnimationFrame(() => {
        const clickPosRatio =
          (this.dragOffsetX - this.dragStartX) / this.scrollbarEl.clientWidth

        const scrollBarScrollDistance = e.clientX - this.dragStartX

        const contentScrollDistance =
          (scrollBarScrollDistance / this.scrollbarContainerEl.scrollWidth) *
          this.contentEl.scrollWidth

        const contentScrollTop =
          this.dragStartContentScrollTop -
          clickPosRatio * this.contentEl.clientWidth +
          contentScrollDistance

        this.scrollContent(
          // 0 <= scrollToWhere <= contentBottom
          Math.max(
            Math.min(
              contentScrollTop,
              this.contentEl.scrollWidth - this.contentEl.clientWidth
            ),
            0
          )
        )
      })
    }
  }

  scrollContent(
    scrollLeft: number,
    behavior: 'auto' | 'smooth' | 'instant' = 'auto'
  ) {
    this.contentEl.scrollTo({
      left: scrollLeft,
      // @ts-ignore
      behavior: behavior,
    })
  }
}

class CustomScrollbarWrap {
  vScrollbar: CustomScrollbarVertical
  hScrollbar: CustomScrollbarHorizontal

  constructor(contentEl: HTMLElement) {
    const scrollbarWrapView = document.createElement('div')
    scrollbarWrapView.classList.add('scrollbar-wrap')

    Array.from(contentEl.children).forEach((child) =>
      scrollbarWrapView.appendChild(child)
    )

    const vScrollbarContainer = document.createElement('div')
    vScrollbarContainer.classList.add(
      'scrollbar-container',
      'scrollbar-vertical-container'
    )
    const hScrollbarContainer = document.createElement('div')
    hScrollbarContainer.classList.add(
      'scrollbar-container',
      'scrollbar-horizontal-container'
    )

    contentEl.appendChild(scrollbarWrapView)
    contentEl.appendChild(vScrollbarContainer)
    contentEl.appendChild(hScrollbarContainer)

    this.vScrollbar = new CustomScrollbarVertical(
      vScrollbarContainer,
      scrollbarWrapView
    )
    this.hScrollbar = new CustomScrollbarHorizontal(
      hScrollbarContainer,
      scrollbarWrapView
    )
  }
}
