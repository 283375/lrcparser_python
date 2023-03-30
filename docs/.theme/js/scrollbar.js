function createScrollbar(container) {
  let scrollbarDragging = false
  let contentStartScrollTop = 0
  let dragStartY = 0
  let dragOffsetY = 0

  const scrollbarWrapView = document.createElement('div')
  scrollbarWrapView.classList.add('scrollbar-wrap')

  for (const child of Array.from(container.children)) {
    scrollbarWrapView.appendChild(child)
  }

  const content = scrollbarWrapView

  const scrollbarContainer = document.createElement('div')
  scrollbarContainer.classList.add('scrollbar-container')
  const scrollbar = document.createElement('div')
  scrollbar.classList.add('scrollbar')

  scrollbarContainer.appendChild(scrollbar)
  container.appendChild(scrollbarWrapView)
  container.appendChild(scrollbarContainer)

  function startScroll() {
    scrollbarDragging = true
    scrollbar.classList.add('scrollbar-active')
  }

  function stopScroll() {
    scrollbarDragging = false
    scrollbar.classList.remove('scrollbar-active')
  }

  function updateScrollbar() {
    window.requestAnimationFrame(() => {
      if (scrollbarContainer.scrollHeight < content.scrollHeight) {
        const scrollbarHeight =
          scrollbarContainer.scrollHeight *
          (content.clientHeight / content.scrollHeight)
        const scrollbarTop =
          (scrollbarContainer.scrollHeight * content.scrollTop) /
          content.scrollHeight

        scrollbar.style.transform = `translateY(${scrollbarTop}px)`
        scrollbar.style.height = `${scrollbarHeight}px`
      }
    })
  }

  function scrollContent(scrollTop, smooth = false) {
    content.scrollTo({
      top: scrollTop,
      behavior: smooth ? 'smooth' : 'instant',
    })
  }

  const contentResizeObserver = new ResizeObserver(updateScrollbar)
  contentResizeObserver.observe(content)

  scrollbarContainer.addEventListener('mousedown', (e) => {
    e.preventDefault()
    e.stopPropagation()

    const clickPosScrollTop =
      (e.clientY - scrollbar.clientHeight / 2) / scrollbarContainer.scrollHeight

    scrollContent(content.scrollHeight * clickPosScrollTop, true)
  })

  content.addEventListener('scroll', updateScrollbar)

  scrollbar.addEventListener('mousedown', (e) => {
    e.preventDefault()
    e.stopPropagation()

    startScroll()

    contentStartScrollTop = content.scrollTop
    dragStartY = parseInt(scrollbar.style.top) || 0
    dragOffsetY = e.clientY
  })

  document.addEventListener('mousemove', (e) => {
    if (scrollbarDragging) {
      window.requestAnimationFrame(() => {
        const clickPosRatio =
          (dragOffsetY - dragStartY) / scrollbar.clientHeight

        const scrollBarScrollDistance = e.clientY - dragStartY

        const contentScrollDistance =
          (scrollBarScrollDistance / scrollbarContainer.scrollHeight) *
          content.scrollHeight

        const contentScrollTop =
          contentStartScrollTop -
          clickPosRatio * content.clientHeight +
          contentScrollDistance

        scrollContent(
          // 0 <= scrollToWhere <= contentBottom
          Math.max(
            Math.min(
              contentScrollTop,
              content.scrollHeight - content.clientHeight
            ),
            0
          )
        )
      })
    }
  })

  document.addEventListener('mouseup', stopScroll)
  document.addEventListener('mouseleave', stopScroll)

  updateScrollbar()
}
